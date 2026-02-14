import gspread
from oauth2client.service_account import ServiceAccountCredentials


class SheetsService:

    def __init__(self, creds_file="service_account.json"):
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            creds_file, scope
        )
        self.client = gspread.authorize(creds)

    def export_leads(self, sheet_name: str, leads):

        sheet = self.client.open(sheet_name).sheet1

        for lead in leads:
            sheet.append_row([
                lead.company,
                lead.role,
                lead.location,
                lead.email,
                lead.state
            ])
