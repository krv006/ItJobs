# --- START OF FILE Extract_jobs.py (Complete & Corrected) ---

import random
import time

from selenium.common import TimeoutException, WebDriverException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from Extract_skills import extract_skills
from Location_by_region import identify_region
from Translation import translate_to_english
# This line imports the corrected variables from XPathes.py
from XPathes import *
from clean_and_take_date_and_location import extract_date
from clean_company_name import transliterate_company_name
from salary_identify import extract_salary
from take_location import extract_location


class Extract:
    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)
        self.company_names = []
        self.job_titles = []
        self.post_dates = []
        self.technical_skills = []
        self.salaries = []
        self.locations = []
        self.company_logo_urls = []
        self.job_ids = []

    def load_data(self):
        page_num = 0
        jobs_processed_total = 0

        while True:
            paginated_url = f"https://hh.uz/search/vacancy?area=97&enable_snippets=true&ored_clusters=true&search_period=1&text=developer&search_field=name&search_field=company_name&search_field=description&L_save_area=true&professional_role=156&professional_role=160&professional_role=10&professional_role=12&professional_role=150&professional_role=25&professional_role=165&professional_role=34&professional_role=36&professional_role=73&professional_role=155&professional_role=96&professional_role=164&professional_role=104&professional_role=157&professional_role=107&professional_role=112&professional_role=113&professional_role=148&professional_role=114&professional_role=116&professional_role=121&professional_role=124&professional_role=125&professional_role=126&page={page_num}"

            print(f"\n--- Navigating to search results page {page_num} ---")
            self.driver.get(paginated_url)

            try:
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, Urls_path))
                )

                time.sleep(random.uniform(2, 4))
                job_elements = self.driver.find_elements(By.XPATH, Urls_path)

                if not job_elements:
                    print(f"No more job listings found on page {page_num}. Ending scrape.")
                    break

                print(f"Page {page_num}: Found {len(job_elements)} job listings.")

                job_links = []
                for element in job_elements:
                    href = element.get_attribute("href")
                    if href and '/vacancy/' in href:
                        job_id = href.split('/vacancy/')[1].split('?')[0]
                        job_links.append({'url': href, 'id': job_id})

                main_window = self.driver.current_window_handle

                for i, job_info in enumerate(job_links, 1):
                    jobs_processed_total += 1
                    print(f"\nProcessing Job {jobs_processed_total} (Page {page_num}, Item {i}) | ID: {job_info['id']}")

                    self.driver.execute_script("window.open(arguments[0], '_blank');", job_info['url'])
                    self.driver.switch_to.window(self.driver.window_handles[-1])

                    try:
                        WebDriverWait(self.driver, 25).until(EC.presence_of_element_located((By.XPATH, Job_title_path)))
                        time.sleep(random.uniform(1, 3))

                        # ✅ FIXED: Correct method name
                        self.__extract_data(job_info['id'])

                    except (TimeoutException, WebDriverException) as e:
                        print(f" ❌ Error loading job detail page {job_info['url']}. Skipping. Error: {e}")
                    finally:
                        self.driver.close()
                        self.driver.switch_to.window(main_window)

                    time.sleep(random.uniform(0.5, 1.5))

                try:
                    self.driver.find_element(By.XPATH, next_button_path)
                    page_num += 1
                except NoSuchElementException:
                    print("\n--- No 'Next' button found. Reached the end of search results. ---")
                    break

            except TimeoutException:
                print(f"Timed out waiting for job listings on page {page_num}. Ending scrape.")
                break
            except Exception as e:
                print(f"An unexpected error occurred on page {page_num}: {e}")
                break

        print(f"\n--- Scraping finished. Total jobs processed: {jobs_processed_total} ---")

    def __extract_data(self, job_id):
        self.job_ids.append(job_id)

        company_name_raw = self.__get_text_or_nan(company_name_path)
        company_name = transliterate_company_name(company_name_raw) if company_name_raw != 'N/A' else 'N/A'
        self.company_names.append(company_name)
        print(f" ✅ Company: {company_name}" if company_name != 'N/A' else f" ⚠️ Company not found.")

        job_title = translate_to_english(self.__get_text_or_nan(Job_title_path))
        self.job_titles.append(job_title)
        print(f" ✅ Job Title: {job_title}" if job_title != 'N/A' else f" ⚠️ Job Title not found.")

        location_date_text = self.__get_text_or_nan(location_and_posted_date_path)
        post_date = extract_date(location_date_text)
        self.post_dates.append(post_date)
        print(f" ✅ Post Date: {post_date}" if post_date != 'N/A' else f" ⚠️ Post Date not found.")

        raw_location = extract_location(location_date_text)
        location = identify_region(raw_location)
        self.locations.append(location)
        print(f" ✅ Location: {location}" if location != 'N/A' else f" ⚠️ Location not found.")

        skills_text = self.__get_text_or_nan(skills_path)
        technical_skills = extract_skills(skills_text)
        self.technical_skills.append(technical_skills)
        print(f" ✅ Skills: {technical_skills}" if technical_skills != 'N/A' else f" ⚠️ Skills not found.")

        salary_text = self.__get_text_or_nan(salary_info_path)
        salary = extract_salary(salary_text)
        self.salaries.append(salary)
        print(f" ✅ Salary: {salary}" if salary != 'N/A' else f" ⚠️ Salary not found.")

        # This now uses the correctly defined 'Company_Logo_URL_path'
        company_logo_url = self.__get_attribute_or_nan(Company_Logo_URL_path, 'src')
        self.company_logo_urls.append(company_logo_url)
        print(f" ✅ Logo URL: {company_logo_url}" if company_logo_url != 'N/A' else f" ⚠️ Logo URL not found.")

    def __get_text_or_nan(self, path):
        try:
            element = self.wait.until(EC.presence_of_element_located((By.XPATH, path)))
            text = element.text.strip()
            return text if text else "N/A"
        except:
            return "N/A"

    def __get_attribute_or_nan(self, path, attribute):
        try:
            element = self.wait.until(EC.presence_of_element_located((By.XPATH, path)))
            attr_value = element.get_attribute(attribute)
            return attr_value.strip() if attr_value else "N/A"
        except:
            return "N/A"

    def get_all_data(self):
        """Return all scraped data as a dictionary"""
        return {
            "job_ids": self.job_ids,
            "company_names": self.company_names,
            "job_titles": self.job_titles,
            "locations": self.locations,
            "post_dates": self.post_dates,
            "technical_skills": self.technical_skills,
            "salaries": self.salaries,
            "company_logo_urls": self.company_logo_urls,
        }
