import os
import logging
import io # Ensure io is imported for df.info logging

# Force DEBUG level logging configuration
# Using a more detailed format for better debugging
# Using mode='w' for app.log to overwrite on each run for cleaner debugging sessions
# force=True requires Python 3.8+
logging.basicConfig(
    level=logging.INFO, # Default level changed to INFO
    format='%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - Line %(lineno)d - %(message)s',
    handlers=[
        logging.FileHandler('app.log', mode='w'),
        logging.StreamHandler()
    ],
    force=True 
)

# Get the logger for the main module *after* basicConfig
logger = logging.getLogger(__name__)

# Test log right after basicConfig to ensure it's working
logger.debug("DEBUG logging explicitly configured in main.py using basicConfig with force=True.") # This will not show if level is INFO

# Set higher logging levels for verbose libraries to reduce noise at INFO level
logging.getLogger('googleapiclient.discovery').setLevel(logging.WARNING)
logging.getLogger('google_auth_oauthlib').setLevel(logging.WARNING)
logging.getLogger('requests_oauthlib').setLevel(logging.WARNING)
logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING) # Often verbose via requests
logger.info("Logging levels for verbose libraries set to WARNING.")

# Now import other project modules (so they inherit the root logger config if they use logging.getLogger(__name__))
import pandas as pd
from pdf_extractor import extract_text_from_pdf
from excel_extractor import extract_data_from_excel
from sheets_manager import get_sheets_service, create_spreadsheet, write_data_to_sheet
from financial_ratios import (
    calculate_ebitda, calculate_ebit, calculate_roi, 
    calculate_roe, calculate_roa, calculate_personnel_costs_impact,
    calculate_contribution_margin
)

def get_files_from_bilanci_folder():
    """
    Scans the 'bilanci/' directory and returns a list of full file paths.
    """
    bilanci_folder = "bilanci"
    if not os.path.exists(bilanci_folder):
        logger.error(f"The folder '{bilanci_folder}' does not exist.")
        return []
    if not os.path.isdir(bilanci_folder):
        logger.error(f"'{bilanci_folder}' is not a directory.")
        return []

    file_paths = []
    for filename in os.listdir(bilanci_folder):
        full_path = os.path.join(bilanci_folder, filename)
        if os.path.isfile(full_path): # Ensure it's a file, not a subdirectory
            file_paths.append(full_path)
    return file_paths

if __name__ == "__main__":
    logger.info("Starting main application flow...")

    files_to_process = get_files_from_bilanci_folder() # Re-activate real file processing

    if not files_to_process:
        logger.info("No files found in the 'bilanci' folder to process.")
    else:
        logger.info(f"Found {len(files_to_process)} files to process: {files_to_process}")

        logger.info("Attempting to authenticate with Google Sheets API...")
        service = get_sheets_service()

        if not service:
            logger.critical("Failed to authenticate with Google Sheets API. Service object is None.")
            logger.critical("Please ensure 'credentials.json' is present in the root directory and is configured correctly.")
            logger.critical("Check 'app.log' for more detailed error messages from the authentication process.")
            logger.critical("Exiting application.")
            exit()
        
        logger.info("Successfully authenticated with Google Sheets API.")
        
        spreadsheet_title = "Bilanci Aziendali Analysis" # Restored title
        logger.info(f"Attempting to create or get spreadsheet: '{spreadsheet_title}'")
        spreadsheet_id = create_spreadsheet(service, spreadsheet_title)

        if not spreadsheet_id:
            logger.critical(f"Failed to create or access spreadsheet '{spreadsheet_title}'. Spreadsheet ID is None.")
            logger.critical("Check 'app.log' for more detailed error messages from the spreadsheet creation process.")
            logger.critical("Exiting application.")
            exit()
            
        logger.info(f"Successfully obtained spreadsheet ID: {spreadsheet_id} for title: '{spreadsheet_title}'")

        # Re-activate the original file processing loop and final_df creation
        all_extracted_rows = []
        files_processed_count = 0

        for file_path in files_to_process:
            logger.info(f"Processing file: {file_path}")
            file_name = os.path.basename(file_path)
            _, file_extension = os.path.splitext(file_path)
            file_extension = file_extension.lower()
            current_timestamp = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')

            try:
                if file_extension == ".pdf":
                    extracted_text = extract_text_from_pdf(file_path)
                    if extracted_text:
                        row = {
                            'Company Name': file_name.replace('.pdf', '').replace('.PDF', ''),
                            'Source File': file_name,
                            'Report Year/Period': 'N/A', 
                            'Financial Statement Section': 'N/A', 
                            'Data Point Name': 'Raw Full Text ( первых 1000 символов )', 
                            'Data Point Value': extracted_text[:1000],
                            'Extraction Date': current_timestamp
                        }
                        all_extracted_rows.append(row)
                        logger.info(f"Successfully processed (raw text) from PDF: {file_name}")
                    else:
                        logger.warning(f"Could not extract text from PDF: {file_name} (extractor returned None or empty).")
                
                elif file_extension in [".xlsx", ".xls"]:
                    extracted_excel_data_dict = extract_data_from_excel(file_path)
                    if extracted_excel_data_dict and isinstance(extracted_excel_data_dict, dict) and extracted_excel_data_dict:
                        first_sheet_name = list(extracted_excel_data_dict.keys())[0]
                        df_excel = extracted_excel_data_dict[first_sheet_name]
                        
                        if isinstance(df_excel, pd.DataFrame):
                            excel_preview = df_excel.head(5).iloc[:, :3].to_string()
                            row = {
                                'Company Name': file_name.replace('.xlsx', '').replace('.xls', '').replace('.XLSX', '').replace('.XLS', ''),
                                'Source File': file_name,
                                'Report Year/Period': 'N/A',
                                'Financial Statement Section': 'N/A (Excel Sheet Preview)',
                                'Data Point Name': f'Raw Excel Preview (Sheet: {first_sheet_name}, Top5Rx3C)',
                                'Data Point Value': excel_preview,
                                'Extraction Date': current_timestamp
                            }
                            all_extracted_rows.append(row)
                            logger.info(f"Successfully processed (preview) from Excel: {file_name}, sheet: {first_sheet_name}")
                        else:
                            logger.warning(f"Data in Excel sheet '{first_sheet_name}' from {file_name} is not a DataFrame.")
                    else:
                        logger.warning(f"Could not extract data from Excel: {file_name} (extractor returned None, empty, or not a dict).")
                else:
                    logger.warning(f"Unknown file type '{file_extension}' for file: {file_path}. Skipping.")
                
                files_processed_count += 1
            except Exception as e:
                logger.error(f"MAIN: Error processing file {file_path}: {e}", exc_info=True)
                # Continue to the next file

        logger.info(f"Finished processing all files. Total files attempted: {files_processed_count}/{len(files_to_process)}")

        final_df = pd.DataFrame() # Initialize to empty DataFrame
        if not all_extracted_rows:
            logger.info("No data successfully extracted from any files. Google Sheet writing will be skipped.")
            # Create an empty DataFrame with specific columns for consistency if needed elsewhere
            final_df = pd.DataFrame(columns=['Company Name', 'Source File', 'Report Year/Period', 
                                             'Financial Statement Section', 'Data Point Name', 
                                             'Data Point Value', 'Extraction Date'])
        else:
            final_df = pd.DataFrame(all_extracted_rows)
            logger.info(f"Created DataFrame from extracted data with {len(final_df)} rows.")
            
            try:
                buffer = io.StringIO()
                final_df.info(buf=buffer)
                df_info_str = buffer.getvalue()
                # logger.debug(f"MAIN: final_df info before all-to-string conversion:\n{df_info_str}") # Commented out
            except Exception as e:
                logger.error(f"Error logging final_df info: {e}")

            logger.debug("MAIN: Converting all columns in final_df to string type.") # This DEBUG is fine
            for col in final_df.columns:
                final_df[col] = final_df[col].astype(str)
            
            try:
                buffer = io.StringIO()
                final_df.info(buf=buffer)
                df_info_str = buffer.getvalue()
                # logger.debug(f"MAIN: final_df info after all-to-string conversion:\n{df_info_str}") # Commented out
            except Exception as e:
                logger.error(f"Error logging final_df info after string conversion: {e}")

        # Data Writing Block - Restored to use final_df for "Raw Data Consolidated"
        try:
            logger.debug("MAIN: Entering data writing block.") # This DEBUG is fine
            raw_data_sheet_name = "Raw Data Consolidated"
            
            # logger.debug(f"MAIN: Pre-condition check: service type: {type(service)}, value: {str(service)[:100]}...") # Commented out
            logger.debug(f"MAIN: Pre-condition check: service type: {type(service)}") # Keeping type check as it's not voluminous
            logger.debug(f"MAIN: Pre-condition check: spreadsheet_id type: {type(spreadsheet_id)}, value: {spreadsheet_id}") # Keeping this
                
            if service and spreadsheet_id:
                if not final_df.empty:
                    logger.info(f"MAIN: Condition `if service and spreadsheet_id` is TRUE and final_df is not empty. About to call write_data_to_sheet for '{raw_data_sheet_name}'.")
                    write_success = write_data_to_sheet(service, spreadsheet_id, raw_data_sheet_name, final_df)
                    logger.info(f"MAIN: Returned from write_data_to_sheet for '{raw_data_sheet_name}'. Success flag: {write_success}")

                    if write_success:
                        logger.info(f"Successfully wrote data to sheet: '{raw_data_sheet_name}'.")
                    else:
                        logger.error(f"Failed to write data to sheet: '{raw_data_sheet_name}'. Check 'app.log' for details.")
                else:
                    logger.info("MAIN: final_df is empty. Skipping call to write_data_to_sheet.")
            else:
                logger.error("MAIN: Condition `if service and spreadsheet_id` is FALSE. Cannot write data because service or spreadsheet_id is not available.")
        
        except Exception as e:
            logger.critical(f"MAIN: An unexpected critical error occurred in the data writing block: {e}", exc_info=True)
        
        # (Placeholder) Calculating and Writing Ratios - remains a placeholder
        logger.info("--- Placeholder: Calculating and Writing Ratios (using obtained spreadsheet_id) ---")
        if spreadsheet_id: 
            logger.info(f"Spreadsheet ID {spreadsheet_id} is available for ratio calculations and writing.")
            logger.info("Simulating calculation of ratios using functions from financial_ratios.py...")
            dummy_data_for_ratios = {"Sales": 1000, "COGS": 400, "Operating Expenses": 200, "Net Income": 100, "Assets": 500, "EBITDA": 400, "Depreciation": 50, "Amortization": 50, "Total Investment": 800}
            logger.info(f"  - EBITDA (dummy): {calculate_ebitda(dummy_data_for_ratios)}")
            logger.info(f"  - EBIT (dummy): {calculate_ebit(dummy_data_for_ratios)}")
            # ... (other ratio calls) ...
            logger.info("Simulating writing calculated ratios to sheet 'Financial Ratios' in the created spreadsheet...")
        else:
            logger.warning("Skipping calculation and writing of ratios as spreadsheet_id was not obtained or an error occurred before its use.")

    logger.info("Main application flow completed.")
