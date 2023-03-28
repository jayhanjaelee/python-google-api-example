from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from dotenv import load_dotenv

import os
import mimetypes

load_dotenv()


class GoogleAPI:
    def __init__(self):
        self.credentials = service_account.Credentials.from_service_account_file(
            "credentials.json"
        )
        self.service = build("drive", "v3", credentials=self.credentials)


class GoogleDrive(GoogleAPI):
    def __init__(self):
        super().__init__()
        self.folder_id = os.getenv("FOLDER_ID")

    def get_files(self):
        results = (
            self.service.files()
            .list(
                q=f"'{self.folder_id}' in parents",
                fields="nextPageToken, files(id, name)",
            )
            .execute()
        )
        items = results.get("files", [])
        if not items:
            print("No Items Found.")
            return None

        for item in items:
            print(f'{item["name"]} ({item["id"]})')
        return items

    def upload_file(self, file_name, file_path, mimetype):
        file_metadata = {'name': file_name, 'parents': [self.folder_id]}
        media = MediaFileUpload(file_path, mimetype=mimetype)

        file = (
            self.service.files()
            .create(body=file_metadata, media_body=media, fields='id')
            .execute()
        )

        print(f'File ID: {file.get("id")} is Uploaded.')
        return file.get('id')


class GoogleSheets(GoogleAPI):
    def __init__(self):
        super().__init__()
        self.sheets_id = os.getenv("SHEETS_ID")

    def update_values(self, range_name, values, value_input_option):
        try:
            service = build('sheets', 'v4', credentials=self.credentials)
            body = {'values': values}
            result = (
                service.spreadsheets()
                .values()
                .update(
                    spreadsheetId=self.sheets_id,
                    range=range_name,
                    valueInputOption=value_input_option,
                    body=body,
                )
                .execute()
            )
            print(f"{result.get('updatedCells')} cells updated.")
            return result
        except HttpError as error:
            print(f"An error occurred: {error}")
            return error


def main():
    # google_drive
    google_drive = GoogleDrive()

    FILE_DIRECTORY = "sample"

    ## Upload files
    with os.scandir(FILE_DIRECTORY) as files:
        for file in files:
            file_path = os.path.join(os.getcwd(), FILE_DIRECTORY, file.name)
            mimetype = mimetypes.guess_type(file_path)[0]
            google_drive.upload_file(file.name, file_path, mimetype)

    ## List files
    google_drive.get_files()

    # google_sheets
    google_sheet = GoogleSheets()
    sheets_values = [["1", "2", "3"]]
    google_sheet.update_values("A1", sheets_values, "USER_ENTERED")

    return


if __name__ == "__main__":
    main()
