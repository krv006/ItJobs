import os

import pandas as pd
import pyodbc


def collect_into_dataframe(job_ids, company_names, job_titles, location_jobs,
                           post_dates, technical_skills, salary, company_logo_urls,
                           job="unknown"):
    num_rows = len(company_names)

    data = {
        "ID": job_ids if len(job_ids) == num_rows else ["N/A"] * num_rows,
        "Posted_date": post_dates if len(post_dates) == num_rows else ["N/A"] * num_rows,
        "Job_Title_from_List": [job] * num_rows,
        "Job_Title": job_titles if len(job_titles) == num_rows else ["N/A"] * num_rows,
        "Company": company_names,
        "Company_Logo_URL": company_logo_urls if len(company_logo_urls) == num_rows else ["N/A"] * num_rows,
        "Country": ["Uzbekistan"] * num_rows,
        "Location": location_jobs if len(location_jobs) == num_rows else ["N/A"] * num_rows,
        "Skills": technical_skills if len(technical_skills) == num_rows else ["N/A"] * num_rows,
        "Salary_Info": salary if len(salary) == num_rows else ["N/A"] * num_rows,
        "Source": ["hh.uz"] * num_rows
    }

    for key, value in data.items():
        if len(value) != num_rows:
            print(f"Warning: Length mismatch for '{key}'. Padding with N/A.")
            data[key] = (list(value) + ["N/A"] * num_rows)[:num_rows]

    df = pd.DataFrame(data)

    folder_path = 'Data'
    file_path = os.path.join(folder_path, 'job_data_raw.csv')

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Created folder: {folder_path}")

    df.to_csv(file_path, mode='w', header=True, index=False, encoding='utf-8')
    print(f"Raw data saved to '{file_path}'.")

    # todo Database Setting
    insert_to_sql_server(df,
                         server="localhost",
                         database="YourDatabaseName",
                         table_name="YourTableName",
                         username="your_username",
                         password="your_password")


def insert_to_sql_server(df, server, database, table_name, username, password):
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password}"
    )

    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        print("Connected to SQL Server!")

        for index, row in df.iterrows():
            cursor.execute(f"""
                INSERT INTO {table_name} (
                    ID, Posted_date, Job_Title_from_List, Job_Title,
                    Company, Company_Logo_URL, Country, Location,
                    Skills, Salary_Info, Source
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, tuple(row))

        conn.commit()
        print(f"Inserted {len(df)} rows into {table_name}.")
        cursor.close()
        conn.close()

    except Exception as e:
        print(f"SQL Server error: {e}")
