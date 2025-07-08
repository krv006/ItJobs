import os

import pandas as pd


def cleaned_data_to_csv():
    raw_csv_path = os.path.join("Data", "job_data_raw.csv")
    title_csv_path = "Title.csv"
    final_csv_path = 'cleaned_job_titles_final.csv'

    if not os.path.exists(raw_csv_path):
        print(f"❌ Error: Raw data file '{raw_csv_path}' not found. Cannot perform cleaning.")
        return

    df = pd.read_csv(raw_csv_path, keep_default_na=False, na_values=['', 'N/A'], encoding='utf-8')
    print(f"\nRead {len(df)} rows from {raw_csv_path} for cleaning.")

    if os.path.exists(title_csv_path):
        try:
            df_titles = pd.read_csv(title_csv_path)
            if len(df_titles) == len(df):
                df["Job_Title_from_List"] = df_titles["Title"]
                print("✅ Successfully merged AI-identified titles from Title.csv.")
            else:
                # This warning is key!
                print(
                    f"⚠️ Warning: Row count mismatch between raw data ({len(df)}) and titles ({len(df_titles)}). AI titles will not be used.")
        except Exception as e:
            print(f"⚠️ Warning: Could not read or process Title.csv. Error: {e}. AI titles will not be used.")
    else:
        print("⚠️ Warning: Title.csv not found. 'Job_Title_from_List' will contain default values.")

    df_cleaned = df.copy()

    valid_job_titles = [
        "Backend Developer", "Frontend Developer", "Full Stack Developer", "Data Analyst", "Data Engineer",
        "Data Scientist",
        "AI Engineer", "Android Developer", "IOS Developer", "Game Developer", "DevOps Engineer", "IT Project Manager",
        "Network Engineer",
        "Cybersecurity Analyst", "Cloud Architect", "QA Engineer", "UI/UX Designer", "System Administrator",
        "IT Support Specialist",
        "Graphic Designer"
    ]

    initial_rows = len(df_cleaned)
    df_cleaned = df_cleaned[df_cleaned['Job_Title_from_List'].isin(valid_job_titles)]
    print(f"Filtered by valid titles: {initial_rows} -> {len(df_cleaned)} rows.")

    initial_rows = len(df_cleaned)
    df_cleaned.dropna(subset=['ID', 'Job_Title', 'Company', 'Posted_date'], inplace=True)
    print(f"Dropped rows with missing critical info: {initial_rows} -> {len(df_cleaned)} rows.")

    initial_rows = len(df_cleaned)
    df_cleaned = df_cleaned.drop_duplicates(subset=['Company', 'Job_Title', 'Location'], keep='first')
    print(f"Dropped duplicate listings: {initial_rows} -> {len(df_cleaned)} rows.")

    required_db_columns = [
        'ID', 'Posted_date', 'Job_Title_from_List', 'Job_Title', 'Company',
        'Company_Logo_URL', 'Country', 'Location', 'Skills', 'Salary_Info', 'Source'
    ]

    final_df = df_cleaned.reindex(columns=required_db_columns, fill_value='N/A')

    final_df.to_csv(final_csv_path, index=False, encoding='utf-8')
    print(f"✅ Cleaned data with {len(final_df)} rows saved to '{final_csv_path}'")
