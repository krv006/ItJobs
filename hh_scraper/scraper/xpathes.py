# --- from XPathes.py ---
# --- START OF FILE XPathes.py (Corrected) ---

Job_title_path = "//h1[@data-qa='vacancy-title']"

# Targets the company name link's text content
company_name_path = "//a[@data-qa='vacancy-company-name']"

salary_info_path = "//div[@data-qa='vacancy-salary']"

# A stable path for the entire vacancy description block
skills_path = "//div[contains(@class, 'vacancy-description')]"

# Targets the element containing both location and date
location_and_posted_date_path = "//p[@data-qa='vacancy-view-location'] | //span[@data-qa='vacancy-view-raw-address']"

# This remains correct for getting the link to each job from the search results
Urls_path = '//a[@data-qa="serp-item__title"]'

# --- THE FIX IS HERE: Renamed variables to match their usage ---

# A reliable XPath for the 'Next' button on the search results page
next_button_path = "//a[@data-qa='pager-next']"

# A specific XPath for the company logo on the job details page
Company_Logo_URL_path = "//a[@data-qa='vacancy-company-logo']/img"

