# processing.py
import re
from datetime import datetime
from transliterate import translit
from deep_translator import GoogleTranslator
import time

# --- COMPANY NAME CLEANING ---
def transliterate_company_name(company_name: str) -> str:
    """Transliterates a Russian company name and removes common business suffixes."""
    suffixes = ["ООО", "АО", "ИП", "ЗАО", "ПАО", "ОАО"]
    for suffix in suffixes:
        company_name = company_name.replace(suffix, "").strip()
    transliterated_name = translit(company_name, 'ru', reversed=True)
    return re.sub(r'\s+', ' ', transliterated_name).strip()

# --- DATE & LOCATION EXTRACTION ---
def extract_date(text: str) -> str:
    """Extracts a date and formats it to MM/DD/YYYY."""
    date_pattern = r"(\d{1,2} \w+ \d{4}|[A-Za-z]+ \d{1,2}, \d{4})"
    match = re.search(date_pattern, text)
    if not match:
        return 'N/A'
    try:
        raw_date = match.group(1)
        date_format = "%B %d, %Y" if ',' in raw_date else "%d %B %Y"
        date_obj = datetime.strptime(raw_date, date_format)
        return date_obj.strftime("%m/%d/%Y")
    except (ValueError, IndexError):
        return 'N/A'

def extract_location_from_text(text: str) -> str:
    """Extracts the city/location from the 'posted in' text."""
    location_pattern = r"\b(?:в|in|da)\s+([a-zA-Zа-яА-ЯёЁўқғҳʼ\- ]+)\b"
    match = re.search(location_pattern, text, re.IGNORECASE)
    return match.group(1).strip() if match else "Tashkent" # Default to Tashkent

def identify_region(name: str) -> str:
    """Identifies the region based on a city name. (Simplified for brevity)"""
    regions_districts = {"Andijan": ["Andijon", "Asaka"], "Bukhara": ["Bukhara", "Gijduvon"], "Fergana": ["Fergana", "Kokand"], "Tashkent": ["Tashkent", "Chilonzor", "Yunusobod"]} # Add more as needed
    name_lower = name.strip().lower()
    for region, districts in regions_districts.items():
        if name_lower == region.lower() or name_lower in [d.lower() for d in districts]:
            return region
    return "Tashkent"

# --- SALARY PROCESSING ---
def extract_salary(salary_text: str, usd_to_uzs=13000, rub_to_uzs=150) -> str:
    """Extracts and standardizes salary to UZS."""
    salary_text = salary_text.replace(",", "").replace(" ", "").lower()
    
    # Pattern for ranges like "from...to" or "от...до"
    range_match = re.search(r'(?:from|от)(\d+)(?:to|до)(\d+)', salary_text)
    if range_match:
        min_salary = int(range_match.group(1))
        max_salary = int(range_match.group(2))
        median_salary = (min_salary + max_salary) // 2
    else: # Pattern for single amounts
        single_match = re.search(r'(\d+)', salary_text)
        if not single_match: return "N/A"
        median_salary = int(single_match.group(1))

    if "$" in salary_text:
        return str(int(median_salary * usd_to_uzs))
    if "₽" in salary_text or "rub" in salary_text:
        return str(int(median_salary * rub_to_uzs))
    if "so'm" in salary_text or "сум" in salary_text:
        return str(median_salary)
    return "N/A" # Default if currency not identified

# --- SKILL EXTRACTION ---
def extract_skills(text: str, skills_list: list) -> str:
    """Extracts predefined skills from text."""
    if not isinstance(text, str): return "N/A"
    found_skills = set()
    text_lower = text.lower()
    for skill in skills_list:
        pattern = re.compile(rf'\b{re.escape(skill.lower())}\b')
        if pattern.search(text_lower):
            found_skills.add(skill)
    return ", ".join(sorted(found_skills)) if found_skills else "N/A"

# --- TEXT TRANSLATION ---
def translate_to_english(text: str, max_retries=3) -> str:
    """Translates text to English, with retry logic."""
    if not text or not text.strip() or text == 'N/A':
        return "N/A"
    for attempt in range(max_retries):
        try:
            # Clean non-essential characters before translation
            cleaned_text = re.sub(r'[^\w\s.,/-]', '', text)
            translated = GoogleTranslator(source='auto', target='en').translate(cleaned_text)
            return translated.strip('"') if translated else "Translation Failed"
        except Exception as e:
            print(f"  - Translation error (Attempt {attempt+1}): {e}")
            time.sleep(1)
    return "Translation Failed"