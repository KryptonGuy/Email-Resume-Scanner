import imaplib
from fileops.azureClient import AzureBlobClient
import tempfile
from config import EMAIL, SERVER, PASSWORD
from .convert_attachment import extract_text_from_pdf
from parser.text_parser import parse_text
import json
from logger import getLogger

logger = getLogger(__name__)

logger.error("error")

# Email Client to perform all operation with email server
class EmailClient():

    def __init__(self):
        #self.imap = imaplib.IMAP4_SSL(os.environ['EMAIL_IMAP_DOMAIN'])
        self.imap = imaplib.IMAP4_SSL(SERVER)

    def login(self):
        try:
            #self.imap.login(os.environ['EMAIL_LOGIN'], os.environ['EMAIL_PASSWORD'])
            self.imap.login(EMAIL, PASSWORD)
            logger.info("Successfully logged into email server ")

        except Exception as e:
            logger.critical(f"Failed to Logged into the email server: {e}")
            self.logout()

    def selectFolder(self, folder, readonly=True):
        try:
            self.imap.select(folder, readonly)
            logger.info(f"{folder} folder has been selected.")
        except Exception as e:
            logger.error(f"Unable to select folder. Exception {e}")
            self.logout()

    def logout(self):
        self.imap.close()
        self.imap.logout()
        logger.info("Email Client logged out")
    

    def get_emails_uid_list(self):
        res, data =self.imap.uid('search', None, "ALL")
        if res == "OK":
            decoded_data =data[0].decode()
            uid_list = decoded_data.split()
        else:
            raise Exception("Unable to fetch UIDs")

        return uid_list

    def move_uid_to_processed(self, email_uid, folder="INBOX.processed"):
        logger.info(f"Moving {email_uid} to {folder}")
        return self.imap.uid("MOVE", email_uid, folder)

    def move_uid_to_error(self,email_uid, folder="INBOX.errors"):
        logger.info(f"Moving {email_uid} to {folder}")
        return self.imap.uid("MOVE", email_uid, folder)

    def search_unread(self):
        return self.imap.uid('search', '(UNSEEN)')

    def get_email(self, uid: str):
        logger.info(f"Getting email uid {uid}")
        return self.imap.uid('FETCH', str(uid), '(RFC822)')

    


class Email():

    def __init__(self, uuid, email_message_byte) -> None:
        self.uuid = uuid
        self.email_message_byte = email_message_byte
        subject, From, To = self.process_email_data(email_message_byte)

        self.body = self.get_body(email_message_byte)
        self.subject = subject
        self.From = From
        self.To = To
    
    def process_email_data(self, email_message_byte):

        # Decode email Subject 
        subject = email_message_byte["Subject"]
        if isinstance(subject, bytes):
            subject = subject.decode()

        # decode email FROM
        From = email_message_byte["From"]
        if isinstance(From, bytes):
            From = From.decode()
        
        # decode email TO
        To = email_message_byte["To"]
        if isinstance(To, bytes):
            To = To.decode()
        
        return subject, From, To




    def get_body(self,email_message_byte):


        if email_message_byte.is_multipart():

            for email_part in email_message_byte.walk():

                content_type = email_part.get_content_type()
                content_disposition = str(email_part.get("Content-Disposition"))

                if content_type == "text/plain" and "attachment" not in content_disposition:
                   return email_part.get_payload(decode=True).decode()
        else:
            content_type = email_part.get_content_type()
            content_disposition = str(email_part.get("Content-Disposition"))

            if content_type == "text/plain" and "attachment" not in content_disposition:
                return email_part.get_payload(decode=True).decode()
            else:
                return None


    def process_attachments(self):
        attachments = []
        if self.email_message_byte.is_multipart():

            for email_part in self.email_message_byte.walk():

                content_disposition = str(email_part.get("Content-Disposition"))

                # Get Attachment from message
                if "attachment" in content_disposition:
                    # download attachment
                    filename = email_part.get_filename()
                    print(filename)
                    some = AzureBlobClient()
                    some.write_to_blob(filename, email_part.get_payload(decode=True))
                    temp = tempfile.TemporaryFile(mode='w+b')
                    temp.write(email_part.get_payload(decode=True))
                    print(temp)
                    print(type(temp))
                    attachment_text = extract_text_from_pdf(temp)
                    print(attachment_text)
                    json_text = parse_text(attachment_text)
                    some.write_to_blob(filename, json.dumps(json_text))
                    attachments.append(temp)

            return filename
        else:
            content_disposition = str(email_part.get("Content-Disposition"))
            if "attachment" in content_disposition:
                    # download attachment
                    filename = email_part.get_filename()
                    some = AzureBlobClient()
                    some.write_to_blob(filename, email_part.get_payload(decode=True))
                    temp = tempfile.TemporaryFile(mode='w+b')
                    temp.write(email_part.get_payload(decode=True))
                    return temp

            else:
                return []


                    