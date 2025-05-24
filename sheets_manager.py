import os.path
import logging
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'

def get_sheets_service():
    """Shows basic usage of the Sheets API.
    Handles authentication and returns a service object.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
            logger.info("Loaded credentials from token.json")
        except Exception as e:
            logger.error(f"Error loading token.json: {e}. Will attempt to re-authenticate.")
            creds = None

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                logger.info("Refreshed expired credentials.")
            except Exception as e:
                logger.error(f"Error refreshing credentials: {e}. Will attempt to re-authenticate.")
                creds = None # Force re-authentication
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                logger.error(f"{CREDENTIALS_FILE} not found. Please download it from Google Cloud Console and place it in the project root.")
                logger.error("Refer to README.md for instructions on how to get this file.")
                return None
            try:
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
                # Pass a specific port to run_local_server to avoid issues if default port is in use
                # You can choose any available port, e.g., 8080, 8081 etc.
                # If you often run multiple local servers, consider making the port configurable or trying a few.
                creds = flow.run_local_server(port=0) # port=0 will find an available port
                logger.info("Authentication successful, obtained new credentials.")
            except FileNotFoundError: # This specific exception is good to catch for credentials.json
                logger.error(f"{CREDENTIALS_FILE} not found during authentication flow. Ensure it's in the project root.")
                return None
            except Exception as e:
                logger.error(f"Error during authentication flow: {e}", exc_info=True)
                return None
        # Save the credentials for the next run
        if creds: # Ensure creds exist before trying to save
            try:
                with open(TOKEN_FILE, 'w') as token:
                    token.write(creds.to_json())
                logger.info(f"Saved new credentials to {TOKEN_FILE}")
            except Exception as e:
                logger.error(f"Error saving credentials to {TOKEN_FILE}: {e}", exc_info=True)
                # Even if saving token fails, proceed with current creds for this session
        
    if not creds: # Final check if creds are still None
        logger.error("Failed to obtain valid credentials after all authentication attempts.")
        return None

    try:
        service = build('sheets', 'v4', credentials=creds)
        logger.info("Google Sheets API service created successfully.")
        return service
    except HttpError as err:
        logger.error(f"An API error occurred while building the service: {err}", exc_info=True)
        # Log details from the error object if available
        if hasattr(err, '_get_reason'):
             logger.error(f"Reason: {err._get_reason()}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred while building the service: {e}", exc_info=True)
        return None

def create_spreadsheet(service, title):
    """
    Creates a new Google Spreadsheet.
    :param service: Authenticated Google Sheets API service object.
    :param title: The title for the new spreadsheet.
    :return: The ID of the newly created spreadsheet, or None if creation fails.
    """
    if not service:
        logger.error("Google Sheets service object is not available. Cannot create spreadsheet.")
        return None
    if not title:
        logger.error("Spreadsheet title cannot be empty.")
        return None

    spreadsheet_body = {
        'properties': {
            'title': title
        }
    }
    try:
        spreadsheet = service.spreadsheets().create(body=spreadsheet_body, fields='spreadsheetId').execute()
        spreadsheet_id = spreadsheet.get('spreadsheetId')
        logger.info(f"Spreadsheet created successfully with Title: '{title}' and ID: '{spreadsheet_id}'")
        return spreadsheet_id
    except HttpError as error:
        logger.error(f"An API error occurred while creating the spreadsheet: {error}")
        # Log details from the error object if available
        if hasattr(error, '_get_reason'):
             logger.error(f"Reason: {error._get_reason()}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred while creating the spreadsheet: {e}")
        return None

def write_data_to_sheet(service, spreadsheet_id, sheet_name, data_df):
    """
    Writes a pandas DataFrame to a specific sheet in a Google Spreadsheet.
    Creates the sheet if it doesn't exist. Clears existing data before writing.

    :param service: Authenticated Google Sheets API service object.
    :param spreadsheet_id: ID of the Google Spreadsheet.
    :param sheet_name: Name of the sheet to write to.
    :param data_df: Pandas DataFrame containing the data.
    :return: True if successful, False otherwise.
    """
    if not service:
        logger.error("Google Sheets service object is not available. Cannot write data.")
        return False
    if not spreadsheet_id:
        logger.error("Spreadsheet ID is not provided. Cannot write data.")
        return False
    if not sheet_name:
        logger.error("Sheet name is not provided. Cannot write data.")
        return False
    if data_df is None: # Check if data_df is None explicitly
        logger.error("DataFrame is None. Nothing to write.")
        return False # Or True, if writing nothing is considered a success in some contexts

    try:
        # Check if sheet exists, and get its properties (like sheetId)
        sheet_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        sheets = sheet_metadata.get('sheets', '')
        sheet_exists = False
        target_sheet_id = None # Not strictly needed for clear/write by name, but good for creation
        for sheet in sheets:
            if sheet.get("properties", {}).get("title", "") == sheet_name:
                sheet_exists = True
                target_sheet_id = sheet.get("properties", {}).get("sheetId")
                logger.info(f"Sheet '{sheet_name}' already exists with ID: {target_sheet_id}.")
                break
        
        if not sheet_exists:
            logger.info(f"Sheet '{sheet_name}' does not exist. Creating it...")
            body = {
                'requests': [{
                    'addSheet': {
                        'properties': {
                            'title': sheet_name
                        }
                    }
                }]
            }
            response = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()
            # Retrieve the new sheet's ID if needed, though not strictly necessary for subsequent operations by name
            new_sheet_properties = response.get('replies')[0].get('addSheet').get('properties')
            target_sheet_id = new_sheet_properties.get('sheetId') # Storing for logging
            logger.info(f"Sheet '{sheet_name}' created successfully with ID: {target_sheet_id}.")

        # Clear the sheet before writing new data
        # The range A:Z assumes data won't exceed column Z. For more columns, use a wider range.
        logger.info(f"Clearing existing data from sheet '{sheet_name}' (range A:Z).")
        clear_range = f"'{sheet_name}'!A:Z" # Ensure sheet name is quoted if it contains spaces
        service.spreadsheets().values().clear(
            spreadsheetId=spreadsheet_id,
            range=clear_range
        ).execute()

        # Prepare data for writing: headers + rows
        # Convert DataFrame to list of lists, including headers
        header = data_df.columns.values.tolist()
        values = data_df.values.tolist()
        data_to_write = [header] + values

        body = {
            'values': data_to_write
        }
        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=f"'{sheet_name}'!A1", # Start writing from cell A1
            valueInputOption='USER_ENTERED', # Or 'RAW' if you don't need type conversion
            body=body
        ).execute()
        logger.info(f"{result.get('updatedCells')} cells updated in '{sheet_name}'. Data written successfully.")
        return True

    except HttpError as error:
        logger.error(f"An API error occurred while writing to sheet '{sheet_name}': {error}")
        if hasattr(error, '_get_reason'):
             logger.error(f"Reason: {error._get_reason()}")
        return False
    except Exception as e:
        logger.error(f"An unexpected error occurred while writing to sheet '{sheet_name}': {e}", exc_info=True)
        return False
