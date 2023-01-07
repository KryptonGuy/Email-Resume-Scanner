import imaplib
import tempfile
from logger import getLogger

# @ToDo change the way to fetch Creds
from config import EMAIL, SERVER, PASSWORD


logger = getLogger(__name__)

# Email Client to perform all operation with email server
class EmailClient():

    def __init__(self):
        self.imap = imaplib.IMAP4_SSL(SERVER)

    def login(self):
        try:
            self.imap.login(EMAIL, PASSWORD)
            logger.info("Successfully logged into the email server ")

        except Exception as e:
            logger.critical(f"Cannot connect to the email server.  \n {e.with_traceback()}")
            self.logout()

    def selectFolder(self, folder, readonly=True):
        try:
            self.imap.select(folder, readonly)
            logger.info(f"{folder} folder has been chosen.")
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
            logger.info(f"Fetching uids. {len(uid_list)} new emails found.")
        else:
            logger.error(f"Unable to search uids. Response: {res}")

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
        subject, From, To = self.get_header_data(email_message_byte)

        self.body = self.get_body(email_message_byte)
        self.subject = subject
        self.From = From
        self.To = To
    
    # To extract subject, From and To from email
    def get_header_data(self, email_message_byte):

        # Decode email Subject 
        subject = email_message_byte["Subject"]
        if isinstance(subject, bytes):
            subject = subject.decode()

        # Decode email FROM
        From = email_message_byte["From"]
        if isinstance(From, bytes):
            From = From.decode()
        
        # Decode email TO
        To = email_message_byte["To"]
        if isinstance(To, bytes):
            To = To.decode()
        
        return subject, From, To



    # Extract body from email
    def get_body(self,email_message_byte):


        if email_message_byte.is_multipart():

            for email_part in email_message_byte.walk():

                content_type = email_part.get_content_type()
                content_disposition = str(email_part.get("Content-Disposition"))

                # Return body if part is plain text
                if content_type == "text/plain" and "attachment" not in content_disposition:
                   return email_part.get_payload(decode=True).decode()
        else:
            content_type = email_part.get_content_type()
            content_disposition = str(email_part.get("Content-Disposition"))

            if content_type == "text/plain" and "attachment" not in content_disposition:
                return email_part.get_payload(decode=True).decode()
            else:
                logger.info("No body found for the email.")
                return ""


    # Returns List of attachemnts (Temporary file) and File name
    def get_attachments(self):

        attachments = []

        if self.email_message_byte.is_multipart():

            for email_part in self.email_message_byte.walk():

                content_disposition = str(email_part.get("Content-Disposition"))

                # Get Attachment from message
                if "attachment" in content_disposition:

                    # Get File name
                    filename = email_part.get_filename()
                    logger.info(f"Attachment with filename {filename} found")

                    # Write attachment to a temporary file
                    tempf = tempfile.TemporaryFile(mode='w+b')
                    tempf.write(email_part.get_payload(decode=True))
                    logger.info(f"Created a temporary file {filename} at {tempf.name}")

                    attachments.append((tempf, filename))

            return attachments
        else:
            content_disposition = str(email_part.get("Content-Disposition"))
            if "attachment" in content_disposition:
                   # Get File name
                    filename = email_part.get_filename()
                    logger.info(f"Attachment with filename {filename} found")

                    # Write attachment to a temporary file
                    tempf = tempfile.NamedTemporaryFile(mode='w+b')
                    tempf.write(email_part.get_payload(decode=True))
                    logger.info(f"Created a temporary file {filename} at {tempf.name}")

                    return [(tempf, filename)]

            else:
                return attachments