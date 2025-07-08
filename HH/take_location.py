import re


def extract_location(text):
    location_pattern = r"\b(?:в|in|da)\s+([a-zA-Zа-яА-ЯёЁўқғҳʼ\- ]+)\b"

    location_match = re.search(location_pattern, text, re.IGNORECASE)
    if location_match:
        location = location_match.group(1).strip()
        print(f"Extracted location: {location}")
        return location

    print("No location found.")
    return "N/A"


test_cases = [
    "Вакансия опубликована 3 января 2025 в Ханабаде",
    "The job was posted on January 6, 2025 in Tashkent",
    "Ish o‘rni 2025-yil 3-yanvarda Xonobodda eʼlon qilindi",
]

for text in test_cases:
    location = extract_location(text)
    print(f"Text: {text}\nLocation: {location}\n")
