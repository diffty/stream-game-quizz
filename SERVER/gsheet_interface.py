import pickle
import os

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets.readonly',
]


def auth():
    # Auth
    creds = None

    token_path = "SERVER/creds/token.pickle"
    creds_path = "SERVER/creds/credentials.json"

    if not os.path.exists(creds_path):
        raise Exception("<!!> Creds JSON cannot be found in %s" % creds_path)

    if os.path.exists(token_path):
        with open(token_path, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                creds_path, SCOPES
            )

            creds = flow.run_console()
        
        with open(token_path, "wb") as token:
            pickle.dump(creds, token)

    return creds


def get_spreadsheet_service(creds):
    service = build("sheets", "v4", credentials=creds)
    return service.spreadsheets()


def get_sheet_name_by_id(spreadsheet_service, spreadsheet_id: int, sheet_id: int):
    spreadsheet = spreadsheet_service.get(
        spreadsheetId=spreadsheet_id,
    ).execute()
    
    for _sheet in spreadsheet["sheets"]:
        if str(_sheet["properties"]["sheetId"]) == str(sheet_id):
            return _sheet["properties"]["title"]
    else:
        raise Exception("Can't find sheet with id %s" % sheet_id)


def get_info(creds, spreadsheet_id: int, sheet_id: int, cell_range: str):
    spreadsheet_service = get_spreadsheet_service(creds) 

    sheet_name = get_sheet_name_by_id(spreadsheet_service, spreadsheet_id, sheet_id)

    spreadsheet = spreadsheet_service.values().get(
        spreadsheetId=spreadsheet_id,
        range=f"{sheet_name}!{cell_range}"
    ).execute()
    
    return spreadsheet.get("values", [])
