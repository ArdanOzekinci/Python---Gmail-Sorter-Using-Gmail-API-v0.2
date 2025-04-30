import os.path
import pickle

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly",
          "https://www.googleapis.com/auth/gmail.modify"
          ]

flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)

creds = flow.run_local_server(port=0)


#Build the Gmail Service After authentication, use the credentials (creds) to build the Gmail API service
service = build('gmail', 'v1', credentials=creds)




with open('token.pickle', 'wb') as token:
    pickle.dump(creds, token)

def authenticate_gmail():
    creds = None
    # Use previously saved credentials if available
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=8080) 
        # Save the credentials for future use
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def get_gmail_service():
    creds = authenticate_gmail()
    service = build('gmail', 'v1', credentials=creds)
    return service

#Stores data of fetched emails
email_data=[]

University_Filters={
    "McMaster": {"keywords": ["McMaster", "thinkeng@mcmaster.ca","macadmit@mcmaster.ca"]},
    "Waterloo": {"keywords": ["Waterloo", "Waterloo", "myapplication@uwaterloo.ca","no-reply@uwaterloo.ca", "safa@uwaterloo.ca", "askus@uwaterloo.ca"]},
    "Guelph": {"keywords": ["Guelph", "admission@uoguelph.ca"]},
    "Ottawa": {"keywords": ["Ottawa", "admissions@uottawa.ca","liaison@uottawa.ca"]},
    "Queen's": {"keywords": ["Queen", "admission@queensu.ca","entrance@queensu.ca"]},
    "York": {"keywords": ["York", "Lassonde", "info@yorku.ca", "ask@lassondeschool.com","welcome@uwo.ca","welcome@e.uwo.ca"]},
    "Ouac": {"keywords": ["Ouac","ouac", "undergrad_support@ouac.on.ca","no-reply@bambora.com","101_support@ouac.on.ca", "OUAC-team@ouac.on.ca","ouevents@ouac.on.ca", ]},
    "Western": {"keywords": ["Western", "apply@university.edu"]},
    "University Of Toronto": {"keywords": ["University Of Toronto","UofT","U of T", "engineering@utoronto.ca","noreply@utoronto.ca"]},
    "Scholarships": {"keywords": ["scholarship","Scholarship","scholarships","Scholarships","Financial Aid", "financial aid","Financial aid"]}
}

def fetch_emails(option):
    try:
        creds = authenticate_gmail()
        service = build('gmail', 'v1', credentials=creds)

        # Fetch email metadata
        if option == "all":
            print("Fetching all emails...")
            results = service.users().messages().list(userId='me').execute()
        else:
            print(f"Fetching {option} emails...")
            results = service.users().messages().list(userId='me', maxResults=option).execute()

        # Initialize a list to hold the emails
        all_messages = []
        
        # Loop through results
        while 'messages' in results:
            messages = results['messages']
            all_messages.extend(messages)

            # Check if there's a nextPageToken to continue fetching
            if 'nextPageToken' in results:
                results = service.users().messages().list(userId='me', pageToken=results['nextPageToken']).execute()
            else:
                break  # No more pages, exit the loop

        print(f"Total messages fetched: {len(all_messages)}")

        # Fetch details for each message and store them
        email_data = []
        for message in all_messages:
            msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()

            body = ""
            # Extract all parts of the email
            for part in msg.get('payload', {}).get('parts', []):
                mime_type = part.get('mimeType')
                body_data = part.get('body', {}).get('data', '')

                # Check if part is text (either plain or html)
                if mime_type == 'text/plain' or mime_type == 'text/html':
                    body += body_data if body_data else ''

            email_data.append({
                'id': msg['id'],
                'snippet': msg.get('snippet', 'No snippet available'),
                'body': body  # Store the full body text
            })

            print(f"Message ID: {msg['id']}")
            print(f"Snippet: {msg.get('snippet', 'No snippet available')}")
            print(f"Body: {body[:100]}...")  # Print the first 100 characters of the body for debugging
            print("-" * 50)

        return email_data

    except HttpError as error:
        print(f"An error occurred: {error}")
        return []
    
def get_existing_labels(service):
    """Fetch existing labels and return a dictionary of {label_name: label_id}."""
    existing_labels = service.users().labels().list(userId="me").execute().get("labels", [])
    label_map = {label["name"]: label["id"] for label in existing_labels}
    return label_map

def create_labels_from_filters(service, filters):
    label_map = get_existing_labels(service)  # Get all existing labels

    for label_name in filters.keys():  # Loop through filter keys like 'McMaster', 'Guelph', etc.
        if label_name not in label_map:  # Only create the label if it doesn't already exist
            print(f"Creating label: {label_name}")
            label_body = {
                "name": label_name,  # Use the filter key as the label name
                "labelListVisibility": "labelShow",
                "messageListVisibility": "show",
            }
            new_label = service.users().labels().create(userId="me", body=label_body).execute()
            label_map[label_name] = new_label["id"]
            print(f"Label '{label_name}' created with ID: {new_label['id']}")
        else:
            print(f"Label '{label_name}' already exists with ID: {label_map[label_name]}")

    return label_map

def apply_labels(service, emails, label_map, filters):
    """Apply labels to emails based on filters."""
    for email in emails:
        email_id = email["id"]
        email_snippet = email["snippet"]

        for label, params in filters.items():
            if any(keyword.lower() in email_snippet.lower() for keyword in params["keywords"]):
                label_id = label_map.get(label)
                if label_id:
                    print(f"Applying label '{label}' to email ID {email_id}")
                    service.users().messages().modify(
                        userId='me',
                        id=email_id,
                        body={'addLabelIds': [label_id]}
                    ).execute()

# Main script
if __name__ == "__main__":
    try:
        creds = authenticate_gmail()
        service = build("gmail", "v1", credentials=creds)

        # Create labels from filters without duplicates
        label_map = create_labels_from_filters(service, University_Filters)

        # Fetch emails and apply labels
        user_input = input("Enter the number of emails to fetch (or type 'all' to process all emails): ").strip().lower()
        if user_input == "all":
            emails = fetch_emails("all")
        else:
            x = int(user_input)
            if x <= 0:
                raise ValueError("Number of emails must be positive.")
            emails = fetch_emails(x)

        apply_labels(service, emails, label_map, University_Filters)
        print("Labeling complete.")
    except ValueError as e:
        print(f"Invalid input: {e}")
    except HttpError as error:
        print(f"An API error occurred: {error}")

