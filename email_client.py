# sourced from https://mailtrap.io/blog/python-send-email-gmail/

import base64
from email.mime.text import MIMEText
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from requests import HTTPError

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send"
]
flow = InstalledAppFlow.from_client_secrets_file('secrets.json', SCOPES)
creds = flow.run_local_server(port=0)

service = build('gmail', 'v1', credentials=creds)

def send_email(email):
    """
    :type email: Email
    """
    message = MIMEText(email.body)
    message['to'] = email.to_address
    message['subject'] = email.subject
    formatted_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

    try:
        message = (service.users().messages().send(userId="me", body=formatted_message).execute())
        print(f'sent message to {message} Message Id: {message["id"]}')
    except HTTPError as error:
        print(f'An error occurred: {error}')
        message = None

