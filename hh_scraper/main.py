# --- from Extract_jobs.py ---
import random
import time

from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import processing as proc
from scraper import xpathes as sel


class GhhScraper:
    def __init__(self, driver, wait, limit=None):
        self.driver = driver
        self.wait = wait
        self.limit = limit
        self.results = {
            "ID": [], "Posted_date": [], "Job_Title": [], "Company": [],
            "Company_Logo_URL": [], "Location": [], "Skills": [], "Salary_Info": []
        }
        self.technical_skills_list = [
            ".NET", "SQL", "Python", "Java", "C++", "JavaScript", "React",
            "Angular", "Vue.js", "Node.js", "Docker", "Kubernetes",
            "AWS", "Azure", "GCP", "Terraform", "Git"
        ]

    def scrape(self):
        page_num = 0
        jobs_processed_count = 0

        while True:
            if self.limit is not None and jobs_processed_count >= self.limit:
                print(f"\n--- Reached scrape limit of {self.limit} jobs. ---")
                break

            paginated_url = config.BASE_URL.format(page_num=page_num)
            print(f"\n--- Navigating to page {page_num} ---")
            self.driver.get(paginated_url)

            try:
                self.wait.until(EC.presence_of_element_located((By.XPATH, sel.job_list_urls_xpath)))
                time.sleep(random.uniform(2, 4))
                job_elements = self.driver.find_elements(By.XPATH, sel.job_list_urls_xpath)

                if not job_elements:
                    print("No more job listings found. Ending scrape.")
                    break

                job_links = []
                for el in job_elements:
                    href = el.get_attribute('href')
                    if href and '/vacancy/' in href:
                        job_id = href.split('/vacancy/')[1].split('?')[0]
                        job_links.append({'url': href, 'id': job_id})

                main_window = self.driver.current_window_handle
                for job_info in job_links:
                    if self.limit is not None and jobs_processed_count >= self.limit:
                        break

                    jobs_processed_count += 1
                    print(f"\nProcessing Job #{jobs_processed_count} | ID: {job_info['id']}")

                    self.driver.execute_script("window.open(arguments[0], '_blank');", job_info['url'])
                    self.driver.switch_to.window(self.driver.window_handles[-1])

                    try:
                        self.wait.until(EC.presence_of_element_located((By.XPATH, sel.job_title_xpath)))
                        time.sleep(random.uniform(1, 2))
                        self._extract_job_details(job_info['id'])
                    except (TimeoutException, WebDriverException) as e:
                        print(f"  ❌ Error loading job detail page. Skipping. Error: {e}")
                    finally:
                        self.driver.close()
                        self.driver.switch_to.window(main_window)

                page_num += 1

            except NoSuchElementException:
                print("\n--- No 'Next' button found. Reached the end of search results. ---")
                break
            except TimeoutException:
                print(f"Timed out waiting for job listings on page {page_num}. Ending scrape.")
                break

        print(f"\n--- Scraping finished. Total jobs processed: {jobs_processed_count} ---")

        self.save_to_csv()
        return self.results

    def _extract_job_details(self, job_id):
        self.results["ID"].append(job_id)

        company_raw = self._get_text(sel.company_name_xpath)
        self.results["Company"].append(proc.transliterate_company_name(company_raw))

        job_title_raw = self._get_text(sel.job_title_xpath)
        self.results["Job_Title"].append(proc.translate_to_english(job_title_raw))

        location_date_text = self._get_text(sel.location_and_date_xpath)
        self.results["Posted_date"].append(proc.parse_posted_date(location_date_text))

        raw_location = proc.extract_location_from_text(location_date_text)
        self.results["Location"].append(proc.identify_region(raw_location))

        skills_text = self._get_text(sel.skills_xpath)
        self.results["Skills"].append(proc.extract_skills(skills_text, self.technical_skills_list))

        salary_text = self._get_text(sel.salary_info_xpath)
        self.results["Salary_Info"].append(proc.extract_salary(salary_text))

        logo_url = self._get_attribute(sel.company_logo_url_xpath, 'src')
        self.results["Company_Logo_URL"].append(logo_url)

    def _get_text(self, xpath):
        try:
            element = self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            if element:
                return element.text.strip()
        except:
            pass
        return "N/A"

    def _get_attribute(self, xpath, attribute):
        try:
            element = self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            if element:
                return element.get_attribute(attribute)
        except:
            pass
        return "N/A"

    def save_to_csv(self):
        print("\n--- Saving scraped data to CSV ---")
        df = pd.DataFrame(self.results)
        folder = 'Data'
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, 'job_data_raw.csv')
        df.to_csv(path, index=False, encoding='utf-8')
        print(f"✅ Saved {len(df)} rows to '{path}'")

    def get_all_data(self):
        return self.results


# --- from Jobs_to_scrape.py ---
job_titles = [
    # 'Backend developer' 
    # ,'Frontend developer'
    # ,'Data analyst'
    # ,'Data engineer'
    # ,'Data scientist'
    # ,'AI engineer'
    # ,'Android developer'
    # ,'IOS developer'
    # ,'Game developer'
    # ,'DevOps engineer'
    # ,'IT project manager'
    # ,'Network engineer'
    # ,'Cybersecurity Analyst'
    # ,
    "'Cloud Architect'"
    # ,'Full stack developer'
]

# --- from salary_identify.py ---
import re


def extract_salary(salary_text, usd_to_uzs=13000, rub_to_uzs=150):
    """
    Extracts and processes salary information from a given text.
    
    Args:
        salary_text (str): The raw salary text.
        usd_to_uzs (float): Conversion rate from USD to Uzbek sum.
        rub_to_uzs (float): Conversion rate from RUB to Uzbek sum.
    
    Returns:
        int or str: The salary in Uzbek sum, or "N/A" if no valid salary is found.
    """
    # Expanded regex patterns to include UZS
    range_pattern = r"(от|from)\s*([\d\s]*)\s*(до|to)\s*([\d\s]+)\s*(so'm|сум|₽|[a-zA-Z$]+|UZS)"
    single_amount_pattern = r"([\d\s]+)\s*(so'm|сум|₽|[a-zA-Z$]+|UZS)"

    # Clean up the input text
    salary_text = salary_text.replace(",", "").strip()

    print(f"Processing text: {salary_text}")  # Debug output

    # Handle "None" in the salary text and treat it as missing value
    if "None" in salary_text:
        salary_text = salary_text.replace("None", "").strip()

    # Check for range pattern
    match = re.search(range_pattern, salary_text)
    if match:
        min_salary = match.group(2).replace(" ", "")
        max_salary = match.group(4).replace(" ", "")
        currency = match.group(5).strip().lower()

        # Handle missing values
        if not min_salary and max_salary:
            min_salary = max_salary
        if not max_salary and min_salary:
            max_salary = min_salary

        if not min_salary or not max_salary:
            return "N/A"

        try:
            min_salary = int(min_salary)
            max_salary = int(max_salary)
        except ValueError:
            return "N/A"

        median_salary = (min_salary + max_salary) // 2
        print(
            f"Range detected: min={min_salary}, max={max_salary}, median={median_salary}, currency={currency}")  # Debug output
    else:
        # Check for single amount pattern
        match = re.search(single_amount_pattern, salary_text)
        if match:
            salary_value = match.group(1).replace(" ", "")
            currency = match.group(2).strip().lower()

            if not salary_value:
                return "N/A"
            try:
                median_salary = int(salary_value)
            except ValueError:
                return "N/A"
            print(f"Single amount detected: salary={median_salary}, currency={currency}")  # Debug output
        else:
            return "N/A"

    # Convert to Uzbek sum if necessary
    if "so'm" in currency or "сум" in currency or "uzs" in currency:
        print(f"Salary is already in UZS: {median_salary}")
        return median_salary
    elif "$" in currency or "usd" in currency:
        uzs_salary = int(median_salary * usd_to_uzs)
        print(f"Converted USD to UZS: {uzs_salary}")
        return uzs_salary
    elif "rub" in currency or "₽" in currency:
        uzs_salary = int(median_salary * rub_to_uzs)
        print(f"Converted RUB to UZS: {uzs_salary}")
        return uzs_salary
    else:
        print(f"Unsupported currency: {currency}")
        return "N/A"


# Test cases
print(extract_salary("None UZS to 20800000 UZS"))  # ✅ Должно вернуть 20800000
print(extract_salary("from 800 to 2 000 $ after taxes"))  # ✅ Конвертация в UZS
print(extract_salary("from 10 000 000 to 25 000 000 so'm after taxes"))  # ✅ В суммах
print(extract_salary("2 000 $ before tax"))  # ✅ Конвертация из USD
print(extract_salary("15 000 ₽ after taxes"))  # ✅ Конвертация из RUB
print(extract_salary("до 1 000 $ до вычета налогов"))  # ✅ Конвертация из USD (только max)
print(extract_salary("от 10 000 000 до 20 000 000 so'm до вычета налогов"))  # ✅ В суммах
print(extract_salary("от 3 000 000 до 5 000 000 so'm на руки"))  # ✅ В суммах

# --- from main.py ---
# main.py
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

# Import from our refactored modules
import config
from scraper.scraper import GhhScraper
from utils.tools import ai_processing
import database


def clean_and_prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    """Cleans the DataFrame after AI processing."""
    print("\n--- Starting final data cleaning ---")

    initial_rows = len(df)
    df_cleaned = df[df['Job_Title_from_List'].isin(config.VALID_JOB_TITLES) & (df['Job_Title_from_List'] != 'unknown')]
    print(f"Filtered by valid AI titles: {initial_rows} -> {len(df_cleaned)} rows.")

    initial_rows = len(df_cleaned)
    df_cleaned = df_cleaned.dropna(subset=['ID', 'Job_Title', 'Company', 'Posted_date'])
    print(f"Dropped rows with missing critical info: {initial_rows} -> {len(df_cleaned)} rows.")

    initial_rows = len(df_cleaned)
    df_cleaned = df_cleaned.drop_duplicates(subset=['Company', 'Job_Title', 'Location'], keep='first')
    print(f"Dropped duplicate listings: {initial_rows} -> {len(df_cleaned)} rows.")

    db_columns = [
        'ID', 'Posted_date', 'Job_Title_from_List', 'Job_Title', 'Company',
        'Company_Logo_URL', 'Country', 'Location', 'Skills', 'Salary_Info', 'Source'
    ]
    final_df = df_cleaned.reindex(columns=db_columns, fill_value='N/A')

    return final_df


def main():
    """Main function to orchestrate the scraping and data processing pipeline."""
    print("--- Starting Job Scraper ---")
    if config.SCRAPE_LIMIT:
        print(f"⚠️ Running in test mode. Scrape limit is set to {config.SCRAPE_LIMIT} jobs.")

    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 10)

    try:
        # --- 2. SCRAPE DATA ---
        scraper = GhhScraper(driver, wait, limit=config.SCRAPE_LIMIT)
        scraped_data = scraper.scrape()

        if not scraped_data or 'ID' not in scraped_data or not scraped_data['ID']:
            print("Scraping returned no data. Exiting.")
            return

        df_raw = pd.DataFrame(scraped_data)

        # Save raw data
        data_folder = 'Data'
        os.makedirs(data_folder, exist_ok=True)
        raw_file_path = os.path.join(data_folder, 'job_data_raw.csv')
        df_raw.to_csv(raw_file_path, index=False, encoding='utf-8')
        print(f"\nRaw data with {len(df_raw)} rows saved to '{raw_file_path}'")

        # --- 3. AI PROCESSING ---
        titles_to_identify = df_raw['Job_Title'].tolist()
        skills_to_identify = df_raw['Skills'].tolist()

        identified_titles = ai_processing.identify_job_titles(titles_to_identify, skills_to_identify)
        if len(identified_titles) != len(df_raw):
            print("❌ AI returned mismatched title count. Exiting.")
            return

        df_raw['Job_Title_from_List'] = identified_titles
        df_raw['Country'] = "Uzbekistan"
        df_raw['Source'] = "hh.uz"

        # --- 4. CLEAN AND SAVE FINAL DATA ---
        df_cleaned = clean_and_prepare_data(df_raw)

        cleaned_file_path = os.path.join(data_folder, 'job_data_cleaned.csv')
        df_cleaned.to_csv(cleaned_file_path, index=False, encoding='utf-8')
        print(f"✅ Cleaned data with {len(df_cleaned)} rows saved to '{cleaned_file_path}'")

        # --- 5. PUSH TO DATABASE ---
        database.insert_to_sql(df_cleaned, config.DB_CONFIG)

    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()
        print("\n--- Process complete. Browser closed. ---")


if __name__ == "__main__":
    main()
