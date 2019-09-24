from __future__ import print_function
import pickle
import os.path
import json
from time import sleep

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets', ]

# The ID and range of a sample spreadsheet.
with open('config.json', 'r') as f:
    config = json.load(f)
SPREADSHEET_ID = config['DEFAULT']['SPREADSHEET_ID']
FRAME_TITLE = "양식"


class Generator:
    def __init__(self):
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('sheets', 'v4', credentials=creds)

    def getSheetInfo(self, sheet_name=""):
        request = self.service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID, ranges=[],
                                                  includeGridData=False)
        response = request.execute()
        sheets = response.get('sheets')
        for sheet in sheets:
            if sheet['properties']['title'] == sheet_name:
                return sheet
        return None

    def generate(self, sheet_name="자동 생성된 시트"):

        requests = []
        requests.append({
            'addSheet': {
                "properties": {
                    "title": sheet_name,
                    "sheetType": 'GRID',
                }
            }
        })

        body = {
            'requests': requests
        }
        response = self.service.spreadsheets().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body=body).execute()
        frame = self.getSheetInfo(FRAME_TITLE)
        requests = []
        requests.append({
            "copyPaste":
                {
                    "source": {
                        "sheetId": frame['properties']['sheetId'],
                        "startRowIndex": 0,
                        "endRowIndex": 20,
                        "startColumnIndex": 0,
                        "endColumnIndex": 100,
                    },
                    "destination": {
                        "sheetId": response['replies'][0]['addSheet']['properties']['sheetId'],
                        "startRowIndex": 0,
                        "endRowIndex": 20,
                        "startColumnIndex": 0,
                        "endColumnIndex": 100
                    },
                    "pasteType": 'PASTE_NORMAL',
                    "pasteOrientation": 'NORMAL'
                }
        })

        requests.append({
            "setBasicFilter": {
                "filter": {
                    "range":
                        {
                            "sheetId": response['replies'][0]['addSheet']['properties']['sheetId'],
                            "startRowIndex": 0,
                            "endRowIndex": 1000,
                            "startColumnIndex": 0,
                            "endColumnIndex": 11
                        },
                }
            }
        }
        )
        body = {
            'requests': requests
        }
        response = self.service.spreadsheets().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body=body).execute()

    def addRow(self, sheet_name, values):
        body = {
            'values': values
        }
        result = self.service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID, range=sheet_name + "!A2", body=body,
            valueInputOption='USER_ENTERED').execute()
        print('{0} cells updated.'.format(result.get('updatedCells')))


if __name__ == '__main__':
    generator = Generator()
    generator.generate('실행')
    generator.addRow('완료', [['테스트', '테스트2'], ['테스트', '테스트2', 'ㅅ']])
