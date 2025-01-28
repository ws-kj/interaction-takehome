from model import Conversation
from pydantic import BaseModel
from datetime import datetime
from email.utils import parsedate_to_datetime
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import pickle
from tkinter.constants import E

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify']

application_status = [
    "Application Submitted",
    "Recent Communication"
    "Interview Scheduled",
    "Accepted",
    "Rejected"
]

is_application_system="You determine whether or not emails are related to job/internship application updates."
parse_system="You extract relevant details from emails containing job/internship application updates."

class Email(BaseModel):
    sender: str
    subject: str
    sent_time: datetime
    body: str

class ApplicationUpdateExtraction(BaseModel):
    company: str
    status: str
    summary: str

class ApplicationUpdate(BaseModel):
    company: str
    status: str
    sent_time: datetime
    summary: str


class EmailProcessor:
    def __init__(self):
        # mainly google oauth flow
        self.creds = None
        # Load cached credentials if they exist
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)

        # If credentials are invalid or don't exist, get new ones
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                flow.redirect_uri = 'http://localhost:8080'
                self.creds = flow.run_local_server(port=8080)

            # Save credentials for future use
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)

        self.service = build('gmail', 'v1', credentials=self.creds)

    def process_new_updates(self, unread_only=False):
        updates = []
        new_messages = self.get_application_emails(unread_only)
        for email in new_messages:
            if self.is_update(email):
                parsed = self.extract_update(email)
                if parsed:
                    updates.append(parsed)
                    #print(parsed)
        return updates

    def get_all_messages(self):
        # get messages from entire inbox (for testing)
        emails = []

        # Get unread messages
        results = self.service.users().messages().list(
            userId='me',
#            labelIds=['UNREAD']
        ).execute()

        return reversed(results.get('messages', []))

    def get_new_messages(self):
        # only get new messages in inbox
        # Get unread messages
        results = self.service.users().messages().list(
            userId='me',
            labelIds=['UNREAD']
        ).execute()

        return reversed(results.get('messages', []))

    def get_application_emails(self, unread_only=False):
        # process emails and extract application updates
        messages = self.get_new_messages() if unread_only else self.get_all_messages()

        emails = []

        # process raw emails
        for message in messages:
            msg = self.service.users().messages().get(
                userId='me',
                id=message['id'],
                format='full'
            ).execute()

            # Parse headers
            headers = msg['payload']['headers']
            sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), '(No Sender)')
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), '(No Subject)')
            date_str = next((h['value'] for h in headers if h['name'].lower() == 'datetime'), None)

            if date_str:
                sent_time = parsedate_to_datetime(date_str)
            else:
                sent_time = datetime.now()

            # Get body
            body = ''
            if 'parts' in msg['payload']:
                for part in msg['payload']['parts']:
                    if part['mimeType'] == 'text/plain':
                        if 'data' in part['body']:
                            body = base64.urlsafe_b64decode(
                                part['body']['data'].encode('ASCII')
                            ).decode('utf-8')
                            break
            elif 'body' in msg['payload']:
                if 'data' in msg['payload']['body']:
                    body = base64.urlsafe_b64decode(
                        msg['payload']['body']['data'].encode('ASCII')
                    ).decode('utf-8')

            email = Email(
                sender=sender,
                subject=subject,
                sent_time=sent_time,
                body=body
            )
            emails.append(email)

            # Mark as read
            self.service.users().messages().modify(
                userId='me',
                id=message['id'],
                body={'removeLabelIds': ['UNREAD']}
            ).execute()

        return emails

    def is_update(self, email: Email):
        is_application_prompt = f"""
        Analyze this email and determine if it's related to a job/internship application.
        Subject: {email.subject}
        From: {email.sender}
        Body: {email.body}

        Return only 'yes' or 'no'.
        """

        is_application = Conversation(system=is_application_system).gen(is_application_prompt).lower().strip()
        return is_application == 'yes'

    def extract_update(self, email: Email):
        parse_prompt = f"""
        Extract job application information from this email:
        Subject: {email.subject}
        From: {email.sender}
        Body: {email.body}

        Return the company name and application status.

        Also extract and summarize salient details such as:
            - Proposed dates for interview
            - Current interview stage
            - Questions from interviewer
            - Changes or updates to the role
            Ex:
                "Interview schedule request for 1/2/24"
                "Company wishes to proceed to technical interview"
                "Company has question about background"

        The status must be one of: {', '.join(application_status)}
        """

        try:
            extracted = Conversation(system=parse_system).gen_structured(ApplicationUpdateExtraction, parse_prompt)
            if extracted is None:
                raise Exception()

            return ApplicationUpdate(
                company=extracted.company,
                status=extracted.status,
                sent_time=email.sent_time,
                summary=extracted.summary
            )

        except Exception as e:
            print(f"Failed to parse application email: {e}")
            return None
