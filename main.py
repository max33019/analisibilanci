import os
import logging

# Force DEBUG level logging configuration
# Using a more detailed format for better debugging
# Using mode='w' for app.log to overwrite on each run for cleaner debugging sessions
# force=True requires Python 3.8+
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - Line %(lineno)d - %(message)s',
    handlers=[
        logging.FileHandler('app.log', mode='w'),
        logging.StreamHandler()
    ],
    force=True 
)

# Get the logger for the main module *after* basicConfig
# This logger instance will use the configuration set by basicConfig
logger = logging.getLogger(__name__)

# Test log right after basicConfig to ensure it's working
logger.debug("DEBUG logging explicitly configured in main.py using basicConfig with force=True.")

# Now import other project modules (so they inherit the root logger config if they use logging.getLogger(__name__))
import pandas as pd
from pdf_extractor import extract_text_from_pdf
from excel_extractor import extract_data_from_excel
from sheets_manager import get_sheets_service, create_spreadsheet, write_data_to_sheet
# Updated import for financial_ratios to match the provided snippet
from financial_ratios import (
    calculate_ebitda, calculate_ebit, calculate_roi, 
    calculate_roe, calculate_roa, calculate_personnel_costs_impact,
    calculate_contribution_margin
)

# The old logger configuration block below has been removed:
# # Configure logging
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG) # Set to DEBUG to capture all levels of logs
# 
# # Create handlers
# file_handler = logging.FileHandler('app.log')
# console_handler = logging.StreamHandler()
# 
# # Create formatter and add it to handlers
# formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(message)s')
# file_handler.setFormatter(formatter)
# console_handler.setFormatter(formatter)
# 
# # Add handlers to the logger
# logger.addHandler(file_handler)
# logger.addHandler(console_handler)


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

    files_to_process = get_files_from_bilanci_folder()

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
        
        spreadsheet_title = "Bilanci Aziendali Analysis" # Or make this configurable
        logger.info(f"Attempting to create or get spreadsheet: '{spreadsheet_title}'")
        spreadsheet_id = create_spreadsheet(service, spreadsheet_title)

        if not spreadsheet_id:
            logger.critical(f"Failed to create or access spreadsheet '{spreadsheet_title}'. Spreadsheet ID is None.")
            logger.critical("Check 'app.log' for more detailed error messages from the spreadsheet creation process.")
            logger.critical("Exiting application.")
            exit()
            
        logger.info(f"Successfully obtained spreadsheet ID: {spreadsheet_id} for title: '{spreadsheet_title}'")

        # The file processing loop below is still a placeholder for actual data extraction.
        # For this subtask, we focus on writing sample data after this loop.
        files_processed_count = 0
        if files_to_process: # Only loop if there are files
            for file_path in files_to_process:
                logger.info(f"Simulating processing for file: {file_path} (placeholder - no actual extraction)")
                # Actual extraction logic (extract_text_from_pdf, extract_data_from_excel)
                # will be integrated here in future steps. For now, we just log.
                files_processed_count +=1
            logger.info(f"Finished simulated processing of {files_processed_count} files.")
        else:
            logger.info("No files were in 'bilanci' folder to simulate processing for.")

        # Create and write sample data (after the loop)
        logger.info("Preparing sample data to test writing to Google Sheets...")
        sample_data = {
            'Company Name': ['Test Company A', 'Test Company A', 'Test Company B'],
            'Source File': ['sample1.pdf', 'sample1.pdf', 'sample2.xlsx'],
            'Report Year/Period': [2023, 2023, 2022],
            'Financial Statement Section': ['Stato Patrimoniale', 'Conto Economico', 'Stato Patrimoniale'],
            'Data Point Name': ['Total Assets', 'Revenue', 'Total Liabilities'],
            'Data Point Value': [100000, 50000, 30000],
            'Extraction Date': pd.to_datetime(['2024-01-15', '2024-01-15', '2024-01-16'])
        }
        sample_df = pd.DataFrame(sample_data)
        logger.info(f"Sample DataFrame created with {len(sample_df)} rows.")

    # Convert Timestamp objects to string format
    try:
        sample_df['Extraction Date'] = sample_df['Extraction Date'].dt.strftime('%Y-%m-%d %H:%M:%S')
        logger.info("Converted 'Extraction Date' column to string format.")
    except Exception as e:
        logger.error(f"Error converting 'Extraction Date' to string: {e}")
        # Decide if you want to proceed with original dates or exit, for now, log and proceed cautiously
        # This error shouldn't happen with pd.to_datetime input, but good to be aware

    # NEW: Convert all columns to string type for robust API submission
    logger.debug("MAIN: Converting all columns in sample_df to string type.")
    for col in sample_df.columns:
        # Optional: log original dtype before conversion
        # logger.debug(f"MAIN: Column '{col}' original dtype: {sample_df[col].dtype}")
        sample_df[col] = sample_df[col].astype(str)
        # Optional: log new dtype after conversion
        # logger.debug(f"MAIN: Column '{col}' new dtype: {sample_df[col].dtype}")
    
    # Log df.info() again to see the dtypes after conversion
    try:
        import io
        buffer = io.StringIO()
        sample_df.info(buf=buffer)
        df_info_str = buffer.getvalue()
        logger.debug(f"MAIN: DataFrame info after all-to-string conversion:\n{df_info_str}")
    except Exception as e:
        logger.error(f"Error logging DataFrame info: {e}")

    # Start of the try block for data writing
    try:
        logger.debug("MAIN: Entering critical data writing block (inside try).")
        raw_data_sheet_name = "Raw Data Consolidated"
        logger.debug("MAIN: Reached point immediately after defining raw_data_sheet_name.")

        logger.debug(f"MAIN: Pre-condition check: service type: {type(service)}, value: {str(service)[:100]}...")
        logger.debug(f"MAIN: Pre-condition check: spreadsheet_id type: {type(spreadsheet_id)}, value: {spreadsheet_id}")
            
        if service and spreadsheet_id:
            logger.info("MAIN: Condition `if service and spreadsheet_id` is TRUE. About to call write_data_to_sheet.")
            # Ensure sample_df is defined in this scope. It is defined earlier in the main block.
            write_success = write_data_to_sheet(service, spreadsheet_id, raw_data_sheet_name, sample_df)
            logger.info(f"MAIN: Returned from write_data_to_sheet. Success flag: {write_success}")

            if write_success:
                logger.info(f"Successfully wrote sample data to sheet: '{raw_data_sheet_name}'.")
            else:
                logger.error(f"Failed to write sample data to sheet: '{raw_data_sheet_name}'. Check 'app.log' for details.")
        else:
            logger.error("MAIN: Condition `if service and spreadsheet_id` is FALSE. Cannot write sample data because service or spreadsheet_id is not available.")
    
    except Exception as e:
        logger.critical(f"MAIN: An unexpected critical error occurred in the data writing preparation block: {e}", exc_info=True)

        
    # (Placeholder) Calculating and Writing Ratios - this remains a placeholder
    logger.info("--- Placeholder: Calculating and Writing Ratios (using obtained spreadsheet_id) ---")
    if spreadsheet_id: # This check needs to be robust against spreadsheet_id possibly not being defined if the error occurred before its assignment.
                       # However, in this specific structure, spreadsheet_id is defined before the try block.
        logger.info(f"Spreadsheet ID {spreadsheet_id} is available for ratio calculations and writing.")
        logger.info("Simulating calculation of ratios using functions from financial_ratios.py...")
        # Using the specific imported functions now
        dummy_data_for_ratios = {"Sales": 1000, "COGS": 400, "Operating Expenses": 200, "Net Income": 100, "Assets": 500, "EBITDA": 400, "Depreciation": 50, "Amortization": 50, "Total Investment": 800}
        logger.info(f"  - EBITDA (dummy): {calculate_ebitda(dummy_data_for_ratios)}")
        logger.info(f"  - EBIT (dummy): {calculate_ebit(dummy_data_for_ratios)}")
        logger.info(f"  - ROI (dummy): {calculate_roi(dummy_data_for_ratios)}")
        logger.info(f"  - ROE (dummy): {calculate_roe(dummy_data_for_ratios)}")
        logger.info(f"  - ROA (dummy): {calculate_roa(dummy_data_for_ratios)}")
        logger.info(f"  - Personnel Costs Impact (dummy): {calculate_personnel_costs_impact(dummy_data_for_ratios)}")
        logger.info(f"  - Contribution Margin (dummy): {calculate_contribution_margin(dummy_data_for_ratios)}")
        logger.info("Simulating writing calculated ratios to sheet 'Financial Ratios' in the created spreadsheet...")
    else:
        logger.warning("Skipping calculation and writing of ratios as spreadsheet_id was not obtained or an error occurred before its use.")

    logger.info("Main application flow completed (sample data writing attempted).")
