import threading
import time
from random import randint

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
from Data_time_clean import clean_and_format_first_date
from Translation import *
from selenium import webdriver
from extractskill import extract_skills
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import pandas as pd
import os
class Extract:

    # Set up WebDriver


    def __init__(self):


        self.name_companies = []
        self.job_titles = []
        self.location_jobs = []
        self.post_dates = []
        self.skills = []

    def data_scrapping(self, list_of_urls : list):

        name_companies = []
        job_titles = []
        location_jobs = []
        post_dates = []
        skills = []

        options = webdriver.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--start-maximized")
        cService = Service(executable_path=r"C:\Users\abduk\AppData\Local\Google\Chrome\User Data\Default")

        driver = webdriver.Chrome(options=options)
        wait = WebDriverWait(driver, 15)

        for url in list_of_urls:
            try:
                driver.get(url)
                time.sleep(randint(1, 5))
                self.__extract_data(driver,wait,EC,name_companies,job_titles,location_jobs,post_dates,skills)
            except:
                pass


        self.collect_into_dataframe(name_companies=name_companies,job_titles=job_titles,location_jobs=location_jobs,post_dates=post_dates,skills=skills)

    def collect_into_dataframe(self,name_companies, job_titles, location_jobs, post_dates, skills):

        print(f"name_companies: {len(name_companies)},job_titles: {len(job_titles)},location_jobs: {len(location_jobs)},post_dates: {len(post_dates)} skills: {len(skills)}")
        country_list = ["South Korea"] * len(name_companies)
        job_title_from_list = ["N/A"] * len(name_companies)
        sourses = ["saramin.co"] * len(name_companies)
        salary_list = ["N/A"] * len(name_companies)
        logo_urls = ["N/A"] * len(name_companies)
        # ID,Posted_date,Job Title from List,Job Title,Company,Company Logo URL,Country,Location,Skills,Salary Info,Source
        data = {
            "ID": range(1, len(name_companies) + 1),
            "Posted_date": post_dates,
            "Job Title from List": job_title_from_list,
            "Job Title": job_titles,
            "Company": name_companies,
            "Company Logo URL": logo_urls,
            "Country": country_list,
            "Location": location_jobs,
            "Skills": skills,
            "Salary Info": salary_list,
            "Source": sourses,
        }

        # Convert the dictionary into a DataFrame
        df = pd.DataFrame(data)
        file_name_skills = f"{randint(1,1000000000)} skills"
        self.save_dataframe_to_csv(df,file_name_skills)

    def save_dataframe_to_csv(self,df, file_name, folder_name="data"):
        try:

            if not os.path.exists(folder_name):
                os.makedirs(folder_name)
            file_name_csv = f"{file_name}.csv"
            # Construct the full file path
            file_path = os.path.join(folder_name, file_name_csv)

            # Save the DataFrame to the specified path
            df.to_csv(file_path, index=False)
            print(f"DataFrame successfully saved to {file_path}")

        except Exception as e:
            print(f"An error occurred while saving the DataFrame: {e}")

    def __extract_data(self,driver,wait,ec,name_companies,job_titles,location_jobs,post_dates,skills):
        time.sleep(1)
        name_company=job_title=location=posted_date=skill= "N/A"

        company_Xpath = '//*[@id="content"]/div[3]/section[1]/div[1]/div[1]/div/div[1]/a[1]'
        name_company = self.__get_text_or_nan(By.XPATH, company_Xpath,wait=wait,driver=driver,ec=ec)
        translated_company_name = translate_to_english(name_company)

        job_title_xpath = '//*[@id="content"]/div[3]/section[1]/div[1]/div[1]/div/h1'
        job_title = self.__get_text_or_nan(By.XPATH, job_title_xpath,wait=wait,driver=driver,ec=ec)
        translated_job_title = translate_to_english(job_title)


        location_xpath = '''//div[@class='col']//dl[dt[text()='근무지역']]/dd'''
        location = self.__get_text_or_nan(By.XPATH, location_xpath,wait=wait,driver=driver,ec=ec)
        transalted_location = translate_to_english(location)

        posted_date_xpath = '''//*[@id="content"]//dl[contains(., '시작일')]'''
        posted_date = self.__get_text_or_nan(By.XPATH, posted_date_xpath,wait=wait,driver=driver,ec=ec)
        cleaned_date = clean_and_format_first_date(posted_date)

        skill = self.__get_skills_from_page(wait=wait,ec=ec)
        job_titles.append(translated_job_title)
        location_jobs.append(transalted_location)
        post_dates.append(cleaned_date)
        name_companies.append(translated_company_name)
        skills.append(skill)


    def __get_text_or_nan(self, locator_type, locator_value,wait,ec,driver):
        try:
            element = wait.until(ec.presence_of_element_located((locator_type, locator_value)))
            return element.text.strip() if element and element.text.strip() else "N/A"
        except Exception as e:
            return "N/A"
    
    def __get_skills_from_page(self,wait,ec):
     texts=[]
     try:
         target_element  = wait.until(ec.presence_of_element_located((By.XPATH,'//*[@id="content"]/div[3]/section[1]')))
         for child in target_element.find_elements(By.XPATH, './*'):

             try:
                 stop=child.find_element(By.XPATH, '//*[@id="content"]/div[3]/section[2]/div/div[7]/div[1]/h2/font/font')
             except:
                 try:
                     stop=child.find_element(By.XPATH, '//*[@id="content"]/div[3]/section[2]/div/div[9]/div[1]/h2/font/font')
                 except:
                     stop=None

             text = translate_to_english(child.text.strip())
             if stop:  # Case-insensitive match
                 break
             texts.append(text)
         return extract_skills(texts) if texts else " "
     except:
        return " "