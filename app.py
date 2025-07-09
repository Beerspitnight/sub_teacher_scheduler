import gspread
from google.oauth2.service_account import Credentials
from flask import Flask, render_template, request, redirect, url_for

# --- Basic Configuration ---

# This creates your web application
app = Flask(__name__)

# The ID of your "daily_coverage" Google Sheet
# You can get this from the URL of the sheet.
DAILY_COVERAGE_ID = "1vIpDw6erO5dO8IlMfoQlvfSS8fVd76WSaj28uwEZwuk"

# --- Google Sheets Authentication ---

def get_sheets_client():
    """Authenticates with Google and returns a client to interact with sheets."""
    # Ensure your credentials.json file is in the same folder as this script
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
    client = gspread.authorize(creds)
    return client

# --- Web Page Routes ---

@app.route('/')
def index():
    """
    Renders the main page with the form.
    The 'form.html' file needs to be in a folder named 'templates'.
    """
    return render_template('form.html')

@app.route('/submit', methods=['POST'])
def submit():
    """
    Handles the form submission, gets the data, and sends it to Google Sheets.
    """
    try:
        # Get the data from the form fields
        teacher_name = request.form.get('teacher_name', '')
        duration = request.form.get('duration', '')
        
        # 'getlist' is used for checkboxes to get all selected values
        periods = request.form.getlist('periods')
        
        # --- Prepare the row for Google Sheets ---
        
        # This is the header row of your "daily_coverage" sheet
        headers = ["Teacher/TA", "HR", "1", "2", "3", "4", "5", "6", "7", "8", "9", "Subs", "Duration"]
        
        # Create a blank row, then fill it in
        new_row = [""] * len(headers)
        new_row[0] = teacher_name
        new_row[12] = duration
        
        # Place an 'X' in the columns for the selected periods
        for period in periods:
            if period in headers:
                col_index = headers.index(period)
                new_row[col_index] = 'X'

        # --- Append the new row to the Google Sheet ---
        client = get_sheets_client()
        daily_coverage_sheet = client.open_by_key(DAILY_COVERAGE_ID).sheet1
        daily_coverage_sheet.append_row(new_row, value_input_option='USER_ENTERED')

        # Redirect back to the main page after submission
        return redirect(url_for('index'))

    except Exception as e:
        # If something goes wrong, print the error
        print(f"An error occurred: {e}")
        return "An error occurred. Please check the console.", 500

# --- This part runs the web server ---
if __name__ == '__main__':
    # To view the web page, open a browser and go to http://127.0.0.1:5000
    app.run(debug=True)