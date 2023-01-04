import imaplib
import os
from fileops.azureClient import AzureBlobClient
import tempfile
from config import EMAIL, SERVER, PASSWORD

class EmailClient():
    def __init__(self):
        #self.imap = imaplib.IMAP4_SSL(os.environ['EMAIL_IMAP_DOMAIN'])
        self.imap = imaplib.IMAP4_SSL(SERVER)

    def login(self):
        #self.imap.login(os.environ['EMAIL_LOGIN'], os.environ['EMAIL_PASSWORD'])
        self.imap.login(EMAIL, PASSWORD)

    def seleteFolder(self, folder, readonly=True):
        self.imap.select(folder, readonly)

    def logout(self):
        self.imap.close()
        self.imap.logout()    

    def get_emails_uid_list(self):
        res, data =self.imap.uid('search', None, "ALL")
        if res == "OK":
            decoded_data =data[0].decode()
            uid_list = decoded_data.split()
        else:
            raise Exception("Unable to fetch UIDs")

        return uid_list

    def move_uid_to_processed(self, email_uid, folder="INBOX.processed"):
        return self.imap.uid("MOVE", email_uid, folder)

        if state!="OK":
            print("Unable to move email",state)
            self.move_uid_to_error(email_uid)
    
    def move_uid_to_error(self,email_uid, folder="INBOX.errors"):
        return self.imap.uid("MOVE", email_uid, folder)

    def search_unread(self):
        return self.imap.uid('search', '(UNSEEN)')

    def get_email(self, uid: str):
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
                    #AzureBlobClient.write_to_blob(filename, email_part.get_payload(decode=True))
                    temp = tempfile.TemporaryFile(mode='w+b')
                    temp.write(email_part.get_payload(decode=True))
                    attachments.append(temp)

            return attachments
        else:
            content_disposition = str(email_part.get("Content-Disposition"))
            if "attachment" in content_disposition:
                    # download attachment
                    filename = email_part.get_filename()
                    #AzureBlobClient.write_to_blob(filename, email_part.get_payload(decode=True))
                    temp = tempfile.TemporaryFile(mode='w+b')
                    temp.write(email_part.get_payload(decode=True))
                    return temp

            else:
                return []


                    