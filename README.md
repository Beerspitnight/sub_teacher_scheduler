    # Teacher Absence Tracking & Coverage Automation

## Overview

This project automates the daily task of creating a teacher substitute coverage report. It fetches a daily absence report (as a PDF) from Google Drive, intelligently parses the information, looks up each absent teacher's schedule from a master Google Sheet, and compiles a complete, detailed coverage report in a final Google Sheet.

* **The daily absence report is from Frontline.**  The script was created to read and parse the structure of the Frontline report.  

Additionally, it includes a simple web interface for manually entering one-off absences that may not be on the main report.

---

## Key Features

* **Automated PDF Processing**: Automatically finds and downloads the latest "Aesop - Daily Report.pdf" from a specified Google Drive folder.
* **Intelligent Data Extraction**: Reads the PDF to accurately match absent teachers with their assigned substitutes.
* **Schedule Integration**: Looks up each absent teacher in a "Master Schedule" Google Sheet and pulls their period-by-period schedule into the final report.
* **Web-Based Manual Entry**: Provides a simple web form to manually add an absence to the coverage sheet.
* **Centralized Reporting**: Consolidates all information into a single, clean "Daily Coverage" Google Sheet.

---

## Project Structure

Here are the key files that make up this project:

* `run_daily_coverage.py`: The main script for the automated process. It handles fetching, parsing, and generating the daily report.
* `app.py`: The script for the manual entry web form. It uses the Flask web framework.
* `requirements.txt`: A list of all the Python packages this project needs to run.
* `credentials.json`: Your private key file from Google Cloud that gives your scripts permission to access your Google Drive and Sheets. **(Important: Keep this file private and do not share it publicly).**
* `/templates/form.html`: The HTML file that creates the structure and look of the manual entry web form.

---

## Setup and Installation

Follow these steps carefully to get the project running on your MacBook Pro.

### Step 1: Google Cloud and Service Account Setup

This is the most important step. You need to create a "service account" so your Python scripts have permission to access your Google files.

1.  **Create a Google Cloud Project**:
    * Go to the [Google Cloud Console](https://console.cloud.google.com/).
    * Click the project dropdown at the top of the page and click **"New Project"**.
    * Give it a name like "Teacher Coverage Automation" and click **"Create"**.

2.  **Enable the Necessary APIs**:
    * Make sure your new project is selected in the dropdown.
    * In the search bar at the top, search for and **enable** the **Google Drive API**.
    * Search for and **enable** the **Google Sheets API**.

3.  **Create a Service Account**:
    * In the search bar, search for **"Service Accounts"** and go to that page.
    * Click **"+ Create Service Account"** at the top.
    * Give it a name (e.g., `coverage-bot`) and a description, then click **"Create and Continue"**.
    * In the "Grant this service account access to project" step, select the role **"Editor"** and click **"Continue"**.
    * Skip the last step by clicking **"Done"**.

4.  **Generate Your Credentials Key**:
    * On the Service Accounts page, find the account you just created and click on its email address.
    * Go to the **"Keys"** tab.
    * Click **"Add Key"** -> **"Create new key"**.
    * Choose **JSON** as the key type and click **"Create"**.
    * A file will be downloaded to your computer. **This is your `credentials.json` file.**

5.  **Move the Credentials File**:
    * Find the downloaded JSON file in your "Downloads" folder.
    * Rename it to exactly `credentials.json`.
    * Move this file into your project folder, alongside `run_daily_coverage.py` and `app.py`.

6.  **Share Your Google Drive Folder & Sheets**:
    * The service account needs permission to see your files. Find the long email address of the service account on the "Details" tab (it ends in `@...iam.gserviceaccount.com`).
    * **Share the Google Drive folder** containing your PDF reports with this email address (give it "Viewer" access).
    * **Share your Google Sheets** (Master Schedule, Teacher List, and Daily Coverage) with this email address (give it "Editor" access).

### Step 2: Install Python Packages

1.  Open the **Terminal** app on your Mac.
2.  Navigate to your project folder using the `cd` command (e.g., `cd ~/Documents/MyProject`).
3.  Install all the necessary packages at once by running:
    ```bash
    pip install -r requirements.txt
    ```

---

## Configuration

Before you run the scripts, you need to tell them which files to use by pasting in the correct IDs.

1.  **In `run_daily_coverage.py`**:
    * Open the script and find the `main()` function at the bottom.
    * Update the file IDs with the correct IDs from the URLs of your own Google Drive folder and Google Sheets.
    ```python
    folder_id = "1RJzDwcEluGkqglmX-e3cg09Ai35kBSQG"  # <-- Paste your Google Drive Folder ID here
    daily_coverage_sheet_id = "1vIpDw6erO5dO8IlMfoQlvfSS8fVd76WSaj28uwEZwuk" # <-- Your final report sheet
    teacher_list_sheet_id = "1Qsn5JtwHTvokL87wTYbHzDPTDCOwWVZ27LhN3x1aJMo" # <-- Your teacher list sheet
    master_schedule_id = "12XNbaa4AvahxYxR7D6Qa6DfrEeZPgrSiTTo5V9uFTsg" # <-- Your master schedule sheet
    ```

2.  **In `app.py`**:
    * Open the script and update the `DAILY_COVERAGE_ID` with the ID of your final report sheet.
    ```python
    DAILY_COVERAGE_ID = "1vIpDw6erO5dO8IlMfoQlvfSS8fVd76WSaj28uwEZwuk" # <-- Paste your final report Sheet ID here
    ```

---

## How to Use the Project

### To Run the Automated Daily Report:

1.  Make sure a new "Aesop - Daily Report.pdf" has been added to your shared Google Drive folder.
2.  Open the Terminal, navigate to your project folder, and run the command:
    ```bash
    python run_daily_coverage.py
    ```
3.  The script will print its progress and let you know when it has successfully updated the Google Sheet.

### To Use the Manual Entry Form:

1.  Open the Terminal, navigate to your project folder, and run the command:
    ```bash
    python app.py
    ```
2.  The terminal will show a message like `* Running on http://127.0.0.1:5000`.
3.  Open a web browser (like Chrome or Safari) and go to that address: **http://127.0.0.1:5000**.
4.  Fill out the form and click "Submit". The new entry will be added to the bottom of your "Daily Coverage" Google Sheet.
5.  To stop the web server, go back to the Terminal window and press **Control + C**.
