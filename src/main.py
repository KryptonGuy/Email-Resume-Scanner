import email
import logging

from process.email import EmailClient, Email

logging.basicConfig(filename='email_processing.log', encoding='utf-8', level=logging.INFO)

# Auth
client = EmailClient()
client.login()

# mail box selection
client.seleteFolder("INBOX.test")

# Get the list of uid to be fetched

uid_list = client.get_emails_uid_list()

raw_email_list = []
for email_uid in uid_list[-2:]:
    print([uid_list[-2:]])
    res, data = client.get_email(email_uid)

    if res=="OK":
        raw_email = data[0][1]
        # raw_email_string = raw_email.decode('utf-8')
        email_message_bytes = email.message_from_bytes(raw_email)
        try:
            Email(email_uid,email_message_bytes)
            state,data = client.move_uid_to_processed(email_uid)

            if state!="OK":
                print("Unable to move email",state)
                state,data = client.move_uid_to_error(email_uid)
        except:
            state,data = client.move_uid_to_error(email_uid)
            print("Unable to process email",res)
    else:
        # Error Handling (@ToDO)
        state,data = client.move_uid_to_error(email_uid)
        print("Unable to fetch email",res)
        continue


# close the email client connection

client.logout()

# parse the email data and get attachment



