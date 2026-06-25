"""
Google Sheets storage — saves reports, ideas, scripts, and trends.
"""

import os
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

SHEET_TABS = ["Reports", "Ideas", "Scripts", "Trends", "Channels", "ContentPlan"]


def get_sheets_client():
    creds = Credentials.from_service_account_file(
        os.getenv("GOOGLE_CREDENTIALS_FILE", "config/google_credentials.json"),
        scopes=SCOPES,
    )
    return gspread.authorize(creds)


def get_or_create_sheet(tab_name: str):
    gc = get_sheets_client()
    spreadsheet = gc.open_by_key(os.getenv("GOOGLE_SHEETS_ID"))

    try:
        return spreadsheet.worksheet(tab_name)
    except gspread.WorksheetNotFound:
        return spreadsheet.add_worksheet(title=tab_name, rows=1000, cols=20)


def save_report(report_text: str, report_type: str = "daily") -> bool:
    try:
        sheet = get_or_create_sheet("Reports")
        sheet.append_row([
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            report_type,
            report_text[:50000],
        ])
        return True
    except Exception as e:
        print(f"Failed to save report: {e}")
        return False


def save_idea(idea: str, score: str, topic_priority: int = 5) -> bool:
    try:
        sheet = get_or_create_sheet("Ideas")
        sheet.append_row([
            datetime.now().strftime("%Y-%m-%d"),
            idea,
            topic_priority,
            score,
        ])
        return True
    except Exception as e:
        print(f"Failed to save idea: {e}")
        return False


def save_script(topic: str, script_text: str) -> bool:
    try:
        sheet = get_or_create_sheet("Scripts")
        sheet.append_row([
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            topic,
            script_text[:50000],
        ])
        return True
    except Exception as e:
        print(f"Failed to save script: {e}")
        return False


def get_recent_reports(limit: int = 5) -> list[dict]:
    try:
        sheet = get_or_create_sheet("Reports")
        rows = sheet.get_all_records()
        return rows[-limit:]
    except Exception:
        return []
