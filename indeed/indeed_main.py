import json
import time
import pyodbc
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


def create_driver(headless=False):
    options = uc.ChromeOptions()
    if headless:
        options.add_argument("--headless=chrome")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("start-maximized")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
    options.add_argument("user-data-dir=C:\\Users\\user\\AppData\\Local\\Google\\Chrome\\User Data")
    driver = uc.Chrome(options=options, version_main=124)
    return driver


def load_cookies(driver):
    print("Loading cookies for Indeed session...")
    try:
        driver.get("https://www.indeed.com")
        with open("cookies.json", "r") as file:
            cookies = json.load(file)

        for cookie in cookies:
            driver.add_cookie(cookie)
        driver.refresh()
        time.sleep(2)

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//a[contains(text(), 'Sign out') or contains(text(), 'Log out')]"))
            )
            print("Successfully logged in using cookies.")
            return True
        except TimeoutException:
            print("Login failed. Cookies may be invalid or expired.")
            return False
    except Exception as e:
        print(f"Error loading cookies: {e}")
        return False


def save_to_database(job_id, job_title, location, skills, salary, education, job_type, company_name, job_url, source):
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
        INSERT INTO indeed (
            job_id, job_title, location, skills, salary, education, job_type, company_name, job_url, source
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(insert_query, (
            job_id, job_title, location, skills, salary, education, job_type, company_name, job_url, source))
        conn.commit()
        print(f"Saved job {job_id} to database.")
    except Exception as e:
        print(f"Error saving to database: {e}")
    finally:
        if 'conn' in locals():
            conn.close()


def scrape_jobs(driver, base_url):
    driver.get(base_url)
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'mosaic-provider-jobcards')]"))
        )
    except TimeoutException:
        print("Job cards not found. Check URL or login status.")
        return

    while True:
        try:
            jobs = driver.find_elements(By.XPATH, "//li[contains(@class, 'result')]")
            for job in jobs:
                try:
                    tt = job.find_element(By.XPATH, ".//a[contains(@class, 'jcs-JobTitle')]")
                    job_url = tt.get_attribute("href")
                    tt.click()
                    title = tt.text
                except:
                    continue
                time.sleep(1)

                # Location
                try:
                    location = job.find_element(By.XPATH, ".//div[contains(@data-testid, 'companyLocation')]").text
                except:
                    location = ""

                # Salary
                try:
                    salary = job.find_element(By.XPATH, ".//span[contains(@class, 'salary')]").text.replace("Pay",
                                                                                                            "").strip()
                except:
                    salary = ""

                # Job type
                try:
                    job_type = job.find_element(By.XPATH,
                                                ".//div[contains(@data-testid, 'attribute_snippet')]").text.strip()
                except:
                    job_type = ""

                # Skills
                try:
                    try:
                        driver.find_element(By.XPATH, "//button[contains(text(), '+ show more')]").click()
                        time.sleep(1)
                    except:
                        pass
                    skills = driver.find_element(By.XPATH, "//div[@data-testid='skills-section']").find_element(
                        By.XPATH, ".//ul").text
                    sks = skills.replace("Skills", "").replace("+ show more", "").replace("- show less", "").replace(
                        "(Required)", "").replace("\n", ",").replace(",,", ",").split(",")
                    skills = ",".join([sk.strip() for sk in sks if sk.strip() and "Do you have" not in sk])
                except:
                    skills = ""

                # Education
                try:
                    education = driver.find_element(By.XPATH, "//div[@data-testid='education-section']").text.replace(
                        "Education", "").replace("(Required)", "").replace("\n", ",").replace(",,", ",")
                    edcs = education.split(",")
                    education = ",".join([ed.strip() for ed in edcs if ed.strip() and "Do you have" not in ed])
                except:
                    education = "No Degree Required"

                # Company name
                try:
                    comp_name = job.find_element(By.XPATH, ".//span[contains(@class, 'companyName')]").text
                except:
                    comp_name = ""

                job_id = job_url.split("vjk=")[-1].split("&")[0] if "vjk=" in job_url else ""
                save_to_database(job_id, title, location, skills, salary, education, job_type, comp_name, job_url,
                                 "indeed.com")

            # Keyingi sahifaga o‘tish
            try:
                next_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[@data-testid='pagination-page-next']"))
                )
                next_button.click()
                time.sleep(2)
            except TimeoutException:
                print("No more pages to scrape.")
                break

        except Exception as e:
            print(f"Error while scraping: {e}")
            break


def main():
    driver = None
    try:
        driver = create_driver(headless=False)
        if not load_cookies(driver):
            print("Failed to load cookies. Please provide valid cookies in cookies.json.")
            return

        print("Login successful. Starting job scraping...")
        with open("jobs-list.json") as file:
            data = json.load(file)

        for job_n in data:
            base_url = f"https://www.indeed.com/jobs?q={job_n}&l=&sort=date&from=searchOnDesktopSerp"
            scrape_jobs(driver, base_url)

    except Exception as e:
        print(f"Error in main: {e}")
    finally:
        if driver:
            try:
                driver.quit()
            except Exception as e:
                print(f"Error quitting driver: {e}")


if __name__ == "__main__":
    main()