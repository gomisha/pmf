import re

import pymupdf
import os
import csv
import sys

# configuration
KEYWORDS = ["BCBS", "Blue Cross", "BlueCross" "Blue Shield", "BlueShld", "Availity", "Change Healthcare", "EFT/ACH Payment from", "Insurance Reimbursement"]
NEGATIVE_KEYWORDS = ["debit", "premium"]
WINDOW_SIZE = 4  # number of words to look around the keyword for a negative keyword
OUTPUT_FILE = "scan.csv"


def extract_text_from_pdf(file_path):
    try:
        doc = pymupdf.open(file_path)
        # reader = PdfReader(file_path)
        text = ""
        for page in doc:
            text += page.get_text() or ""
        return text, None
    except Exception as e:
        return "", str(e)


def count_nearby_negative_keywords(text, keyword, index, radius=50):
    lower_text = text.lower()
    start = max(0, index - radius)
    end = min(len(lower_text), index + radius)
    context = lower_text[start:end]
    count = sum(1 for neg in NEGATIVE_KEYWORDS if neg.lower() in context)
    found_keywords = [neg for neg in NEGATIVE_KEYWORDS if neg.lower() in context]
    return count, found_keywords


def scan_pdf(file_path):
    text, error = extract_text_from_pdf(file_path)
    lower_text = text.lower()
    word_count = len(text.split())

    matched_keywords = []
    matched_negative_keywords = []
    positive_keyword_count = 0
    nearby_negative_keyword_count = 0

    if not error:
        for keyword in KEYWORDS:
            for match in re.finditer(re.escape(keyword.lower()), lower_text):
                positive_keyword_count += 1
                matched_keywords.append(keyword)
                neg_count, neg_matches = count_nearby_negative_keywords(lower_text, keyword, match.start())
                nearby_negative_keyword_count += neg_count
                matched_negative_keywords.extend(neg_matches)

    # Append results to CSV
    with open(OUTPUT_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            file_path,
            positive_keyword_count,
            "|".join(matched_keywords),
            nearby_negative_keyword_count,
            "|".join(matched_negative_keywords),
            error or "",
            word_count
        ])


def initialize_csv():
    # if not os.path.exists(OUTPUT_FILE):
    with open(OUTPUT_FILE, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            "file_path",
            "positive_keyword_count",
            "matched_keywords",
            "nearby_negative_keyword_count",
            "matched_negative_keywords",
            "error",
            "word_count"
        ])


def main(folder_path):
    initialize_csv()

    for root, _, files in os.walk(folder_path):
        for name in files:
            if name.lower().endswith(".pdf"):
                file_path = os.path.join(root, name)
                print(f"Scanning: {file_path}")
                scan_pdf(file_path)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scan.py /path/to/folder")
        sys.exit(1)
    folder_to_scan = sys.argv[1]
    main(folder_to_scan)
