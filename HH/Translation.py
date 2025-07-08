import re
import time

from deep_translator import GoogleTranslator


def split_text(text, max_length=5000):
    sentences = re.split(r'(?<=[.?!])\s+', text)
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
    try:
        if not text or not text.strip():
            return "N/A"

        cleaned_text = re.sub(r'[^\w\s.,/-]', '', text)
        text_chunks = split_text(cleaned_text)

        translated_chunks = []
        for chunk in text_chunks:
            for attempt in range(max_retries):
                try:
                    translated = GoogleTranslator(source='auto', target='en').translate(chunk)
                    if translated:
                        translated_chunks.append(translated.strip('"'))
                        break
                except Exception as e:
                    print(f"Error during translation (Attempt {attempt + 1}): {e}")
                    time.sleep(2 ** attempt)

        return " ".join(translated_chunks) if translated_chunks else "Translation Failed"

    except Exception as e:
        print(f"Unexpected error during translation: {e}")
        return "Translation Failed"
