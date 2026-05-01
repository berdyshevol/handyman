from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SHEETS_SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
SPREADSHEET_ID = "1of5byl45R6uI8I4cN46kU_Vv53g0rfqmlY7QNvUgEdY"

RANGE_NAME = "Sheet1!A1:G10"

def main():
    creds = Credentials.from_service_account_file(
        "service_account.json",
        scopes=SHEETS_SCOPES
    )

    service = build("sheets", "v4", credentials=creds)

    result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME
        ).execute()

    values = result.get("values", [])

    if not values:
        print("No data found.")
        return

    print("\nSUCCESS: Spreadsheet data retrieved\n")
    for row in values:
        print(row)

if __name__ == "__main__":
    main()
