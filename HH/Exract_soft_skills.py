import re
import time

import google.generativeai as genai

API_KEY = "AIzaSyDAhcvX5-iAwOk8XQXZKFQdcQVszvwnTXI"
genai.configure(api_key=API_KEY)


def clean_soft_skills(text):
    if not text or text.strip() == "":
        return "N/A"

    cleaned_text = re.sub(r'[\n\r]+', ', ', text.strip())

    return cleaned_text


def extract_soft_skills(text, max_retries=3):
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

            return clean_soft_skills(result) if result else "N/A"

        except Exception as e:
            print(f"Error during API request (Attempt {attempt + 1}/{max_retries}): {e}")
            time.sleep(2 ** attempt)
    print("Max retries reached. Returning 'N/A'.")
    return "N/A"
