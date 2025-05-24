import os
import logging
import pandas as pd
from pdf_extractor import extract_text_from_pdf
from excel_extractor import extract_data_from_excel
from sheets_manager import get_sheets_service, create_spreadsheet, write_data_to_sheet
import financial_ratios # Import the whole module for clarity

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO) # Or logging.DEBUG for more detail

# Create handlers
file_handler = logging.FileHandler('app.log')
console_handler = logging.StreamHandler()

# Create formatter and add it to handlers
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)


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

        raw_data_sheet_name = "Raw Data Consolidated"
        logger.info(f"Attempting to write sample data to sheet: '{raw_data_sheet_name}' in spreadsheet ID: {spreadsheet_id}")
        
        # Ensure 'service' and 'spreadsheet_id' are available from previous steps
        if service and spreadsheet_id: # These should be valid if script reached here
            write_success = write_data_to_sheet(service, spreadsheet_id, raw_data_sheet_name, sample_df)
            if write_success:
                logger.info(f"Successfully wrote sample data to sheet: '{raw_data_sheet_name}'.")
            else:
                logger.error(f"Failed to write sample data to sheet: '{raw_data_sheet_name}'. Check 'app.log' for details.")
        else:
            # This case should ideally not be reached if the exit() calls in earlier Google Sheets setup work as expected.
            logger.error("Cannot write sample data because Google Sheets service or spreadsheet_id is not available.")
        
        # (Placeholder) Calculating and Writing Ratios - this remains a placeholder
        logger.info("--- Placeholder: Calculating and Writing Ratios (using obtained spreadsheet_id) ---")
        if spreadsheet_id: 
            logger.info(f"Spreadsheet ID {spreadsheet_id} is available for ratio calculations and writing.")
            logger.info("Simulating calculation of ratios using functions from financial_ratios.py...")
            dummy_data_for_ratios = {"Sales": 1000, "COGS": 400, "Operating Expenses": 200, "Net Income": 100, "Assets": 500}
            logger.info(f"  - EBITDA (dummy): {financial_ratios.calculate_ebitda(dummy_data_for_ratios)}")
            logger.info(f"  - ROI (dummy): {financial_ratios.calculate_roi(dummy_data_for_ratios)}")
            logger.info("Simulating writing calculated ratios to sheet 'Financial Ratios' in the created spreadsheet...")
        else:
            logger.warning("Skipping calculation and writing of ratios as spreadsheet_id was not obtained.")

    logger.info("Main application flow completed (sample data writing attempted).")
