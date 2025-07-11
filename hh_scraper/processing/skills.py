# --- from Exract_soft_skills.py ---
import google.generativeai as genai
import time
import re

# Set up Google AI API Key
API_KEY = "AIzaSyDAhcvX5-iAwOk8XQXZKFQdcQVszvwnTXI"
genai.configure(api_key=API_KEY)

def clean_soft_skills(text):
    """Cleans AI-generated soft skills by ensuring they are comma-separated."""
    if not text or text.strip() == "":
        return "N/A"

    # Replace newlines and extra spaces with a comma
    cleaned_text = re.sub(r'[\n\r]+', ', ', text.strip())
    
    return cleaned_text

def extract_soft_skills(text, max_retries=3):
    """Extracts the most relevant soft skills from job descriptions using AI."""
    
    prompt = (
        "You are an AI trained to analyze job descriptions and extract only the most relevant soft skills mentioned in the text. "
        "Soft skills refer to interpersonal, communication, leadership, analytical, and problem-solving abilities that contribute to job success. "
        "Your task is to carefully identify and return only the closest matching soft skills without any explanations or additional text. "
        "If no soft skills are present in the text, return 'N/A'. "
        "\n\nGuidelines:\n"
        "1. Extract and return all relevant soft skills found in the text, even if they are not predefined. Remove any unnecessary words or explanations.\n"
        "2. Categorize extracted skills under broad groups where applicable:\n"
        "   - Logical Thinking\n"
        "   - Analytical Thinking\n"
        "   - Critical Thinking\n"
        "   - Creative Thinking\n"
        "   - Problem-Solving\n"
        "   - Leadership\n"
        "   - Communication\n"
        "   - Negotiation\n"
        "   - Teamwork\n"
        "   - Adaptability\n"
        "   - Self-Motivation\n"
        "3. If a soft skill is found that does not match any predefined category, return it as is.\n"
        "4. Ensure the output is a comma-separated list of skills without any explanations.\n"
        "5. If the provided text contains no relevant soft skills, return only 'N/A'.\n"
        "\nExample:\n"
        "Input: 'We need a candidate with problem-solving, leadership, adaptability, teamwork, and emotional intelligence.'\n"
        "Output: Problem-Solving, Leadership, Adaptability, Teamwork, Emotional Intelligence\n"
        "\nInput: 'Only technical skills like production management, budgeting, logistics are required.'\n"
        "Output: N/A\n"
        "\nNow, analyze this text and return only soft skills mentioned, separated by commas: " + text
    )

    model = genai.GenerativeModel("gemini-1.5-flash")

    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            result = response.text.strip()
            
            # Ensure the output is comma-separated
            return clean_soft_skills(result) if result else "N/A"
        
        except Exception as e:
            print(f"Error during API request (Attempt {attempt+1}/{max_retries}): {e}")
            time.sleep(2 ** attempt)  # Exponential backoff

    print("Max retries reached. Returning 'N/A'.")
    return "N/A"

# # Example job description
# job_description = """
# The candidate must have strong leadership, decision-making, and problem-solving skills. 
# They should be highly adaptable and have excellent communication abilities.
# """

# # Extract soft skills using AI
# soft_skills = extract_soft_skills(job_description)
# print("Extracted Soft Skills:", soft_skills)


# --- from Extract_languages.py ---
import re

# Common languages in job postings
LANGUAGES = ["English", "Russian", "Uzbek", "French", "German", "Spanish", "Chinese",
             "Japanese", "Italian", "Korean", "Portuguese", "Arabic", "Turkish", "Hindi"]

# Proficiency level pattern
LEVEL_PATTERN = r"(?:A1|A2|B1|B2|C1|C2|Fluent|Native|Proficient)"

# Exclusion pattern to prevent false detection of "Uzbekistan"
EXCLUSION_PATTERN = r"\bUzbekistan\b|\bRepublic of Uzbekistan\b"

def extract_languages_with_levels(text):
    """Extracts languages and their proficiency levels from a job posting text."""

    extracted = []
    found_languages = set()

    # Remove "Uzbekistan" or similar country mentions
    text = re.sub(EXCLUSION_PATTERN, "", text, flags=re.IGNORECASE)

    for lang in LANGUAGES:
        # Ensure we correctly extract proficiency levels linked to a language
        matches = re.findall(rf"\b{lang}\b(?:\s*[-—:,\s]?\s*({LEVEL_PATTERN}))?", text, re.IGNORECASE)

        for match in matches:
            language = lang
            level = match.upper() if match else ""  # Convert level to uppercase

            # Ensure level is added only once per language
            formatted = f"{language} {level}".strip()
            if formatted not in found_languages:
                extracted.append(formatted)
                found_languages.add(formatted)

    # If no language is found but a level exists, return "N/A"
    if not found_languages and re.search(LEVEL_PATTERN, text, re.IGNORECASE):
        extracted.append("N/A")

    # If no language or level is found, return "N/A"
    if not extracted:
        extracted.append("N/A")

    return ", ".join(extracted)

# --- from Extract_skills.py ---
import re
from  Skills_mapping import tools_list
def extract_skills(text, skills_list = tools_list):
    if not isinstance(text, str):  # Handle non-string inputs
        return "N/A"

    text = text.lower().strip()  # Normalize input text
    found_skills = set()  # Use a set to store unique matches

    # Sort skills by length first to ensure "PHP7" is matched before "PHP"
    sorted_skills = sorted(skills_list, key=len, reverse=True)

    for skill in sorted_skills:
        # Use regex to match standalone words or exact multi-word skills
        pattern = re.compile(rf'(?<!\w){re.escape(skill.lower())}(?!\w)')
        if pattern.search(text):
            found_skills.add(skill)

    return ", ".join(sorted(found_skills)) if found_skills else "N/A"


# --- from Take_technical_skills.py ---
import pandas as pd
from Extract_skills import extract_skills

# Read the CSV file
df = pd.read_csv("cleaned_job_titles.csv",keep_default_na=False, encoding='utf-8')

# Apply the extract_skills function to each row of the Skills column
df['Skills'] = df['Skills'].apply(
    lambda x: extract_skills(x) if isinstance(x, str) and x.strip() else "N/A"
)

# Save the updated DataFrame back to a new CSV (optional)
df.to_csv("updated_job_titles.csv", index=False)

print("Skills column updated successfully!")


