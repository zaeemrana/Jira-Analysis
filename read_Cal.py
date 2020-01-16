"""
Read Calendar and keep it up to date
"""

from __future__ import print_function
import pickle, sys
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import datetime
# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

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

def updateCal(timeslots, netid, name):
    RANGE_NAME =  'Cal!A2:O11'
    timeslots = [(x.split(" ")[0], x.split(" ")[1]) for x in timeslots]

    sheet = getSpreadSheet()
    result = sheet.get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    values = result.get('values', [])
    values = [row[1:-1] for row in values]
    values = [ row[:6]+row[7:] for row in values]
    row = {
            "11":0,
            "12":1,
            "13":2,
            "21":3,
            "22":4,
            "23":5,
            "24":6,
            "31":7,
            "32":8,
            "33":9,
            "111":0,
            "112":1,
            "113":2,
            "121":3,
            "122":4,
            "123":5,
            "124":6,
            "131":7,
            "132":8,
            "133":9
        }
    ind_to_col = ["B","C","D","E","F","G","I","J","K","L","M","N"]
    col = {
        "Monday":0,
        "Tuesday":1,
        "Wednesday":2,
        "Thursday": 3,
        "Friday": 4,
        "Saturday": 5,
        "Monday1":6,
        "Tuesday1":7,
        "Wednesday1":8,
        "Thursday1": 9,
        "Friday1": 10,
        "Saturday1": 11
    }

    cells = [(col[day], row[time]) for day,time in timeslots]
    current_cells = [values[j][i] for i,j in cells]

    edit_cells = []
    for i,x in enumerate(cells):
        curr_cell = current_cells[i]

        if netid in curr_cell:
            edit_cells.append((x,True))
        else:
            edit_cells.append((x,False))

    def removeID(str,netid):
        return str.replace(netid, "").strip()
    def addID(str,id):
        return (str + " " + netid).strip()

    finalVals = []
    for i,x in enumerate(edit_cells):
        isRemove = x[1]

        if isRemove:
            finalVals.append((x[0],removeID(current_cells[i],netid)))
        else:
            finalVals.append((x[0], addID(current_cells[i], netid) ))

    for x in finalVals:
        newCellVal = {'values': [[x[1]]] ,'majorDimension' : 'COLUMNS' }
        sheetRow = x[0][1]+2
        sheetCol = ind_to_col[ x[0][0] ]

        curr_range = "Cal!" + str(sheetCol) + str(sheetRow)

        request = sheet.update(spreadsheetId=SPREADSHEET_ID,
                     range= curr_range,
                     valueInputOption = 'RAW',
                     body = newCellVal
                )
        response = request.execute()

"""
Adds a log row in the google sheet "Logs" for each entry selected
"""
def logCalRow(timeslots, netid, name):
    RANGE_NAME =  'Logs'

    sheet = getSpreadSheet()
    timeslots = [(x.split(" ")[0], x.split(" ")[1]) for x in timeslots]

    today = datetime.date.today()
    idx = (today.weekday() + 1) % 7
    sun = today - datetime.timedelta(idx)
    value_range_body = []

    for day, timeslot in timeslots:
        row = [datetime.datetime.now().strftime("%m/%d/%y-%H:%M:%S"),
                            netid,
                            name,
                            day,
                            timeslot,
                            sun.strftime("%m/%d/%Y")
                            ]
        value_range_body.append(row)

    value_range_body = {'values': value_range_body}
    request = sheet.append(spreadsheetId=SPREADSHEET_ID,
                            range = RANGE_NAME,
                            valueInputOption = 'RAW',
                            body = value_range_body)
    response = request.execute()
