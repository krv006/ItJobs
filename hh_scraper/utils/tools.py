import re

from hh_scraper.processing.identify import identify_title


def give_to_ai():
    raw_csv_path = os.path.join("Data", "job_data_raw.csv")

    if not os.path.exists(raw_csv_path):
        print(f"Error in give_to_ai: Input file not found at '{raw_csv_path}'")
        return

    try:

        df = pd.read_csv(raw_csv_path, keep_default_na=False, encoding='utf-8')
        print(f"Read {len(df)} rows from {raw_csv_path} for AI processing.")

        if "Job_Title" not in df.columns or "Skills" not in df.columns:
            print("Error in give_to_ai: Required columns 'Job_Title' or 'Skills' not found in CSV.")
            return

        titles = df["Job_Title"].tolist()
        skills = df["Skills"].tolist()

        cleaned_titles = []
        for title in titles:
            title_str = str(title).strip()
            title_str = re.sub(r'[^\w\s]', '', title_str)
            title_str = re.sub(r'\s+', ' ', title_str)
            title_str = title_str.lower()
            cleaned_titles.append(title_str)

        print(f"Processing {len(cleaned_titles)} titles for AI.")

        # Batch processing with specified batch size
        batch_size = 10  # Consider making this smaller if AI times out
        for i in range(0, len(cleaned_titles), batch_size):
            # Slice titles and skills for the current batch
            titles_batch = cleaned_titles[i:i + batch_size]
            skills_batch = skills[i:i + batch_size]  # Assumes skills list matches length

            # Call the function with the current batch
            print(f"\nProcessing AI batch {i // batch_size + 1}...")
            try:
                # Ensure identify_title saves results to Title.csv or handles output
                identify_title(titles=titles_batch, skills=skills_batch)
                print(f"Sent batch to AI: {titles_batch}")
            except Exception as ai_call_error:
                print(f"ERROR calling identify_title for batch starting at index {i}: {ai_call_error}")
                # Decide whether to continue or stop on AI error

            # Add a delay
            time.sleep(5)
        print("\nFinished AI processing.")

    except FileNotFoundError:
        print(f"Error in give_to_ai: File not found at '{raw_csv_path}'")
    except Exception as e:
        print(f"An error occurred in give_to_ai: {e}")
        import traceback
        traceback.print_exc()


# Ensure identify_title function exists and correctly writes to "Title.csv"
# Example call (if running this script directly):
# if __name__ == "__main__":
#    give_to_ai()

# --- from search_by_title.py ---
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time


def search(title, wait):
    try:
        # Locate the search input box and button
        jobs_entered_button = wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="a11y-search-input"]'))
        )
        search_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="supernova_search_form"]/div/div[2]/button/div/span/span'))
        )

        # Input the job title and perform the search
        jobs_entered_button.send_keys(Keys.CONTROL + "a")  # Select all text
        jobs_entered_button.send_keys(Keys.DELETE)
        time.sleep(2)
        jobs_entered_button.send_keys(title)
        time.sleep(3)
        search_button.click()
    except Exception as e:
        print(f"An error occurred during search: {e}")


# --- from Skills_mapping.py ---
tools_list = [
    ".NET", "Adobe XD", "Airflow", "Alamofire", "Alexa Skills Kit", "Amplify", "Ansible",
    "Apache", "Apache Kafka", "Apache Airflow", "Apache NiFi", "Apache Storm", "AppDynamics",
    "Argo", "Asana", "Athena", "AWS", "AWS SageMaker", "Azure", "Azure DevOps", "Azure ML",
    "Bash", "BigQuery", "Bizagi", "Bitbucket", "Blender", "Bootstrap", "C++", "Caffe",
    "Cassandra", "Chef", "Cisco ASA", "Cisco Packet Tracer", "CircleCI", "ClickHouse",
    "CloudFormation", "CloudWatch", "Combine", "Confluence", "CoreData", "CSS", "Dagger",
    "DataRobot", "Databricks", "Datadog", "dbt (data build tool)", "Django", "Docker",
    "Docker Swarm", "Domo", "Draw.io", "Dynatrace", "Eclipse", "ElasticSearch", "Excel",
    "Fargate", "FastAPI", "Firebase", "Figma", "Flask", "GCP", "Git", "GitHub",
    "GitHub Actions", "GitLab CI/CD", "Glide", "Golang", "Google AI Platform",
    "Google Analytics", "Google Tag Manager", "Gradle", "Grafana", "Graylog", "H2O.ai",
    "Hadoop", "Helm", "Heroku", "Hugging Face", "OpenAI API", "IIS", "Informatica",
    "Insomnia", "IntelliJ IDEA", "iOS SDK", "Istio", "Jenkins", "Jenkins X", "JIRA",
    "JMeter", "Jupyter", "Jupyter Notebook", "JUnit", "Kali Linux", "Keras", "Kibana",
    "KNIME", "Kotlin", "Kubernetes", "Lambda", "Linux", "Logstash", "Looker", "LookML",
    "Lucidchart", "MATLAB", "Maven", "Metasploit", "Cognitive Services",
    "Minitab", "MongoDB", "MongoDB Atlas", "Mocha", "Mulesoft",
    "Nagios", "Netlify", "New Relic", "Nexus", "Nginx", "Node.js", "Notion", "NumPy",
    "Objective-C", "OpenCV", "OpenShift", "OpenStack", "Oracle", "Oracle Cloud",
    "Pandas", "Palo Alto Networks", "PeopleSoft", "Podman", "PostgreSQL", "Power BI",
    "Power Automate", "PowerApps", "PowerShell", "Presto", "Prometheus", "Puppet",
    "PyCharm", "Python", "Pytest", "PyTorch", "QlikView", "Qlik Sense", "R", "R Studio",
    "Rancher", "RapidMiner", "React", "Red Hat Enterprise Linux", "Redshift",
    "Retrofit", "Ruby", "RxJava", "Rust", "SalesForce", "SAP", "SAP Analytics Cloud",
    "Scala", "Scikit-learn", "SciPy", "Selenium", "Snyk", "Snowflake", "Spark",
    "Splunk", "Spyder", "SQLite", "SSH", "SQL", "SSL", "Stata", "Superset", "Swagger",
    "Swift", "Tableau", "Tableau Prep", "Tailwind CSS", "Talend", "TensorFlow",
    "Terraform", "Trello", "Travis CI", "Unity", "Unreal Engine", "Vercel",
    "Visual Studio", "VS Code", "Vue.js", "Wireshark", "Windows Server", "Xcode",
    "ASP.NET", "Java", "Spring", "JavaScript", "Angular", "Vue.js", "Ruby on Rails",
    "Laravel", "Gin", "Qt", "SwiftUI", "Android SDK", "TypeScript", "NestJS",
    "Shiny", "Elixir", "Phoenix", "Clojure", "Compojure", "Rocket",
    "Dart", "Flutter", "Haskell", "Yesod", "Julia", "HTTP.jl", "Lua", "LÖVE",
    "Shell", "PowerShell", "Cocoa", "Simulink", "Assembly", "NASM", "COBOL",
    "Pascal", "Free Pascal", "F#", "ASP.NET Core", "Blazor", "Android Studio",
    "Charles Proxy", "PHP", "MySQL", "PHP7", "RabbitMQ", "GitHub", "Agile",

    # Added tools from job post:
    "Word", "Excel", "PowerPoint",
    "Adobe Creative Suite", "Midjourney", "DALL·E", "Bitrix",
    # Newly added tools for Graphic Designer
    "Adobe Photoshop", "Adobe Illustrator", "Adobe InDesign", "CorelDRAW",
    "Midjourney", "DALL·E", "Canva", "Affinity Designer", "Procreate",
    "Font Awesome", "Google Fonts", "DaFont", "Placeit", "MockupWorld"
]

# --- from Title_to_csv.py ---
import pandas as pd
import os


def to_csv(titles: list, file_name: str = "Title.csv"):
    # Create a dictionary with the data
    data = {"Title": titles}

    # Convert the dictionary into a DataFrame
    df = pd.DataFrame(data)

    # Check if the file already exists
    file_exists = os.path.exists(file_name)

    # Write to the file, appending if it exists
    df.to_csv(
        file_name,
        index=False,
        mode="a",  # Append mode
        header=not file_exists  # Write header only if the file does not exist
    )

    if file_exists:
        print(f"Data appended to the existing file '{file_name}'.")
    else:
        print(f"File '{file_name}' created with header.")
