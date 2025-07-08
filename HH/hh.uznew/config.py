# config.py

# --- SCRAPING CONFIGURATION ---
# Set to an integer (e.g., 5) for testing, or None to scrape all pages.
SCRAPE_LIMIT = 5
BASE_URL = "https://hh.uz/search/vacancy?area=97&enable_snippets=true&ored_clusters=true&search_period=1&text=developer&search_field=name&search_field=company_name&search_field=description&L_save_area=true&professional_role=156&professional_role=160&professional_role=10&professional_role=12&professional_role=150&professional_role=25&professional_role=165&professional_role=34&professional_role=36&professional_role=73&professional_role=155&professional_role=96&professional_role=164&professional_role=104&professional_role=157&professional_role=107&professional_role=112&professional_role=113&professional_role=148&professional_role=114&professional_role=116&professional_role=121&professional_role=124&professional_role=125&professional_role=126&page={page_num}"

# --- AI & DATA CLEANING CONFIGURATION ---
# 🔁 ADD YOUR GOOGLE AI API KEY HERE
API_KEY = "AIzaSyDAhcvX5-iAwOk8XQXZKFQdcQVszvwnTXI" 

# List of job titles the AI is allowed to identify. Used for final filtering.
VALID_JOB_TITLES = [
    "Backend Developer", "Frontend Developer", "Full Stack Developer", "Data Analyst", 
    "Data Engineer", "Data Scientist", "AI Engineer", "Android Developer", "IOS Developer", 
    "Game Developer", "DevOps Engineer", "IT Project Manager", "Network Engineer",
    "Cybersecurity Analyst", "Cloud Architect", "QA Engineer", "UI/UX Designer", 
    "System Administrator", "IT Support Specialist", "Graphic Designer", "unknown"
]


# --- DATABASE CONFIGURATION ---
# 🔁 ADD YOUR SQL SERVER DETAILS HERE
DB_CONFIG = {
    'driver': '{ODBC Driver 17 for SQL Server}',
    'server': 'POWERBI-1\\IT_JOBS',  # e.g., 'localhost' or 'SERVER_NAME\\INSTANCE_NAME'
    'database': 'IT_JOBS',
    'username': 'sa',
    'password': 'maab2024',
    'table_name': 'JobListings'
}