# --- from config.py ---
# config.py
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# options = webdriver.ChromeOptions()
# options.add_argument(r"--user-data-dir=C:\\Users\\bozor\\AppData\\Local\\Google\\Chrome\\User Data\\NewProfile")
# options.add_argument("--profile-directory=Default")  # Use the Chrome profile you want
driver = webdriver.Chrome()
wait = WebDriverWait(driver, 10)
ec = EC

