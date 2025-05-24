import pandas as pd
import logging

logger = logging.getLogger(__name__)

def extract_data_from_excel(excel_path):
    """
    Opens an Excel file and reads all sheets into a dictionary of DataFrames.

    Args:
        excel_path (str): The path to the Excel file.

    Returns:
        dict: A dictionary where keys are sheet names and values are pandas DataFrames.
              Returns None if the file cannot be opened or processed.
    """
    logger.info(f"Attempting to extract data from Excel: {excel_path}")
    try:
        # Read all sheets into a dictionary of DataFrames
        excel_data = pd.read_excel(excel_path, sheet_name=None)
        if excel_data:
            logger.info(f"Successfully extracted data from {excel_path}. Sheets found: {list(excel_data.keys())}")
            return excel_data
        else:
            logger.info(f"No data or sheets found in {excel_path}.")
            return None
    except FileNotFoundError:
        logger.error(f"Error: Excel file not found at {excel_path}")
        return None
    except Exception as e:
        logger.error(f"Error processing Excel file {excel_path}: {e}", exc_info=True)
        return None
