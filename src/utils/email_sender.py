import os.path
import base64
from email.message import EmailMessage
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def get_credentials():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def send_email(subject, body, to_email, from_email='ducanh2002add@gmail.com', is_html=False):
    """
    Send an email using Gmail API.

    Args:
        subject (str): Email subject.
        body (str): Email body.
        to_email (str): Recipient email.
        from_email (str): Sender email.
        is_html (bool): Whether the body is HTML.
    """
    creds = get_credentials()
    try:
        service = build('gmail', 'v1', credentials=creds)

        message = EmailMessage()
        if is_html:
            message.set_content("Vui lòng sử dụng trình xem email hỗ trợ HTML để xem nội dung này.")
            message.add_alternative(body, subtype='html')
        else:
            message.set_content(body)
            
        message['To'] = to_email
        message['From'] = from_email
        message['Subject'] = subject

        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {'raw': encoded_message}

        send_message = service.users().messages().send(userId="me", body=create_message).execute()
        print(f'✅ Email sent successfully! Message Id: {send_message["id"]}')

    except HttpError as error:
        print(f'❌ Error sending email: {error}')