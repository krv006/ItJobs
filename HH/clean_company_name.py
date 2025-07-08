import re

from transliterate import translit


def transliterate_company_name(company_name):
    business_suffixes = ["ООО", "АО", "ИП", "ЗАО", "ПАО", "ОАО"]

    for suffix in business_suffixes:
        company_name = company_name.replace(suffix, "").strip()

    transliterated_name = translit(company_name, 'ru', reversed=True)

    transliterated_name = re.sub(r'\s+', ' ', transliterated_name).strip()

    return transliterated_name
