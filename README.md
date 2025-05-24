# Financial Data Extractor and Analyzer

This Python application extracts financial data from PDF and Excel files (specifically company balance sheets and income statements), uploads it to a Google Sheet, calculates key financial ratios, and prepares the data for dashboarding and comparative analysis.

## Prerequisites

*   Python 3.8+
*   pip (Python package installer)
*   Access to a Google account and Google Cloud Platform.

## Setup Instructions

1.  **Clone the Repository (if applicable):**
    ```bash
    # git clone <repository_url>
    # cd <repository_name>
    ```

2.  **Create and Activate a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    # On Windows
    venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Up Google Sheets API Credentials:**
    *   Go to the [Google Cloud Console](https://console.cloud.google.com/).
    *   Create a new project or select an existing one.
    *   Search for "Google Sheets API" in the API library and enable it for your project.
    *   Go to "Credentials" in the APIs & Services section.
    *   Click "+ CREATE CREDENTIALS" and choose "OAuth client ID".
    *   If prompted, configure the OAuth consent screen:
        *   User Type: External (or Internal if applicable).
        *   App name: (e.g., "Bilanci Analyzer")
        *   User support email: Your email.
        *   Developer contact information: Your email.
        *   Save and continue.
        *   Scopes: Add `https://www.googleapis.com/auth/spreadsheets`.
        *   Test users: Add your Google account email.
        *   Save and continue.
    *   Back on the "Create OAuth client ID" screen:
        *   Application type: "Desktop app".
        *   Name: (e.g., "Bilanci Desktop Client")
        *   Click "CREATE".
    *   A dialog will appear showing your client ID and client secret. Click "DOWNLOAD JSON" to download the credentials file.
    *   **Rename the downloaded file to `credentials.json` and place it in the root directory of this project.** This file is sensitive and is included in `.gitignore` to prevent accidental commits.
    *   The first time you run the application, you will be prompted to authorize access to your Google Account via a web browser. Follow the instructions to grant permission. A `token.json` file will be created in the project root to store your authorization tokens for future runs.

## Usage

1.  **Place Input Files:**
    *   Create a folder named `bilanci` in the root directory of the project if it doesn't already exist.
    *   Place your PDF and Excel financial statement files into this `bilanci` folder.

2.  **Run the Application:**
    ```bash
    python main.py
    ```

3.  **Check Output:**
    *   The application will process the files and attempt to create/update a Google Sheet named "Bilanci Aziendali Analysis" (or similar, as defined in the script) in your Google Drive.
    *   Log messages will be printed to the console and saved in `app.log`.
    *   The Google Sheet will contain:
        *   `Raw Data Consolidated`: Extracted financial line items.
        *   `Company Summaries`: Pivoted data for easier comparison.
        *   `Financial Ratios`: Calculated ratios per company.
    *   You can then use Google Sheets' built-in features to create dashboards based on these sheets.

## Project Structure

*   `main.py`: The main script to run the application.
*   `pdf_extractor.py`: Module for extracting data from PDF files.
*   `excel_extractor.py`: Module for extracting data from Excel files.
*   `sheets_manager.py`: Module for interacting with the Google Sheets API.
*   `financial_ratios.py`: Module for calculating financial ratios.
*   `bilanci/`: Folder where input PDF/Excel files should be placed.
*   `requirements.txt`: List of Python dependencies.
*   `app.log`: Log file for application events and errors.
*   `credentials.json`: (You create this) Google API credentials.
*   `token.json`: (Created after first run) Google API authorization token.
