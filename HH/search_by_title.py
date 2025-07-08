import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC


def search(title, wait):
    try:
        jobs_entered_button = wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="a11y-search-input"]'))
        )
        search_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="supernova_search_form"]/div/div[2]/button/div/span/span'))
        )

        jobs_entered_button.send_keys(Keys.CONTROL + "a")
        jobs_entered_button.send_keys(Keys.DELETE)
        time.sleep(2)
        jobs_entered_button.send_keys(title)
        time.sleep(3)
        search_button.click()
    except Exception as e:
        print(f"An error occurred during search: {e}")
