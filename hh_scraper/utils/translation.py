# --- from Translation.py ---
from deep_translator import GoogleTranslator
import re
import time

def split_text(text, max_length=5000):
    """Splits long text into smaller chunks within the API's character limit."""
    sentences = re.split(r'(?<=[.?!])\s+', text)  # Split by sentence boundaries
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) < max_length:
            current_chunk += sentence + " "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + " "

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

def translate_to_english(text, max_retries=3):
    """Cleans text and translates it to English, handling long texts and errors."""
    try:
        if not text or not text.strip():
            return "N/A"

        # Preprocess text: Remove unwanted characters but keep spaces, commas, periods
        cleaned_text = re.sub(r'[^\w\s.,/-]', '', text)

        # Split long text into chunks
        text_chunks = split_text(cleaned_text)

        translated_chunks = []
        for chunk in text_chunks:
            for attempt in range(max_retries):
                try:
                    translated = GoogleTranslator(source='auto', target='en').translate(chunk)
                    if translated:
                        translated_chunks.append(translated.strip('"'))
                        break  # Exit retry loop if successful
                except Exception as e:
                    print(f"Error during translation (Attempt {attempt+1}): {e}")
                    time.sleep(2 ** attempt)  # Exponential backoff

        # Return full translated text
        return " ".join(translated_chunks) if translated_chunks else "Translation Failed"

    except Exception as e:
        print(f"Unexpected error during translation: {e}")
        return "Translation Failed"

# # Example long job description
# job_text = """
# Строительная компания приглашает в свою команду 2D/Графического дизайнера
# Обязанности:
# работа с изображениями, текстами, интерфейсами, композицией, а также визуализацией и анимацией...
# """

# translated_text = translate_to_english(job_text)
# print("Translated Text:", translated_text)


