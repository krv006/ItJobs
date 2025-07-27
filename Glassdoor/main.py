import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
import datetime
import pyodbc

def save_to_database(title,company,location,location_sub,title_sub,skills,salary,date):
    try:
        with open("conn.json") as file:
            conn_dt = json.load(file)
        conn = pyodbc.connect(
            f"Driver={conn_dt['driver']};"
            f"Server={conn_dt['server']};"
            f"Database={conn_dt['db_name']};"
            "Trusted_Connection=yes;"
        )
        cursor = conn.cursor()
        insert_query = """
        INSERT INTO Glassdoor (
            title,company,location,location_sub,title_sub,skills,salary,date
        ) VALUES (?,?,?,?,?,?,?,?)
        """
        cursor.execute(insert_query, (
            title,company,location,location_sub,title_sub,skills,salary,date))
        conn.commit()
    except Exception as e:
        # print(f"Error saving to database: {e}")
        pass
    finally:
        if 'conn' in locals():
            conn.close()

class GlassdoorScraper:
    def __init__(self, job: str, country: str, headless=False):
        self.job = job.strip().replace(" ", "-")
        self.country = country.strip().replace(" ", "-")
        self.start = 1
        self.continue_scraping = True
        
        # Initialize driver
        options = uc.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--start-maximized")
        if headless:
            options.add_argument("--headless")
            
        self.driver = uc.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 5)
        self.wait1 = WebDriverWait(self.driver, 2)
        self.tries = 0
        
        # Load cookies if available
        self.load_cookies("cookies.json")
        
        # Start scraping
        self.start_scraping()
        
    def load_cookies(self, cookie_file):
        self.driver.get("https://www.glassdoor.com")
        time.sleep(2)  # Wait for initial page load
        
        try:
            with open(cookie_file, "r") as file:
                cookies = json.load(file)
                for cookie in cookies:
                    if "sameSite" in cookie:
                        cookie.pop("sameSite")
                    try:
                        self.driver.add_cookie(cookie)
                    except Exception as e:
                        print(f"Failed to add cookie: {e}")
            self.driver.refresh()
            time.sleep(3)
        except FileNotFoundError:
            print("No cookie file found, proceeding without cookies")
            
    def start_scraping(self):
        url = f"https://www.glassdoor.com/Job/{self.job}-jobs-SRCH_KO0,14.htm"
        print(f"Navigating to: {url}")
        self.driver.get(url)
        time.sleep(3)  # Initial page load
        
        while self.continue_scraping:
            self.scrape_page()
    
    def check_dialog(self):
        try:
            self.wait1.until(
                EC.element_to_be_clickable((By.XPATH,"//button[contains(@data-test, 'job-alert-modal-close')]"))
            ).click()
        except:
            pass
            
    def scrape_page(self):
        try:
            # job_list = self.wait.until(
            #     EC.presence_of_element_located((By.XPATH, "//ul[@aria-label='Jobs List']"))
            # )
            
            # Try to scrape current job
            base = f"//ul[@aria-label='Jobs List']/li[{self.start}]"
            job_element = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, f"{base}"))
            )
            job_element.click()
            time.sleep(1)  # Let the details load
            
            self.scrape_job_details(base)
            self.start += 1
            self.tries = 0
                
        except Exception as e:
            if self.tries < 3:
                self.check_dialog()
                self.tries += 1
                print(f"try: {self.tries}")
            else:
                try:
                    # Try to load more jobs
                    load_more = self.driver.find_element(By.XPATH, "//button[@data-test='load-more']")
                    load_more.click()
                    time.sleep(3)  # Wait for new jobs to load
                except:
                    print("No more jobs to load or load more button not found")
                    self.continue_scraping = False
                
    def scrape_job_details(self,base):
        try:
            company = self.wait1.until(
                EC.presence_of_element_located((By.XPATH, f"//div[contains(@class,'EmployerProfile_employerNameHeading')]"))
            ).text
        except:
            company = ''
            
        try:
            job_title = self.wait1.until(
                EC.presence_of_element_located((By.XPATH, f"//h1[contains(@id,'job-title')]"))
            ).text
        except:
            job_title = ''
            
        try:
            posted_ago = self.wait1.until(
                EC.presence_of_element_located((By.XPATH, f"{base}//div[contains(@data-test,'job-age')]"))
            ).text
        except:
            posted_ago = ''
            
        try:
            salary = self.wait1.until(
                EC.presence_of_element_located((By.XPATH, f"{base}//div[contains(@id,'job-salary')]"))
            ).text
        except:
            salary = ''
        try:
            location = self.wait1.until(
                EC.presence_of_element_located((By.XPATH, f"{base}//div[contains(@data-test,'emp-location')]"))
            ).text
        except:
            location = ''
        try:
            skills = ','.join([x.text
            for x in self.wait1.until(
                EC.visibility_of_all_elements_located((By.XPATH,"//li[contains(@class,'PendingQualification_pendingQualification')]"))
            )])
        except:
            skills = ''
            
        # Get current timestamp
        timestamp = datetime.date.today()
        if "30d+" in posted_ago:
            date = timestamp + datetime.timedelta(days=30)
        elif "d" in posted_ago:
            date = timestamp + datetime.timedelta(days=int(posted_ago.replace("d","")))
        else:
            date = timestamp
        
        # Print or store the data
        save_to_database(job_title,company,location,self.country,self.job,skills,salary,date)
        
        # Here you could also write to a file or database
        # with open("jobs.csv", "a") as f:
        #     f.write(f"{job_title},{company},{posted_ago},{salary}\n")

if __name__ == "__main__":
    with open("listings of jobs.json","r") as file:
        jobs = json.load(file)
    for job in jobs:
        GlassdoorScraper(job, "United States")
