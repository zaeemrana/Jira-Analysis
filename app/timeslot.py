from __future__ import print_function
from typing import List
import attr

import pickle, sys
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import datetime
# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

@attr.s(auto_attribs=True, slots=True)
class Timeslot:
    time: str
    filled: List[bool]

all_timeslots = [
    "9:00AM - 10:00AM",
    "10:00AM - 11:00AM",
    "11:00AM - 12:00PM",
    "1:00PM - 2:00PM",
    "2:00PM - 3:00PM",
    "3:00PM - 4:00PM",
    "4:00PM - 5:00PM",
    "6:00PM - 7:00PM",
    "7:00PM - 8:00PM",
    "8:00PM - 9:00PM",
]

SPREADSHEET_ID = '1swswJZ2WwGTsacl0X_hQzqC36mbRbcHSwpn41jg64_c'
def getSpreadSheet():

    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('/config/token.pickle'):
        with open('/config/token.pickle', 'rb') as token:
            creds = pickle.load(token)
    elif os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets().values()
    return sheet


def get_all_timeslots():
    return list(Timeslot(time, [False, False, False]) for time in all_timeslots)

def getSchedule():
    sheet = getSpreadSheet()

    RANGE_NAME = 'Cal!A2:O11'
    result = sheet.get(spreadsheetId= SPREADSHEET_ID, range = RANGE_NAME).execute()
    values = result.get('values', [])

    HEADER_RANGE = 'Cal!B1:N1'
    result2 = sheet.get(spreadsheetId= SPREADSHEET_ID, range = HEADER_RANGE).execute()
    values2 = result2.get('values', [])

    return [row[1:-1] for row in values], values2