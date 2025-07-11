# main.py
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from Scrapping import Extract
from get_urls import Extract_urls
from threadis import assign_lists_to_threads
from push_to_database import insert_single_row_to_sql

def get_total_pages(driver):
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.pagination")))
        pages = driver.find_elements(By.CSS_SELECTOR, "div.pagination a")
        page_numbers = [int(p.text) for p in pages if p.text.isdigit()]
        return max(page_numbers) if page_numbers else 1
    except Exception:
        return 1

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(options=options)
    return driver

def main():
    driver = setup_driver()

    BASE_URL = "https://www.saramin.co.kr/zf_user/search?cat_mcls=2&company_cd=0%2C1%2C2%2C3%2C4%2C5%2C6%2C7%2C9%2C10&cat_kewd=1658&panel_type=&search_optional_item=y&search_done=y&panel_count=y&preview=y&recruitSort=reg_dt&recruitPageCount=40"

    print("\U0001F310 Saytga ulanish...")
    driver.get(BASE_URL)
    time.sleep(5)
    wait = WebDriverWait(driver, 10)

    total_pages = get_total_pages(driver)
    print(f"\U0001F522 Jami sahifalar: {total_pages}")

    url_extractor = Extract_urls(driver=driver, wait=wait, ec=EC)
    url_extractor.load_data()

    all_urls = []
    for page in range(1, total_pages + 1):
        try:
            page_url = BASE_URL + f"&recruitPage={page}"
            driver.get(page_url)
            time.sleep(2)

            if "존재하지" in driver.page_source or "404" in driver.title or "403" in driver.title:
                print(f"\u274C Sahifa mavjud emas: {page}")
                break

            url_extractor.load_data()
            urls = url_extractor.get_urls()
            print(f"\u2705 {page}-sahifa: {len(urls)} ta URL topildi")
            all_urls.extend(urls)

        except Exception as e:
            print(f"\u26A0\uFE0F  Sahifa {page} da xatolik: {e}")
            continue

    if all_urls:
        print(f"\U0001F50E Umumiy URL soni: {len(all_urls)}")
        data_extractor = Extract()
        assign_lists_to_threads(data_extractor, all_urls, insert_single_row_to_sql)
        print("\U0001F389 Barcha ma'lumotlar bazaga yozildi!")
    else:
        print("\u274C Hech qanday URL topilmadi. Bazaga yozish bekor qilindi.")

if __name__ == "__main__":
    main()
