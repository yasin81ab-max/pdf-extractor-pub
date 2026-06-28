#!/usr/bin/env python3
"""
این اسکریپت داخل GitHub Action اجرا می‌شود (نه روی کامپیوتر کاربر نهایی).
یک ستون از Google Sheet را می‌خواند و در subjects.json می‌نویسد.

متغیرهای محیطی (از طریق GitHub Secrets/Variables):
  SHEET_ID         شناسه‌ی شیت (از URL: .../d/<SHEET_ID>/edit)
  WORKSHEET        نام برگه (پیش‌فرض: Sheet1)
  SUBJECT_COLUMN   حرف ستون موضوع‌ها، مثلاً A (پیش‌فرض: A)
  SKIP_HEADER      اگر "1" باشد، سطر اول (هدر) نادیده گرفته می‌شود (پیش‌فرض: 1)

فایل اعتبارنامه باید قبل از اجرا در مسیر sa.json نوشته شده باشد (در Action انجام می‌شود).
"""
import os
import json
import gspread
from google.oauth2.service_account import Credentials

SHEET_ID = os.environ["SHEET_ID"]
WORKSHEET = os.environ.get("WORKSHEET", "Sheet1")
COLUMN = os.environ.get("SUBJECT_COLUMN", "A").strip().upper()
SKIP_HEADER = os.environ.get("SKIP_HEADER", "1") == "1"

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
creds = Credentials.from_service_account_file("sa.json", scopes=SCOPES)
gc = gspread.authorize(creds)

ws = gc.open_by_key(SHEET_ID).worksheet(WORKSHEET)

# تبدیل حرف ستون به شماره (A→1، B→2، ...)
col_idx = 0
for ch in COLUMN:
    col_idx = col_idx * 26 + (ord(ch) - 64)
values = ws.col_values(col_idx)

if SKIP_HEADER and values:
    values = values[1:]

# پاک‌سازی + حذف تکراری‌ها با حفظ ترتیب
seen, subjects = set(), []
for v in values:
    s = (v or "").strip()
    if s and s not in seen:
        seen.add(s)
        subjects.append(s)

with open("subjects.json", "w", encoding="utf-8") as f:
    json.dump({"subjects": subjects}, f, ensure_ascii=False, indent=2)

print(f"wrote {len(subjects)} subjects to subjects.json")
