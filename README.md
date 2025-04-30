# Python---Gmail-Sorter-Using-Gmail-API-v0.5
This program was designed to auto-label my Gmail account for emails regarding university admissions, and can be repurposed for any need. It uses Google's Gmail API and its associated Cloud Console credentials to authenticate access to Gmail, fetch emails, and apply designated labels based on keyword filters. OAuth 2.0 is used for secure authorization. The program supports full inbox scanning with pagination and processes both email snippets and MIME-formatted bodies for greater accuracy when classifying.

Currently, the user must import their own credentials from the Google Cloud Console into the same directory as the Python script to operate the function (see instructions below).

PROJECT STILL IN DEVELOPMENT

Next Steps:
1. The program does not achieve 100% accuracy; I am working on addressing issues related to a lack of classification.

2. I plan to implement a different methodology for auto-labeling, as the current version is not very accessible or user-friendly.

3. I intend to create a user interface so that users do not need to manually modify keyword filters in the code.


Instructions for Cloud Console credentials:
1. Go to the Google Cloud Console (https://console.cloud.google.com/).
   
2. Create a new project (or select an existing one).

3. Enable the Gmail API under APIs & Services > Library.

4. Go to APIs & Services > Credentials, click "Create Credentials" > OAuth client ID.

5. Choose Desktop App, then download the generated credentials.json file.

6. Place credentials.json in the same directory as the Python script/"Gmail Filter Base Code.py".

7. On first run, a browser window will prompt you to log in and authorize access.

8. After authorization, a token file (token.json or token.pickle) will be created for future access.

