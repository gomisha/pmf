import fitz  # PyMuPDF
import pymupdf
import os

# configuration
ROOT_DIR = "data-test"
KEYWORDS = ["BCBS", "Blue Cross", "Blue Shield", "Availity", "Change Healthcare", "EFT/ACH Payment from", "Insurance Reimbursement"]


def contains_keyword(tull_text):
    text_lower = tull_text.lower()
    for keyword in KEYWORDS:
        if keyword.lower() in text_lower:
            return True # found the keyword
    return False


def scan_pdf(file_path):
    try:
        doc = pymupdf.open(file_path)
        # print(f"file: {file_path}")
        full_text = ""
        for page in doc:
            text = page.get_text()
            # print(text)
            if contains_keyword(text):
                return True # return as soon as there's a match - no need to keep scanning more pages
    except Exception as e:
        print(f"error reading {file_path}: {e}")
        return False

def main():
    # print("Hello World")
    matches = []
    counter = 0
    for dir_path, _, file_names in os.walk(ROOT_DIR):
        for file_name in file_names:
            # print(f"scanning {file_name}")
            if file_name.lower().endswith(".pdf"):
                full_path = os.path.join(dir_path, file_name)
                # print(full_path)
                if scan_pdf(full_path):
                    matches.append(full_path)
                    print(f"[MATCH] {full_path}")
                counter += 1
    print("counter:", counter)

    with open("matches.txt", "w") as matches_file:
        for path in matches:
            matches_file.write(path + "\n")

    print(f"Done. {len(matches)} matches")


if __name__ == "__main__":
    main()
