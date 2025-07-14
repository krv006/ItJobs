# indeed_scraper.py
"""Robust Indeed scraper ‒ June 2025 markup
Run:  python indeed_main.py
Reqs: undetected-chromedriver 3.*, selenium, pyodbc
"""
import json
import random
import re
import time
from typing import Dict, List, Set

import pyodbc
import undetected_chromedriver as uc
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# ────────────────────────── CONFIG ──────────────────────────
MAX_WAIT = 50  # seconds to wait for page elements
PAGE_SLEEP = (1.2, 3.5)  # random sleep range between actions
HEADLESS = False  # switch to True on server
SCROLL_STEPS = 3  # scrolls to trigger lazy‑load

SKILL_PATTERN = re.compile(r"\b(Python|SQL|Power BI|Excel|AWS|Docker|Kubernetes|Java|React|C\+\+|Go)\b", re.I)
EDU_PATTERN = re.compile(r"\bBachelor'?s|Master'?s|PhD\b")


# ───────────────────────── Chrome driver ─────────────────────────

def create_driver(headless: bool = HEADLESS):
    opts = uc.ChromeOptions()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("start-maximized")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    return uc.Chrome(options=opts)


def accept_cookies(driver):
    try:
        WebDriverWait(driver, 6).until(
            EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))).click()
    except TimeoutException:
        pass  # banner yo'q


# ───────────────────────────── DB ─────────────────────────────

def db_connect():
    with open("conn.json") as f:
        c = json.load(f)
    return pyodbc.connect(
        f"Driver={c['driver']};Server={c['server']};Database={c['db_name']};Trusted_Connection=yes;"), None


def save(cursor, row: Dict):
    cursor.execute(
        """IF NOT EXISTS (SELECT 1 FROM indeed WHERE job_id = ?)
           INSERT INTO indeed (job_id, job_title, location, skills, salary, education,
                               job_type, company_name, job_url, source)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        row["job_id"], row["job_title"], row["location"], row["skills"], row["salary"],
        row["education"], row["job_type"], row["company_name"], row["job_url"], "indeed.com"
    )


# ─────────────────────────── Helpers ───────────────────────────

def _lazy_scroll(driver):
    for _ in range(SCROLL_STEPS):
        driver.execute_script("window.scrollBy(0, document.body.scrollHeight*0.6);")
        time.sleep(0.6)


def _wait_results_or_empty(driver):
    try:
        WebDriverWait(driver, MAX_WAIT).until(
            EC.any_of(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a.tapItem[data-jk]")),
                EC.presence_of_element_located((By.CSS_SELECTOR, "#noResultsMessage"))
            )
        )
        return True
    except TimeoutException:
        return False


# ────────────────────────── Scraper core ──────────────────────────

def get_job_links(driver) -> List[str]:
    links = driver.find_elements(By.CSS_SELECTOR, "a.tapItem[data-jk]")
    return [l.get_attribute("href") for l in links if l.get_attribute("href")]


def parse_job_page(driver) -> Dict:
    WebDriverWait(driver, MAX_WAIT).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "h1.jobsearch-JobInfoHeader-title")))

    title = driver.find_element(By.CSS_SELECTOR, "h1.jobsearch-JobInfoHeader-title").text
    company = driver.find_element(By.CSS_SELECTOR, "div[data-testid='inlineHeader-companyName']").text
    location = driver.find_element(By.CSS_SELECTOR, "div[data-testid='inlineHeader-companyLocation']").text
    desc = driver.find_element(By.ID, "jobDescriptionText").text

    skills = ",".join(sorted(set(SKILL_PATTERN.findall(desc))))
    education = ",".join(sorted(set(EDU_PATTERN.findall(desc)))) or "N/A"

    try:
        salary = driver.find_element(By.CSS_SELECTOR, "div[data-testid='salary-snippet-container']").text
    except NoSuchElementException:
        salary = ""

    try:
        job_type = driver.find_element(By.XPATH, "//span[contains(text(),'Job type')]/following-sibling::span").text
    except NoSuchElementException:
        job_type = ""

    return dict(job_title=title, company_name=company, location=location,
                skills=skills, education=education, salary=salary, job_type=job_type)


def scrape_keyword(driver, cursor, keyword: str, processed: Set[str]):
    url = f"https://www.indeed.com/jobs?q={keyword}&sort=date&fromage=7"
    driver.get(url)
    accept_cookies(driver)

    if not _wait_results_or_empty(driver):
        print("    ⚠️  Timed‑out while waiting for results.")
        return

    page = 1
    while True:
        _lazy_scroll(driver)
        links = get_job_links(driver)
        if not links:
            print(f"    ⚠️  No links on page {page}.")
            break

        for job_url in links:
            if job_url in processed:
                continue
            processed.add(job_url)
            driver.execute_script("window.open(arguments[0]);", job_url)
            driver.switch_to.window(driver.window_handles[-1])
            try:
                data = parse_job_page(driver)
                job_id = re.search(r"jk=([a-f0-9]+)", job_url).group(1)
                data.update(job_id=job_id, job_url=job_url)
                save(cursor, data)
            except Exception as e:
                print("       ↳ skip (", e, ")")
            finally:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
            time.sleep(random.uniform(*PAGE_SLEEP))

        try:
            nxt = driver.find_element(By.CSS_SELECTOR, "a[aria-label='Next Page']")
            if nxt.get_attribute("aria-disabled") == "true":
                break
            nxt.click()
            page += 1
            time.sleep(random.uniform(*PAGE_SLEEP))
        except NoSuchElementException:
            break


# ───────────────────────────── main ─────────────────────────────

def main():
    driver = create_driver()
    conn, cur = db_connect()
    cur = conn.cursor()

    processed: Set[str] = set()
    with open("jobs-list.json") as f:
        for kw in json.load(f):
            print(f"🔍 {kw}")
            try:
                scrape_keyword(driver, cur, kw, processed)
                conn.commit()
            except Exception as e:
                print(f"    ❌ '{kw}' failed: {e}")

    cur.close();
    conn.close();
    driver.quit()


if __name__ == "__main__":
    main()
