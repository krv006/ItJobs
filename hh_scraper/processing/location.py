# --- from Location_by_region.py ---
def identify_region(name):
    # Data for regions and districts in English
    regions_districts_english = {
    "Andijan": [
        "Andijon", "Asaka", "Buloqboshi", "Jalolquduq", "Izboskan",
        "Qorgontepa",  # from "Qo‘rg‘ontepa"
        "Marhamat", "Oltinkol",  # from "Oltinko‘l"
        "Paxtaobod", "Shahrixon", "Ulugnor",  # from "Ulug‘nor"
        "Khojaobod",   # from "Xo‘jaobod"
        "Baliqchi"
    ],
    "Bukhara": [
        "Bukhara",     # from "Buxoro" (using the common English name)
        "Gijduvon",    # from "G‘ijduvon"
        "Jondor", "Kogon", "Olot", "Peshku",
        "Qorakol",     # from "Qorako‘l"
        "Qorovulbozor", 
        "Romitan", "Shofirkon", "Vobkent", "Bukhara", "Gijiwan"
    ],
    "Fergana": [
        "Beshariq",
        "Bogdod",      # from "Bog‘dod"
        "Buvayda",
        "Dangara",     # from "Dang‘ara"
        "Fergana",     # standardizing "Farg‘ona" to "Fergana"
        "Furqat",
        "Oltiariq",
        "Uzbekistan",  # from "O‘zbekiston" (some sources list this district as such)
        "Qoshtepa",    # from "Qo‘shtepa"
        "Rishton",
        "Sox",         # from "So‘x" (some prefer "Sokh" but here using Sox)
        "Toshloq",
        "Uchkoprik",   # from "Uchko‘prik"
        "Yozyovon", "Ferghana",
        "Kokand", "Margilan", "Kokand", "Kuva"
    ],
    "Jizzakh": [
        "Arnasoy",
        "Baxmal",
        "Dostlik",    # from "Do‘stlik"
        "Forish",
        "Gallaorol",  # from "G‘allaorol"
        "Jizzakh",    # standardized spelling for the regional center
        "Mirzachol",  # from "Mirzacho‘l"
        "Paxtakor",
        "Yangiobod",
        "Zarbdor",
        "Zafarobod",
        "Zomin", "Jizak"
    ],
    "Kashkadarya": [
        "Chiroqchi",
        "Dehqonobod",
        "Guzor",      # from "G‘uzor"
        "Kasbi",
        "Kitob",
        "Koson",
        "Mirishkor",
        "Muborak",
        "Nishon",
        "Qarshi",
        "Shahrisabz",
        "Yakkabog", "Karshi"    # from "Yakkabog‘"
    ],
    "Khorezm": [
        "Bogot",      # from "Bog‘ot"
        "Gurlan",
        "Hazorasp",
        "Shovot",
        "Urganch", "Urgench",
        "Khonqa",     # from "Xonqa" (using Kh to represent the Uzbek X)
        "Khiva",      # from "Xiva"
        "Yangibozor",
        "Yangiyariq"  # from "Yangiariq"
    ],
    "Namangan": [
        "Chortoq",
        "Chust",
        "Kosonsoy",
        "Mingbuloq",
        "Namangan",
        "Norin",
        "Pop",
        "Toraqorgon", # from "To‘raqo‘rg‘on"
        "Uchqorgon",  # from "Uchqo‘rg‘on"
        "Yangiqorgon" # from "Yangiqo‘rg‘on"
    ],
    "Navoiy": [
        "Karmana",
        "Konimex",
        "Navbahor",
        "Nurota",
        "Qiziltepa",
        "Tomdi",
        "Uchquduq",
        "Xatirchi"
    ],
    "Samarkand": [
        "Bulungur",   # from "Bulung‘ur"
        "Ishtixon",
        "Jomboy",
        "Kattaqorgon",# from "Kattaqo‘rg‘on"
        "Narpay",
        "Oqdaryo",
        "Pastdargom", # from "Pastdarg‘om"
        "Payariq",
        "Samarkand",   # from "Samarqand"
        "Toyloq",
        "Urgut"
    ],
    "Sirdarya": [
        "Boyovut",
        "Guliston",
        "Mirzaobod",
        "Sayxunobod",
        "Sirdaryo",
        "Khovos",     # from "Xovos" (using Kh for X)
        "Yangiyer",
        "Shirin"
    ],
    "Surkhandarya": [
        "Angor",
        "Bandixon",
        "Boysun",
        "Denov",
        "Jarqorgon",  # from "Jarqo‘rg‘on"
        "Muzrabot",
        "Oltinsoy",
        "Qiziriq",
        "Qumqorgon",  # from "Qumqo‘rg‘on"
        "Sariosiyo",
        "Sherobod",
        "Shorchi",    # from "Sho‘rchi"
        "Termiz", "Termez"
    ],
    "Tashkent Region": [
        "Bekobod",
        "Boka",           # from "Bo‘ka"
        "Chinoz",
        "Qibray",
        "Ohangaron",
        "Ortachirchiq",   # from "O‘rtachirchiq"
        "Parkent",
        "Piskent",
        "Quyichirchiq",
        "Yangiyol",       # from "Yangiyo‘l"
        "Yuqorichirchiq",
        "Zangiota",
        "Chirchik",
        "Akhangarang", "Angren"
    ],
    "Tashkent": [
        "Bektemir",
        "Chilonzor",
        "Yashnobod",
        "Mirobod",
        "Mirzo Ulugbek",  # from "Mirzo Ulug‘bek"
        "Olmazor",
        "Sergele",
        "Shayxontohur",
        "Uchtepa",
        "Yakkasaroy",
        "Yunusobod"
    ],
    "Karakalpakstan": [
        "Amudaryo",
        "Beruniy",
        "Chimboy",
        "Elliqala",    # from "Elliqala" (or “Ellikqal’a”)
        "Kegeyli",
        "Moynaq",      # from "Mo‘ynoq" (using a simpler form)
        "Nukus",
        "Qanlikol",    # from "Qanliko‘l"
        "Qoraozak",    # from "Qorao‘zak"
        "Shumanay",
        "Taxtakupir",  # from "Taxtako‘pir"
        "Tortkol",     # from "To‘rtko‘l"
        "Khojayli","Kungrad"     # from "Xo‘jayli"
    ]
}


    # Normalize input
    name = name.strip().lower()

    # Search in regions and districts
    for region, districts in regions_districts_english.items():
        if name == region.lower():
            return region  # Return region name
        if name in [district.lower() for district in districts]:
            return region

    # Default to Tashkent
    return "Tashkent"

# Test the function
test_cases = ["Jizzakh", "Yangiyul", "Nukus", "Nurafshon", "Ahangaran", "Chust"]

for test in test_cases:
    print(f"Input: {test} -> Output: {identify_region(test)}")


# --- from take_location.py ---
import re

def extract_location(text):
    # Regex to capture the location in Russian, English, or Uzbek text
    # Match the word "in" (English), "в" (Russian), or "da" (Uzbek) and extract the following location
    location_pattern = r"\b(?:в|in|da)\s+([a-zA-Zа-яА-ЯёЁўқғҳʼ\- ]+)\b"
    
    # Try to find the location match in the text
    location_match = re.search(location_pattern, text, re.IGNORECASE)
    if location_match:
        location = location_match.group(1).strip()
        print(f"Extracted location: {location}")  # Debug: print the extracted location
        return location

    print("No location found.")  # Debug: no match found
    return "N/A"

# Test the function with multiple examples
test_cases = [
    "Вакансия опубликована 3 января 2025 в Ханабаде",  # Russian
    "The job was posted on January 6, 2025 in Tashkent",  # English
    "Ish o‘rni 2025-yil 3-yanvarda Xonobodda eʼlon qilindi",  # Uzbek
]

# Run the function on test cases
for text in test_cases:
    location = extract_location(text)
    print(f"Text: {text}\nLocation: {location}\n")


