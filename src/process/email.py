import imaplib
import tempfile
from config import EMAIL, SERVER, PASSWORD
from logger import getLogger

logger = getLogger(__name__)

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
    
    # @ToDo Logging
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
    
    # To extract subject, from and To from email || Funcation Name change??
    def process_email_data(self, email_message_byte):

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

                # Return body if part is palin text
                if content_type == "text/plain" and "attachment" not in content_disposition:
                   return email_part.get_payload(decode=True).decode()
        else:
            content_type = email_part.get_content_type()
            content_disposition = str(email_part.get("Content-Disposition"))

            if content_type == "text/plain" and "attachment" not in content_disposition:
                return email_part.get_payload(decode=True).decode()
            else:
                return None


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
                    temp = tempfile.TemporaryFile(mode='w+b')
                    temp.write(email_part.get_payload(decode=True))
    
                    attachments.append((temp, filename))

            return attachments
        else:
            content_disposition = str(email_part.get("Content-Disposition"))
            if "attachment" in content_disposition:
                   # Get File name
                    filename = email_part.get_filename()
                    logger.info(f"Attachment with filename {filename} found")

                    # Write attachment to a temporary file
                    temp = tempfile.TemporaryFile(mode='w+b')
                    temp.write(email_part.get_payload(decode=True))

                    return [(temp, filename)]

            else:
                return attachments


                    