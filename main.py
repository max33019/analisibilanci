import os
import logging
from pdf_extractor import extract_text_from_pdf
from excel_extractor import extract_data_from_excel
from sheets_manager import get_sheets_service, create_spreadsheet
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
        logger.info("No files found in the 'bilanci' folder. Exiting.")
    else:
        logger.info(f"Found {len(files_to_process)} files to process: {files_to_process}")

        # Google Sheets Setup (using placeholders)
        logger.info("Initializing Google Sheets connection (simulated)...")
        sheets_service = None
        spreadsheet_id = None
        try:
            sheets_service = get_sheets_service() # Placeholder, returns None for now
            if sheets_service:
                logger.info("Successfully connected to Google Sheets service (simulated).")
                spreadsheet_id = create_spreadsheet(sheets_service, "Bilanci Aziendali Analysis")
                if spreadsheet_id:
                    logger.info(f"Spreadsheet created/accessed with ID (simulated): {spreadsheet_id}")
                else:
                    logger.warning("Failed to create/access spreadsheet (simulated).")
            else:
                logger.warning("Failed to connect to Google Sheets service (simulated). Using dummy spreadsheet ID.")
                # Fallback to dummy ID if service creation fails, to allow flow to continue
                spreadsheet_id = "dummy_sheet_id_fallback"
                logger.info(f"Using fallback Spreadsheet ID (simulated): {spreadsheet_id}")
        except Exception as e:
            logger.error(f"Error during Google Sheets setup: {e}", exc_info=True)
            spreadsheet_id = "dummy_sheet_id_fallback_error"
            logger.info(f"Using fallback Spreadsheet ID due to error: {spreadsheet_id}")


        all_extracted_data_pdf = [] # Placeholder for collecting PDF data
        all_extracted_data_excel = [] # Placeholder for collecting Excel data
        files_processed_count = 0

        for file_path in files_to_process:
            try:
                logger.info(f"Processing file: {file_path}")
                _, file_extension = os.path.splitext(file_path)
                file_extension = file_extension.lower()

                if file_extension == ".pdf":
                    extracted_text = extract_text_from_pdf(file_path)
                    if extracted_text:
                        logger.info(f"Extracted text from PDF: {file_path} (data not yet processed).")
                        all_extracted_data_pdf.append({"file": file_path, "text_data": extracted_text})
                    else:
                        logger.warning(f"Could not extract text from PDF: {file_path}")
                elif file_extension in [".xlsx", ".xls"]:
                    extracted_excel_data = extract_data_from_excel(file_path)
                    if extracted_excel_data:
                        logger.info(f"Extracted data from Excel: {file_path} (data not yet processed).")
                        all_extracted_data_excel.append({"file": file_path, "excel_sheets": extracted_excel_data})
                    else:
                        logger.warning(f"Could not extract data from Excel: {file_path}")
                else:
                    logger.warning(f"Unknown file type '{file_extension}' for file: {file_path}. Skipping.")
                files_processed_count += 1
            except Exception as e:
                logger.error(f"Error processing file {file_path}: {e}", exc_info=True)
                # Continue to the next file

        logger.info(f"Finished processing files. Total files processed: {files_processed_count}/{len(files_to_process)}")

        # (Placeholder) Data Aggregation & Structuring
        logger.info("--- Placeholder: Data Aggregation & Structuring ---")
        logger.info("Simulating aggregation: [Data from PDF 1, Data from Excel 1, ...]")


        # (Placeholder) Writing to Google Sheets
        logger.info("--- Placeholder: Writing to Google Sheets ---")
        if spreadsheet_id:
            logger.info(f"Target Spreadsheet ID: {spreadsheet_id}")
            logger.info("Simulating writing data to sheet 'Raw Data Consolidated'...")
            logger.info("Simulating writing data to sheet 'Processed Data' (for ratio input)...")
        else:
            logger.warning("Skipping writing to Google Sheets as spreadsheet_id is not available.")

        # (Placeholder) Calculating and Writing Ratios
        logger.info("--- Placeholder: Calculating and Writing Ratios ---")
        if spreadsheet_id:
            logger.info("Simulating calculation of ratios using functions from financial_ratios.py...")
            dummy_data_for_ratios = {"Sales": 1000, "COGS": 400, "Operating Expenses": 200, "Net Income": 100, "Assets": 500}
            # Example calls to show they are connected (using dummy data)
            # These will now use their own loggers if financial_ratios is updated
            logger.info(f"  - EBITDA (dummy): {financial_ratios.calculate_ebitda(dummy_data_for_ratios)}")
            logger.info(f"  - ROI (dummy): {financial_ratios.calculate_roi(dummy_data_for_ratios)}")
            logger.info("Simulating writing calculated ratios to sheet 'Financial Ratios'...")
        else:
            logger.warning("Skipping calculation and writing of ratios as spreadsheet_id is not available.")

    logger.info("Main application flow finished.")
