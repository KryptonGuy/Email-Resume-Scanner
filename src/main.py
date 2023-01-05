import email
import json
from parser.text_parser import parse_text
from fileops.azureClient import AzureBlobClient
from process.email import EmailClient, Email
from process.convert_attachment import extract_text_from_pdf
import traceback
from logger import getLogger

# logging.basicConfig(filename='email_processing.log', encoding='utf-8', level=logging.INFO)

logger = getLogger(__name__)

logger.critical("This is test")

# Auth
client = EmailClient()
client.login()

# mail box selection
client.seleteFolder("INBOX.test")

# Get the list of uid to be fetched

uid_list = client.get_emails_uid_list()

raw_email_list = []
for email_uid in uid_list[-2:]:
    res, data = client.get_email(email_uid)
    print(email_uid)
    if res=="OK":
        raw_email = data[0][1]
        # raw_email_string = raw_email.decode('utf-8')
        email_message_bytes = email.message_from_bytes(raw_email)
        try:

            print("1")
            email_instance = Email(email_uid,email_message_bytes)
            print("2")

            attachments = email_instance.process_attachments()
            print("3")

            state,data = client.move_uid_to_processed(email_uid)
            print("4")

            body = email_instance.body

            json_s = parse_text(body)
            attach = extract_text_from_pdf(f"files/{attachments}")
            json_2 = parse_text(attach)
            print("5")
            some = AzureBlobClient()
            some.write_to_blob(email_instance.subject, json.dumps(json_s))
            some.write_to_blob(email_instance.From, json.dumps(json_2))


            

            if state!="OK":
                print("Unable to move email",state)
                state,data = client.move_uid_to_error(email_uid)
        except Exception:
            print(traceback.format_exc())
            state,data = client.move_uid_to_error(email_uid)
            print("main Unable to process email",res)
    else:
        # Error Handling (@ToDO)
        state,data = client.move_uid_to_error(email_uid)
        print("Unable to fetch email",res)
        continue


# close the email client connection

client.logout()

# parse the email data and get attachment



