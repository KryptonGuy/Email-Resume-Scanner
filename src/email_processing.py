import email
import imaplib
import logging
import re
import nltk
import spacy
from spacy.matcher import Matcher
from pyresparser import ResumeParser
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

logging.basicConfig(filename='email_processing.log', encoding='utf-8', level=logging.INFO)

# Auth Details 
# @ToDo: Get a better way to fetch the details 



# Function to process email string
# TO get -> name, email, number, attachment (if any)

def processBody(body):


    # Get Name
    nlp = spacy.load('en_core_web_sm')

    # initialize matcher with a vocab
    matcher = Matcher(nlp.vocab)

    nlp_text = nlp(body)
    
    # First name and Last name are always Proper Nouns
    pattern = [{'POS': 'PROPN'}, {'POS': 'PROPN'}]
    
    matcher.add('NAME', None, *pattern)
    
    matches = matcher(nlp_text)
    
    for match_id, start, end in matches:
        span = nlp_text[start:end]
        return span.text

    # Get Phone Number

    phone_nums = re.findall(re.compile(r'(?:(?:\+?([1-9]|[0-9][0-9]|[0-9][0-9][0-9])\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([0-9][1-9]|[0-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{4})(?:\s*(?:#|x\.?|ext\.?|extension)\s*(\d+))?'), body)
    
    if phone_nums:
        number = ''.join(phone_nums[0])
        if len(number) > 10:
            number = "+" + number
            

    # Get Email

    emails = re.findall("([^@|\s]+@[^@]+\.[^@|\s]+)", body)
    if emails:
        try:
            email = emails[0].split()[0].strip(';')
        except IndexError:
            pass
    
    # Skills
    
    return email, number

def parse_resume_file(file_path):
    file_path = "resume.pdf"
    data = ResumeParser(file_path).get_extracted_data()

    pass


# Upload data to blob ?? Naming Convention and Structure ??
def upload_to_blob(data, name):
    blob = BlobClient()
    pass

def processEmail(email_message_byte):

    # Decode email Subject 
    subject = email_message_byte["Subject"]
    if isinstance(subject, bytes):
        subject = subject.decode()

    # decode email FROM
    From = email_message_byte["From"]
    if isinstance(From, bytes):
        From = From.decode()
    
    # decode email TO
    to = email_message_byte["To"]
    if isinstance(to, bytes):
        to = to.decode()
    
    # Skip the parsing if email is html message (to work on)
    if email_message_byte.get_content_type()=="text/html":
        raise Exception("Unable to process as email is in HTML")

    # Get Body for the email
    # If email is in multipart
    if email_message_byte.is_multipart():

        for email_part in email_message_byte.walk():

            content_type = email_part.get_content_type()
            content_disposition = str(email_part.get("Content-Disposition"))
            
            # skip if the content type is html
            if content_type=="text/html":
                print("Content Type is HTML for this part")
                continue

            if content_type == "text/plain" and "attachment" not in content_disposition:
                body = email_part.get_payload(decode=True).decode()

            # Get Attachment from message
            elif "attachment" in content_disposition:
                # download attachment
                filename = email_part.get_filename() 

                # Save the file somewhere 
                upload_to_blob(email_part.get_payload(decode=True), filename)

                # ?? Save the file in local working place and then process ??


    else:

        content_type = email_part.get_content_type()

        # If it is only html
        if content_type=="text/html":
            pass

        body = email_message_byte.get_payload(decode=True).decode()
        print(body)
            # Save the attachment 

    # Persist the data
    # print(body)
    # print(subject)
    # print(From)
    # print(to)

    # Persist Data
    


# Auth
client = imaplib.IMAP4_SSL(SERVER)
client.login(EMAIL, PASSWORD)

# mail box selection
client.select("INBOX.test", readonly=True)

# Get the list of uid to be fetched

res, data =client.uid('search', None, "ALL")

if res == "OK":
    decoded_data =data[0].decode()
    uid_list = decoded_data.split()
else:
    raise Exception("Unable to fetch UIDs")

# Fetch each email and add to the list

raw_email_list = []
for email_uid in uid_list[-2:]:
    print([uid_list[-2:]])
    res, data = client.uid("FETCH", email_uid, "(RFC822)")

    if res=="OK":
        raw_email = data[0][1]
        # raw_email_string = raw_email.decode('utf-8')
        email_message_bytes = email.message_from_bytes(raw_email)
        try:
            processEmail(email_message_bytes)
            state,data = client.uid("MOVE", email_uid, "INBOX.processed")

            if state!="OK":
                print("Unable to move email",state)
                state,data = client.uid("MOVE", email_uid, "INBOX.errors")
        except:
            state,data = client.uid("MOVE", email_uid, "INBOX.errors")
            print("Unable to process email",res)
    else:
        # Error Handling (@ToDO)
        state,data = client.uid("MOVE", email_uid, "INBOX.errors")
        print("Unable to fetch email",res)
        continue


# close the email client connection

client.close()
client.logout()

# parse the email data and get attachment



