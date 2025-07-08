# locators.py

# Locators for the search results page
job_list_urls_xpath = "//a[@class='serp-item__title']"
next_button_xpath = "//a[@data-qa='pager-next']"

# Locators for the individual job detail page
job_title_xpath = "//h1[@data-qa='vacancy-title']"
company_name_xpath = "//a[@data-qa='vacancy-company-name']"
location_and_date_xpath = "//p[@data-qa='vacancy-view-location'] | //span[@data-qa='vacancy-view-raw-address']"
skills_xpath = "//div[@class='bloko-tag-list']"
salary_info_xpath = "//div[@data-qa='vacancy-salary']"
company_logo_url_xpath = "//img[@data-qa='vacancy-company-logo']"