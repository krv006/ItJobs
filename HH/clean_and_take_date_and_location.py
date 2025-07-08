import re
from datetime import datetime


def extract_date(text):
    date_pattern = r"(\d{1,2} \w+ \d{4}|[A-Za-z]+ \d{1,2}, \d{4})"
    date_match = re.search(date_pattern, text)
    if date_match:
        raw_date = date_match.group(1)
        print(f"Raw date matched: {raw_date}")

        try:
            if ',' in raw_date:
                date_obj = datetime.strptime(raw_date, "%B %d, %Y")
            else:
                date_obj = datetime.strptime(raw_date, "%d %B %Y")

            formatted_date = date_obj.strftime("%m/%d/%Y")
            print(f"Formatted date: {formatted_date}")
            return formatted_date
        except ValueError as e:
            print(f"Error formatting date: {e}")
            return 'N/A'

    print("No date match found.")
    return 'N/A'
