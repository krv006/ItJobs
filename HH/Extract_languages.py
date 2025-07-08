import re

LANGUAGES = ["English", "Russian", "Uzbek", "French", "German", "Spanish", "Chinese",
             "Japanese", "Italian", "Korean", "Portuguese", "Arabic", "Turkish", "Hindi"]

LEVEL_PATTERN = r"(?:A1|A2|B1|B2|C1|C2|Fluent|Native|Proficient)"

EXCLUSION_PATTERN = r"\bUzbekistan\b|\bRepublic of Uzbekistan\b"


def extract_languages_with_levels(text):
    extracted = []
    found_languages = set()

    text = re.sub(EXCLUSION_PATTERN, "", text, flags=re.IGNORECASE)

    for lang in LANGUAGES:
        matches = re.findall(rf"\b{lang}\b(?:\s*[-—:,\s]?\s*({LEVEL_PATTERN}))?", text, re.IGNORECASE)

        for match in matches:
            language = lang
            level = match.upper() if match else ""

            formatted = f"{language} {level}".strip()
            if formatted not in found_languages:
                extracted.append(formatted)
                found_languages.add(formatted)

    if not found_languages and re.search(LEVEL_PATTERN, text, re.IGNORECASE):
        extracted.append("N/A")

    if not extracted:
        extracted.append("N/A")

    return ", ".join(extracted)
