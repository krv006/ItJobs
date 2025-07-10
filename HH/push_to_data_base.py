import os
import sys
import traceback

import pandas as pd
import pyodbc


def insert_data_to_sql(job_id,company_name, job_title, post_date, location, technical_skills, salary, company_logo_url):
    print("\n--- Connecting to SQL Server ---")
    conn = pyodbc.connect(
        'Driver={ODBC Driver 17 for SQL Server};'  # <<< MODIFIED: USING MODERN DRIVER
        # If you installed ODBC Driver 18, use 'Driver={ODBC Driver 18 for SQL Server};'
        # If you don't have 17 or 18, you MUST install one. Fallback to {SQL Server} is last resort.
        # 'Server=POWERBI-1\\IT_JOBS;'
        # 'Database=IT_JOBS;'
        # 'UID=sa;'
        # 'PWD=maab2024;'
        # 'Connection Timeout=30;'
        'Driver={SQL Server};'
        'Server=WIN-LORQJU2719N;'
        'Database=IT_JOBS;'
        'Trusted_Connection=yes;'
    )
    cursor = conn.cursor()

    create_table_query = """
    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'dbo' AND TABLE_NAME = 'JobListings')
    BEGIN
        CREATE TABLE dbo.JobListings (
            ID NVARCHAR(100) PRIMARY KEY, Posted_date DATE NULL, Job_Title_from_List NVARCHAR(255) NULL,
            Job_Title NVARCHAR(255) NULL, Company NVARCHAR(255) NULL, Company_Logo_URL NVARCHAR(MAX) NULL,
            Country NVARCHAR(100) NULL, Location NVARCHAR(255) NULL, Skills NVARCHAR(MAX) NULL,
            Salary_Info NVARCHAR(255) NULL, Source NVARCHAR(255) NULL, IngestionTimestamp DATETIME2 DEFAULT GETDATE()
        )
        PRINT 'Table dbo.JobListings created.'
    END
    """
    cursor.execute(create_table_query)
    conn.commit()

    insert_query = """
    INSERT INTO dbo.JobListings
    (ID, Posted_date, Job_Title_from_List, Job_Title, Company, Company_Logo_URL, Country, Location, Skills, Salary_Info, Source)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    cursor.execute(insert_query,params = (job_id,post_date,job_title,job_title,company_name,company_logo_url,'uzbekistan',location,technical_skills,salary,'hh.uz'))
    conn.commit()
    print("\n--- Preparing data for insertion ---")

        