import re


def extract_salary(salary_text, usd_to_uzs=13000, rub_to_uzs=150):
    range_pattern = r"(от|from)\s*([\d\s]*)\s*(до|to)\s*([\d\s]+)\s*(so'm|сум|₽|[a-zA-Z$]+)"
    single_amount_pattern = r"([\d\s]+)\s*(so'm|сум|₽|[a-zA-Z$]+)"

    salary_text = salary_text.replace(",", "").strip()

    print(f"Processing text: {salary_text}")

    if "None" in salary_text:
        salary_text = salary_text.replace("None", "").strip()

    match = re.search(range_pattern, salary_text)
    if match:
        min_salary = match.group(2)
        max_salary = match.group(4)
        currency = match.group(5).strip().lower()

        if not min_salary:
            min_salary = max_salary
        elif not max_salary:
            max_salary = min_salary
        min_salary = min_salary.replace(" ", "")
        max_salary = max_salary.replace(" ", "")

        if not min_salary or not max_salary:
            return "N/A"

        min_salary = int(min_salary)
        max_salary = int(max_salary)

        median_salary = (min_salary + max_salary) // 2
        print(
            f"Range detected: min={min_salary}, max={max_salary}, median={median_salary}, currency={currency}")
    else:
        match = re.search(single_amount_pattern, salary_text)
        if match:
            salary_value = match.group(1).replace(" ", "")
            currency = match.group(2).strip().lower()
            if not salary_value:
                return "N/A"
            median_salary = int(salary_value)
            print(f"Single amount detected: salary={median_salary}, currency={currency}")
        else:
            return "N/A"
    if "so'm" in currency or "сум" in currency:
        print(f"Salary is already in UZS: {median_salary}")
        return median_salary
    elif "$" in currency:
        # Convert USD to UZS
        uzs_salary = int(median_salary * usd_to_uzs)
        print(f"Converted USD to UZS: {uzs_salary}")
        return uzs_salary
    elif "rub" in currency or "₽" in currency:
        # Convert RUB to UZS
        uzs_salary = int(median_salary * rub_to_uzs)
        print(f"Converted RUB to UZS: {uzs_salary}")
        return uzs_salary
    else:
        print(f"Unsupported currency: {currency}")
        return "N/A"  # Unsupported currency


# Test with the "None UZS to 20800000 UZS" example
print(extract_salary("None UZS to 20800000 UZS"))

# Example Tests
print(extract_salary("from 800 to 2 000 $ after taxes"))  # Should convert to UZS
print(extract_salary("from 10 000 000 to 25 000 000 so'm after taxes"))  # Already in UZS
print(extract_salary("2 000 $ before tax"))  # Single amount in USD
print(extract_salary("15 000 ₽ after taxes"))  # Single amount in RUB
print(extract_salary("до 1 000 $ до вычета налогов"))  # Russian example with USD
print(extract_salary("от 10 000 000 до 20 000 000 so'm до вычета налогов"))  # Russian example with UZS
print(extract_salary("от 3 000 000 до 5 000 000 so'm на руки"))  # Should be in UZS
