# database.py
import pandas as pd
import pyodbc
import traceback
import config

def insert_to_sql(df: pd.DataFrame, db_config: dict):
    """
    Connects to SQL Server and inserts the DataFrame data.
    Deletes existing records with the same ID before inserting.
    """
    if df.empty:
        print("⚠️ DataFrame is empty. No data to insert into the database.")
        return

    conn_str = (
        f"DRIVER={db_config['driver']};"
        f"SERVER={db_config['server']};"
        f"DATABASE={db_config['database']};"
        f"UID={db_config['username']};"
        f"PWD={db_config['password']};"
        "Connection Timeout=30;"
    )

    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        print("\n--- ✅ Connected to SQL Server ---")

        # Ensure table exists
        create_table_query = f"""
        IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '{db_config['table_name']}')
        BEGIN
            CREATE TABLE dbo.{db_config['table_name']} (
                ID NVARCHAR(100) PRIMARY KEY, Posted_date DATE NULL, Job_Title_from_List NVARCHAR(255) NULL,
                Job_Title NVARCHAR(255) NULL, Company NVARCHAR(255) NULL, Company_Logo_URL NVARCHAR(MAX) NULL,
                Country NVARCHAR(100) NULL, Location NVARCHAR(255) NULL, Skills NVARCHAR(MAX) NULL,
                Salary_Info NVARCHAR(255) NULL, Source NVARCHAR(255) NULL, IngestionTimestamp DATETIME2 DEFAULT GETDATE()
            )
        END
        """
        cursor.execute(create_table_query)
        conn.commit()

        # Delete existing records to prevent primary key violations
        ids_to_insert = df['ID'].tolist()
        if ids_to_insert:
            placeholders = ','.join(['?'] * len(ids_to_insert))
            delete_query = f"DELETE FROM {db_config['table_name']} WHERE ID IN ({placeholders})"
            cursor.execute(delete_query, *ids_to_insert)
            conn.commit()
            print(f"Deleted {cursor.rowcount} old records to prepare for new insertion.")

        # Prepare and insert new data
        insert_query = f"""
        INSERT INTO {db_config['table_name']} (
            ID, Posted_date, Job_Title_from_List, Job_Title, Company, 
            Company_Logo_URL, Country, Location, Skills, Salary_Info, Source
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        # Convert date column to handle potential errors
        df['Posted_date'] = pd.to_datetime(df['Posted_date'], errors='coerce').dt.date
        
        rows_to_insert = [tuple(row) for row in df.itertuples(index=False)]

        cursor.fast_executemany = True
        cursor.executemany(insert_query, rows_to_insert)
        conn.commit()
        print(f"✅ Successfully inserted {len(rows_to_insert)} rows into the database.")

    except pyodbc.Error as db_error:
        print(f"❌ Database Error: {db_error}")
        traceback.print_exc()
    except Exception as e:
        print(f"❌ An unexpected error occurred during database operation: {e}")
        traceback.print_exc()
    finally:
        if 'conn' in locals() and conn:
            conn.close()
            print("--- Connection to SQL Server closed. ---")