import pdfplumber
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import gspread
from fuzzywuzzy import fuzz
import re


def authenticate_google_apis():
    """
    Authenticate to Google APIs using the service account file.
    :return: Google Drive and Sheets client instances.
    """
    credentials = Credentials.from_service_account_file(
        "credentials.json",  # Your service account JSON file
        scopes=["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/spreadsheets"]
    )
    drive_service = build("drive", "v3", credentials=credentials)
    sheets_client = gspread.authorize(credentials)
    return drive_service, sheets_client


def get_latest_pdf_in_folder(drive_service, folder_id, file_name="Aesop - Daily Report.pdf"):
    """
    Find the latest PDF in the specified Google Drive folder.
    :param drive_service: Google Drive API service instance.
    :param folder_id: ID of the Google Drive folder.
    :param file_name: Name of the file to look for.
    :return: File ID of the latest matching file.
    """
    query = f"'{folder_id}' in parents and name='{file_name}' and mimeType='application/pdf'"
    results = drive_service.files().list(q=query, spaces="drive", fields="files(id, name)").execute()
    files = results.get("files", [])
    if not files:
        raise FileNotFoundError(f"No file named '{file_name}' found in folder ID {folder_id}.")
    return files[0]["id"]  # Return the ID of the latest file


def download_pdf_from_drive(drive_service, file_id, destination_path):
    """
    Download a PDF file from Google Drive.
    :param drive_service: Google Drive API service instance.
    :param file_id: ID of the file to download.
    :param destination_path: Local path to save the file.
    """
    request = drive_service.files().get_media(fileId=file_id)
    with open(destination_path, "wb") as f:
        f.write(request.execute())
    print(f"Downloaded PDF to {destination_path}")


def load_teacher_list(sheet_id):
    """
    Load the list of teacher names from a Google Sheet.
    :param sheet_id: The ID of the Google Sheet containing the teacher names.
    :return: List of teacher names.
    """
    try:
        sheets_client = authenticate_google_apis()[1]
        sheet = sheets_client.open_by_key(sheet_id).sheet1  # Access the first sheet
        rows = sheet.get_all_values()

        # Assuming the first column contains the teacher names
        teacher_list = [row[0] for row in rows[1:] if row[0]]  # Skip the header row
        return teacher_list
    except Exception as e:
        print(f"Error loading teacher list from Google Sheet: {e}")
        return []


def extract_teacher_and_sub_data(pdf_path, teacher_list):
    """
    Extract teacher names and substitute names from the PDF file.
    :param pdf_path: Path to the PDF file.
    :param teacher_list: List of teacher names to match.
    :return: A dictionary containing teacher names and substitutes.
    """
    teacher_matches = set()
    substitutes = set()
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                print("\n--- Extracted Text ---")
                print(text)  # Debugging: print the extracted text
                lines = text.split("\n")

                for line in lines:
                    # Match teacher names
                    for teacher in teacher_list:
                        if fuzz.partial_ratio(teacher.lower(), line.lower()) > 80:
                            teacher_matches.add(teacher)

                    # Match substitutes (lines containing "Substitute" or similar structure)
                    substitute_match = re.search(r"Substitute:\s*([\w\s,]+)", line)
                    if substitute_match:
                        substitute_name = substitute_match.group(1).strip()
                        substitutes.add(substitute_name)

                    # Check for direct assignments (e.g., teacher with substitute in the same line)
                    for teacher in teacher_list:
                        if teacher in line:
                            # Extract substitute name if present in the same line
                            possible_sub = re.search(r"(?<=No\s)[\w\s]+$", line)
                            if possible_sub:
                                substitutes.add(possible_sub.group(0).strip())

    except Exception as e:
        print(f"Error processing PDF: {e}")

    return {
        "teachers": list(teacher_matches),
        "substitutes": list(substitutes),
    }


def update_google_sheet(sheet_id, absence_data, master_schedule_id):
    """
    Updates the final coverage sheet by combining absence data with the master schedule.
    """
    try:
        # Authenticate and open all the sheets we need
        sheets_client = authenticate_google_apis()[1]
        sheet = sheets_client.open_by_key(sheet_id).sheet1
        master_schedule_sheet = sheets_client.open_by_key(master_schedule_id).sheet1
        master_schedule_data = master_schedule_sheet.get_all_values()

        # Define the headers for your final report
        headers = ["Teacher/TA", "HR", "1", "2", "3", "4", "5", "6", "7", "8", "9", "Subs", "Duration"]
        
        final_report_data = [headers]

        # Get the list of [teacher, substitute] pairs from the extracted data
        teacher_sub_pairs = absence_data["pairs"]

        for teacher_name, sub_name in teacher_sub_pairs:
            # Create a blank row with the correct number of columns
            new_row = [""] * len(headers)
            
            # Put the teacher, sub, and a placeholder for duration in the correct columns
            new_row[0] = teacher_name
            new_row[11] = sub_name
            new_row[12] = "Full Day" # You can adjust this if you extract duration later

            # Now, find this teacher's schedule in the master schedule data
            best_match_row = None
            highest_ratio = 0
            for master_row in master_schedule_data[1:]: # Skip header row of master
                if not master_row or not master_row[0]: continue # Skip empty rows
                
                # Use fuzzy matching to find the correct teacher
                ratio = fuzz.ratio(teacher_name.lower(), master_row[0].lower())
                if ratio > 85 and ratio > highest_ratio:
                    highest_ratio = ratio
                    best_match_row = master_row
            
            # If we found a matching schedule, fill in the periods
            if best_match_row:
                for i in range(1, 11): # Corresponds to columns HR through 9
                    if i < len(best_match_row):
                        new_row[i] = best_match_row[i]
            
            final_report_data.append(new_row)

        # Clear the sheet and update it with our final, complete report
        sheet.clear()
        if len(final_report_data) > 1:
            sheet.update('A1', final_report_data, value_input_option='USER_ENTERED')
            print(f"\u2705 Successfully updated {len(final_report_data)-1} rows in the daily coverage sheet!")
        else:
            print("\u26a0\ufe0f No absence data found to update.")

    except Exception as e:
        print(f"\u274c An error occurred while updating the Google Sheet: {e}")

def main():
    folder_id = "1RJzDwcEluGkqglmX-e3cg09Ai35kBSQG"
    daily_coverage_sheet_id = "14dPUDBEEE7MuYLGH0UuaWhtFvaSMrK1eBYORinnTHUk"
    teacher_list_sheet_id = "1Qsn5JtwHTvokL87wTYbHzDPTDCOwWVZ27LhN3x1aJMo"
    master_schedule_id = "12XNbaa4AvahxYxR7D6Qa6DfrEeZPgrSiTTo5V9uFTsg" # Master Schedule Sheet ID
    destination_pdf = "Aesop - Daily Report.pdf"

    # Authenticate and get Google Drive & Sheets services
    drive_service, _ = authenticate_google_apis()

    # Step 1: Find and download the latest PDF
    pdf_file_id = get_latest_pdf_in_folder(drive_service, folder_id)
    download_pdf_from_drive(drive_service, pdf_file_id, destination_pdf)

    # Step 2: Load teacher list from Google Sheet
    teacher_list = load_teacher_list(teacher_list_sheet_id)

    # Step 3: Extract teacher and substitute data from the PDF
    data = extract_teacher_and_sub_data(destination_pdf, teacher_list)

    # Display extracted data
    print("\nExtracted Data:")
    print(data)

    # Step 4: Update the Daily Coverage Template
    update_google_sheet(daily_coverage_sheet_id, data, master_schedule_id)


if __name__ == "__main__":
    main()
