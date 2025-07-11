# --- from clean_and_take_date_and_location.py ---
from datetime import datetime
import re

def extract_date(text):
    # Regular expression to capture any date-like pattern (e.g., 6 January 2025 or January 6, 2025)
    date_pattern = r"(\d{1,2} \w+ \d{4}|[A-Za-z]+ \d{1,2}, \d{4})"  # Matches "6 January 2025" or "January 6, 2025"
    
    # Try to find the first date match in the text
    date_match = re.search(date_pattern, text)
    if date_match:
        raw_date = date_match.group(1)
        print(f"Raw date matched: {raw_date}")  # Debug: print the matched raw date
        
        try:
            # Handle both possible date formats (e.g., "6 January 2025" and "January 6, 2025")
            if ',' in raw_date:  # If the format is "January 6, 2025"
                date_obj = datetime.strptime(raw_date, "%B %d, %Y")
            else:  # If the format is "6 January 2025"
                date_obj = datetime.strptime(raw_date, "%d %B %Y")
            
            # Format the date into MM/DD/YYYY (month/day/year)
            formatted_date = date_obj.strftime("%m/%d/%Y")
            print(f"Formatted date: {formatted_date}")  # Debug: print formatted date
            return formatted_date
        except ValueError as e:
            print(f"Error formatting date: {e}")  # Debug: print the error if occurs
            return 'N/A'
    
    # If no date is found, return 'N/A'
    print("No date match found.")  # Debug: print if no match is found
    return 'N/A'

# Test the function with the specific case
# test_text = "Vacancy posted on January 6, 2025 in Tashkent"
# date = extract_date(test_text)
# print(f"Post Date: {date}")  # Output the result


# --- from clean_company_name.py ---
from transliterate import translit
import re

def transliterate_company_name(company_name):
    """
    Transliterates a Russian company name into Latin script and removes common business suffixes.
    
    :param company_name: str - The original company name in Russian
    :return: str - The cleaned and transliterated company name
    """

    # Remove common Russian business entity types
    business_suffixes = ["ООО", "АО", "ИП", "ЗАО", "ПАО", "ОАО"]
    
    # Remove suffixes from the company name
    for suffix in business_suffixes:
        company_name = company_name.replace(suffix, "").strip()

    # Transliterate to Latin script
    transliterated_name = translit(company_name, 'ru', reversed=True)

    # Remove any extra unwanted symbols or spaces
    transliterated_name = re.sub(r'\s+', ' ', transliterated_name).strip()

    return transliterated_name

# # Example Usage
# company1 = "ООО Асакабанк"
# company2 = "АО Коррекционный фитнес"
# company3 = "ИП Иванов и Ко"

# print(transliterate_company_name(company1))  # Output: Asakabank
# print(transliterate_company_name(company2))  # Output: Korrektsionnyy fitnes
# print(transliterate_company_name(company3))  # Output: Ivanov i Ko
# print(transliterate_company_name("ООО AMERIKA TEXNOLOGIYALAR UNIVERSITETI"))
# print(transliterate_company_name("ООО AKFA BUILDING MATERIALS. Производство"))
# # Output: Microsoft Corporation (unchanged)


# --- from clean_the_skills.py ---
import os
import pandas as pd

def clean_hard_skills(csv_file, column_name="Hard Skills", unwanted_skills=["Project", "Office"]):
    """
    Cleans the hard_skills column by removing unwanted skills and replacing empty values with 'N/A'.
    
    Parameters:
        csv_file (str): Path to the CSV file.
        column_name (str): The name of the column to clean.
        unwanted_skills (list): List of skills to remove.
    
    Returns:
        pd.DataFrame: Cleaned DataFrame.
    """
    # Load CSV file
    df = pd.read_csv(csv_file)
    
    def clean_skills(skills):
        if pd.isna(skills) or skills.strip() == "":
            return "N/A"
        # Split skills, remove unwanted ones, and rejoin
        cleaned_skills = [skill.strip() for skill in skills.split(",") if skill.strip() not in unwanted_skills]
        return ", ".join(cleaned_skills) if cleaned_skills else "N/A"

    # Apply cleaning function
    df[column_name] = df[column_name].apply(clean_skills)

    # Ensure directory exists before saving the cleaned file
    cleaned_file_path = os.path.join(os.path.dirname(csv_file), "cleaned_" + os.path.basename(csv_file))
    
    df.to_csv(cleaned_file_path, index=False)
    
    print(f"✅ Data cleaning complete! Saved as '{cleaned_file_path}'")
    return df

# Example Usage
cleaned_df = clean_hard_skills(r"Data\job_data.csv")


