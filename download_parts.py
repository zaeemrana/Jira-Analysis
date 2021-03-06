from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.http import MediaIoBaseDownload
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def main(driveID,name):
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    # if os.path.exists('/config/tokenDrive.pickle'):
    #     with open('/config/tokenDrive.pickle', 'rb') as token:
    #         creds = pickle.load(token)
    if os.path.exists('tokenDrive.pickle'):
        with open('tokenDrive.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentialsDrive.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('tokenDrive.pickle', 'wb') as token:
            pickle.dump(creds, token)

    drive = build('drive', 'v3', credentials=creds)

    # Call the Drive v3 API
    #results = drive.files().list(pageSize=10, fields="nextPageToken, files(id, name)").execute()
    results = drive.files().get_media(fileId = driveID)

    with open('./AddParts/'+name, 'wb') as fh:
        downloader = MediaIoBaseDownload(fh, results)
        done = False
        while done is False:
            status, done = downloader.next_chunk()


if __name__ == '__main__':
    main("","")
