# update_google_sheets.py
# Parses daily_report.csv and cleans names, updates daily_coverage

import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import re

SERVICE_ACCOUNT_FILE = "/Users/bmcmanus/Documents/coverage_pulled_apart/teacher-absence-tracking/app/credentials.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(creds)

DAILY_REPORT_ID = "1xLysLjaHLvXl7BxtnO3xZZoxseICjeYgRrgWgnuTMLM"
DAILY_COVERAGE_ID = "1vIpDw6erO5dO8IlMfoQlvfSS8fVd76WSaj28uwEZwuk"

daily_report_sheet = client.open_by_key(DAILY_REPORT_ID).sheet1
daily_coverage_sheet = client.open_by_key(DAILY_COVERAGE_ID).sheet1

daily_report_data = daily_report_sheet.get_all_values()
df = pd.DataFrame(daily_report_data)

if df.empty or len(df.columns) < 9:
    print("\u274c Error: The daily_report sheet does not have enough data.")
    exit()

teacher_names = df.iloc[1:, 2].tolist()
durations = df.iloc[1:, 5].tolist()
subs = df.iloc[1:, 8].tolist()

def clean_teacher_name(name):
    return " ".join(name.split()[:2])

def clean_sub_name(name):
    return re.sub(r"Phone:.*", "", name).strip()

update_data = []
for teacher, duration, sub in zip(teacher_names, durations, subs):
    cleaned_teacher = clean_teacher_name(teacher)
    cleaned_sub = clean_sub_name(sub)
    update_data.append([cleaned_teacher, "", "", "", "", "", "", "", "", "", "", cleaned_sub, duration])

daily_coverage_sheet.update("A2", update_data)
print("\u2705 Successfully updated daily_coverage with cleaned names and NO phone numbers!")
