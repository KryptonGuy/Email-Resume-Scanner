import email
import json
from parser.text_parser import TextParser
from fileops.azureClient import AzureBlobClient
from process.email import EmailClient, Email
from process.convert_attachment import extract_text_from_file
import traceback
from logger import getLogger

def add_body_resume_data(bodyJson, resumeJson):

    if not bodyJson["Name"]:
        if resumeJson["Name"]:
            bodyJson["Name"] = resumeJson["Name"]

    if not bodyJson["Email"]:
        if resumeJson["Email"]:
            bodyJson["Email"] = resumeJson["Email"]

    if not bodyJson["PhNum"]:
        if resumeJson["PhNum"]:
            bodyJson["PhNum"] = resumeJson["PhNum"]

    if not bodyJson["Locations"]:
        if resumeJson["Locations"]:
            bodyJson["Locations"] = resumeJson["Locations"]
    
    bodyJson["Skills"].extend(resumeJson["Skills"])

    return bodyJson
    

    
logger = getLogger(__name__)


# Auth
client = EmailClient()
client.login()

azure = AzureBlobClient()

# mail box selection
client.selectFolder("INBOX.test")

# Get the list of uid to be fetched

uid_list = client.get_emails_uid_list()

for email_uid in uid_list[-2:]:

    res, data = client.get_email(email_uid)
    logger.info(f"Response to get {email_uid} email uid {res}")

    metadata = dict()

    if res=="OK":

        raw_email = data[0][1]
        # raw_email_string = raw_email.decode('utf-8')
        email_message_bytes = email.message_from_bytes(raw_email)

        try:

            email_instance = Email(email_uid,email_message_bytes)

            # Save email data to object
            metadata['Subject'] = email_instance.subject
            metadata['From'] = email_instance.From
            metadata['To'] = email_instance.To


            body = email_instance.body

            bodyparser = TextParser(body)
            parseData= bodyparser.get_parsed_json()

            # azure.save_on_local(f"{email_uid}_body_parsed.json", json.dumps(parseData))

            attachments = email_instance.get_attachments()

            for attachment in attachments:
                fileobj, filename = attachment

                # Reset pointer before read
                fileobj.seek(0)

                # @ToDo Save it on azure blob
                azure.save_on_local(filename, fileobj.read())

                # Extract text from the file
                text_from_file = extract_text_from_file(fileobj, filename)

                # Parse Resume for details
                text_parser = TextParser(text_from_file)
                attach_parse_data = text_parser.get_parsed_json()

                parseData = add_body_resume_data(parseData, attach_parse_data)

                # Temp
                # azure.save_on_local(f"{filename}_parsed.json", json.dumps(attach_parse_data))



            state,data = client.move_uid_to_processed(email_uid)
            if state!="OK":
                print("Unable to move email",state)
                state,data = client.move_uid_to_error(email_uid)


        except Exception:
            print(traceback.format_exc())
            state,data = client.move_uid_to_error(email_uid)
            print("main Unable to process email",res)

        metadata["ParseData"] = parseData
        
        # Save MetaData for email
        azure.save_on_local(f"{parseData['Name']}_metadata.json", json.dumps(metadata))

    else:
        # Error Handling (@ToDO)
        state,data = client.move_uid_to_error(email_uid)
        print("Unable to fetch email",res)
        continue
    

    

client.logout()