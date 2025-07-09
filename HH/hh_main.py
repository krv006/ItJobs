# --- START OF FILE hh_main.py ---

import os
import time

from Extract_jobs import Extract
from File_to_list_to_ai import give_to_ai
from Matched_data import cleaned_data_to_csv
from collect import collect_into_dataframe
from config import driver, wait
from push_to_data_base import insert_data_to_sql

daily_url = "https://hh.uz/search/vacancy?area=97&enable_snippets=true&ored_clusters=true&search_period=1&text=developer&search_field=name&search_field=company_name&search_field=description&L_save_area=true&professional_role=156&professional_role=160&professional_role=10&professional_role=12&professional_role=150&professional_role=25&professional_role=165&professional_role=34&professional_role=36&professional_role=73&professional_role=155&professional_role=96&professional_role=164&professional_role=104&professional_role=157&professional_role=107&professional_role=112&professional_role=113&professional_role=148&professional_role=114&professional_role=116&professional_role=121&professional_role=124&professional_role=125&professional_role=126&page=0"

print("--- Starting Scraper ---")
if os.path.exists("Title.csv"):
    os.remove("Title.csv")
    print("Removed old Title.csv file.")

driver.get(daily_url)
time.sleep(5)

extractor = Extract(driver=driver, wait=wait)
extractor.load_data()

scraped_data = extractor.get_all_data()
collect_into_dataframe(scraped_data)

try:
    print("\n--- Starting AI Title Identification ---")
    give_to_ai()
except Exception as ai_error:
    print(f"❌ Error during AI processing (give_to_ai): {ai_error}")

try:
    print("\n--- Starting Data Cleaning and Matching ---")
    cleaned_data_to_csv()
except Exception as clean_error:
    print(f"❌ Error during data cleaning (cleaned_data_to_csv): {clean_error}")

try:
    print("\n--- Starting Database Insertion ---")
    insert_data_to_sql()
except Exception as db_error:
    print(f"❌ Error during database insertion (insert_data_to_sql): {db_error}")

# --- 5. CLEANUP ---
driver.quit()
print("\n--- Process complete. Browser closed. ---")
