# --- from Matched_data.py ---
# --- START OF FILE Matched_data.py ---

import pandas as pd
import os

def cleaned_data_to_csv():
    raw_csv_path = os.path.join("Data", "job_data_raw.csv")
    title_csv_path = "Title.csv"
    final_csv_path = os.path.join("Data", "cleaned_job_titles_final.csv")  # ⬅ сохранение в папку Data

    if not os.path.exists(raw_csv_path):
        print(f"❌ Error: Raw data file '{raw_csv_path}' not found. Cannot perform cleaning.")
        return

    df = pd.read_csv(raw_csv_path, keep_default_na=False, na_values=['', 'N/A'], encoding='utf-8')
    print(f"\n📥 Read {len(df)} rows from {raw_csv_path} for cleaning.")

    # --- Merge AI-identified titles ---
    if os.path.exists(title_csv_path):
        try:
            df_titles = pd.read_csv(title_csv_path)
            if len(df_titles) == len(df):
                df["Job_Title_from_List"] = df_titles["Title"]
                print("✅ Successfully merged AI-identified titles from Title.csv.")
            else:
                print(f"⚠️ Warning: Row count mismatch (raw: {len(df)}, titles: {len(df_titles)}). Skipping merge.")
        except Exception as e:
            print(f"⚠️ Error reading Title.csv: {e}")
    else:
        print("⚠️ Title.csv not found. Column 'Job_Title_from_List' will remain unchanged or missing.")

    df_cleaned = df.copy()

    # List of valid AI titles
    valid_job_titles = [
        "Backend Developer", "Frontend Developer", "Full Stack Developer", "Data Analyst", "Data Engineer", "Data Scientist",
        "AI Engineer", "Android Developer", "IOS Developer", "Game Developer", "DevOps Engineer", "IT Project Manager", "Network Engineer",
        "Cybersecurity Analyst", "Cloud Architect", "QA Engineer", "UI/UX Designer", "System Administrator", "IT Support Specialist",
        "Graphic Designer"
    ]

    # 1. Filter by valid AI titles
    initial_rows = len(df_cleaned)
    df_cleaned = df_cleaned[df_cleaned['Job_Title_from_List'].isin(valid_job_titles)]
    print(f"🧹 Filtered by valid titles: {initial_rows} → {len(df_cleaned)} rows.")

    # 2. Drop rows missing critical fields
    initial_rows = len(df_cleaned)
    df_cleaned.dropna(subset=['ID', 'Job_Title', 'Company', 'Posted_date'], inplace=True)
    print(f"🧹 Dropped rows missing required info: {initial_rows} → {len(df_cleaned)} rows.")

    # 3. Remove duplicates
    initial_rows = len(df_cleaned)
    df_cleaned.drop_duplicates(subset=['Company', 'Job_Title', 'Location'], keep='first', inplace=True)
    print(f"🧹 Removed duplicates: {initial_rows} → {len(df_cleaned)} rows.")

    # 4. Add static values if missing
    df_cleaned['Country'] = "Uzbekistan"
    df_cleaned['Source'] = "hh.uz"

    # 5. Reindex columns for DB insert
    required_columns = [
        'ID', 'Posted_date', 'Job_Title_from_List', 'Job_Title', 'Company', 
        'Company_Logo_URL', 'Country', 'Location', 'Skills', 'Salary_Info', 'Source'
    ]
    final_df = df_cleaned.reindex(columns=required_columns, fill_value='N/A')

    # 6. Save final cleaned file
    os.makedirs("Data", exist_ok=True)
    final_df.to_csv(final_csv_path, index=False, encoding='utf-8')
    print(f"✅ Final cleaned data ({len(final_df)} rows) saved to '{final_csv_path}'")

# --- END OF FILE Matched_data.py ---


# --- from push_to_data_base.py ---
import pandas as pd
import pyodbc
import sys
import os
import traceback

def insert_data_to_sql():
    csv_file = os.path.join("Data", "cleaned_job_titles_final.csv")  # ✅ путь к Data/

    conn = None
    cursor = None

    try:
        print(f"\n--- Loading data from {csv_file} ---")
        if not os.path.exists(csv_file):
             print(f"❌ ERROR: Final cleaned CSV file not found at '{csv_file}'. Did Matched_data.py run successfully and create output?")
             return

        job_data = pd.read_csv(csv_file, keep_default_na=False, encoding='utf-8')
        print(f"📥 Loaded {len(job_data)} rows.")
        print(f"📊 Columns: {job_data.columns.tolist()}")

        if job_data.empty:
            print("⚠️ Final CSV file is empty. No data to insert.")
            return

        column_mapping = {
            'ID': 'ID', 'Posted_date': 'Posted_date', 'Job_Title_from_List': 'Job_Title_from_List',
            'Job_Title': 'Job_Title', 'Company': 'Company', 'Company_Logo_URL': 'Company_Logo_URL',
            'Country': 'Country', 'Location': 'Location', 'Skills': 'Skills',
            'Salary_Info': 'Salary_Info', 'Source': 'Source'
        }

        missing_csv_cols = [csv_col for csv_col in column_mapping.keys() if csv_col not in job_data.columns]
        if missing_csv_cols:
            print(f"❌ ERROR: The final CSV file '{csv_file}' is missing required columns: {missing_csv_cols}")
            return

        columns_to_fill_na = ['Salary_Info', 'Company_Logo_URL', 'Skills']
        for csv_col_name in columns_to_fill_na:
             if csv_col_name in job_data.columns:
                 job_data[csv_col_name] = job_data[csv_col_name].astype(str).fillna('N/A').replace('', 'N/A')

        print("\n--- Connecting to SQL Server ---")
        conn = pyodbc.connect(
            'Driver={ODBC Driver 17 for SQL Server};' # <<< MODIFIED: USING MODERN DRIVER
            # If you installed ODBC Driver 18, use 'Driver={ODBC Driver 18 for SQL Server};'
            # If you don't have 17 or 18, you MUST install one. Fallback to {SQL Server} is last resort.
            'Server=POWERBI-1\\IT_JOBS;'
            'Database=IT_JOBS;'
            'UID=sa;'
            'PWD=maab2024;'
            'Connection Timeout=30;'
        )
        cursor = conn.cursor()
        print("✅ Connected.")

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

        if not job_data.empty:
            existing_ids_to_check = job_data['ID'].astype(str).unique().tolist()
            if existing_ids_to_check:
                placeholders = ','.join(['?'] * len(existing_ids_to_check))
                # Ensure IDs are not empty strings or problematic before adding to query
                valid_ids_to_delete = [id_val for id_val in existing_ids_to_check if id_val and id_val.strip()]
                if valid_ids_to_delete:
                    placeholders = ','.join(['?'] * len(valid_ids_to_delete))
                    delete_query = f"DELETE FROM dbo.JobListings WHERE ID IN ({placeholders})"
                    try:
                        print(f"Attempting to delete {len(valid_ids_to_delete)} existing valid IDs before insert...")
                        cursor.execute(delete_query, *valid_ids_to_delete)
                        conn.commit()
                        print(f"Deleted {cursor.rowcount} rows for IDs to be inserted.")
                    except pyodbc.Error as del_err:
                        conn.rollback()
                        print(f"❌ Error deleting existing IDs: {del_err}")
                else:
                    print("No valid IDs found in CSV to perform pre-deletion.")


        insert_query = """
        INSERT INTO dbo.JobListings
        (ID, Posted_date, Job_Title_from_List, Job_Title, Company, Company_Logo_URL, Country, Location, Skills, Salary_Info, Source)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        rows_to_insert = []
        print("\n--- Preparing data for insertion ---")

        for idx, job in job_data.iterrows():
             job_id_val = "N/A"
             try:
                 job_id_val = str(job['ID']).strip()
                 if not job_id_val: # Handle empty string ID after strip
                    print(f"⚠️ Row {idx} has an empty ID. Skipping this row.")
                    continue


                 posted_date_val = None
                 raw_date_str = str(job.get('Posted_date', '')).strip()
                 if raw_date_str and raw_date_str.lower() != 'n/a':
                     try:
                         dt_intermediate = pd.to_datetime(raw_date_str, format='%m/%d/%Y', errors='raise')
                         posted_date_val = dt_intermediate.date()
                     except ValueError:
                         try:
                             dt_intermediate = pd.to_datetime(raw_date_str, errors='raise')
                             posted_date_val = dt_intermediate.date()
                         except ValueError:
                             pass
                     except Exception:
                         pass

                 title_list_val = str(job.get('Job_Title_from_List', 'N/A')).strip()
                 title_val = str(job.get('Job_Title', 'N/A')).strip()
                 company_val = str(job.get('Company', 'N/A')).strip()
                 logo_url_val = str(job.get('Company_Logo_URL', 'N/A')).strip()
                 country_val = str(job.get('Country', 'N/A')).strip()
                 location_val = str(job.get('Location', 'N/A')).strip()
                 skills_val = str(job.get('Skills', 'N/A')).strip()
                 salary_val = str(job.get('Salary_Info', 'N/A')).strip()
                 source_val = str(job.get('Source', 'N/A')).strip()

                 logo_url_val = logo_url_val if logo_url_val else "N/A"

                 row_data = (
                     job_id_val, posted_date_val, title_list_val, title_val, company_val,
                     logo_url_val, country_val, location_val, skills_val, salary_val, source_val
                 )
                 rows_to_insert.append(row_data)

             except KeyError as ke:
                 print(f"❌ ERROR: KeyError preparing row {idx}. Column: {ke}")
                 continue
             except Exception as row_error:
                 print(f"❌ ERROR: Failed preparing row {idx} (ID: {job_id_val}). Type: {type(row_error).__name__}, Msg: {row_error}")
                 exc_type, exc_obj, exc_tb = sys.exc_info(); fname = exc_tb.tb_frame.f_code.co_filename; line_no = exc_tb.tb_lineno
                 print(f"   In {fname}, line {line_no}")
                 continue

        if rows_to_insert:
            print(f"\n--- Inserting {len(rows_to_insert)} prepared rows into SQL Server ---")
            try:
                cursor.fast_executemany = True # <<< MODIFIED: SET BACK TO TRUE
                cursor.executemany(insert_query, rows_to_insert)
                conn.commit()
                print(f"✅ Successfully inserted/committed {len(rows_to_insert)} rows.")
            except pyodbc.IntegrityError as ie:
                conn.rollback()
                print(f"❌ Database Integrity Error during batch insert: {ie}")
                print(f"   SQLSTATE: {ie.args[0]}")
                print(f"   Message: {ie.args[1]}")
            except pyodbc.Error as db_error:
                conn.rollback()
                print(f"❌ Database Error during batch insert: {db_error}")
                if db_error.args:
                    print(f"   SQLSTATE: {db_error.args[0]}")
                    if len(db_error.args) > 1:
                         print(f"   Message: {db_error.args[1]}")
            except Exception as exec_error:
                 conn.rollback()
                 print(f"❌ Unexpected Error during batch insert (executemany): {exec_error}")
                 traceback.print_exc()
        else:
            print("⚠️ No rows were successfully prepared for insertion (check cleaning steps in Matched_data.py).")

    except FileNotFoundError:
        print(f"❌ ERROR: Final CSV file not found at '{csv_file}'")
    except pd.errors.EmptyDataError:
         print(f"❌ ERROR: Final CSV file '{csv_file}' is empty.")
    except pyodbc.Error as db_conn_error: # Catches connection errors, driver errors
        print(f"❌ Database System Error (e.g., connection, driver): {db_conn_error}")
        if hasattr(db_conn_error, 'args') and db_conn_error.args:
            print(f"   SQLSTATE: {db_conn_error.args[0]}") # e.g., '08001' for client unable to establish connection
            if len(db_conn_error.args) > 1:
                print(f"   Message: {db_conn_error.args[1]}") # e.g., '[Microsoft][ODBC Driver 17 for SQL Server]TCP Provider: No connection could be made...'
        else:
            traceback.print_exc()
    except Exception as e:
        print(f"❌ An unexpected error occurred in insert_data_to_sql: {e}")
        traceback.print_exc()

    finally:
        if cursor: cursor.close()
        if conn: conn.close(); print("✅ Connection closed.")

# Example call (if running this script directly):
# if __name__ == "__main__":
#    insert_data_to_sql()

# --- from database.py ---
# database.py
import pandas as pd
import pyodbc
import traceback
import config

def insert_to_sql(df: pd.DataFrame, db_config: dict):
    """
    Connects to SQL Server and inserts the DataFrame data.
    Deletes existing records with the same ID before inserting.

    Args:
        df (pd.DataFrame): The DataFrame to insert.
        db_config (dict): Contains connection parameters and target table name.

    Returns:
        None
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
                ID NVARCHAR(100) PRIMARY KEY,
                Posted_date DATE NULL,
                Job_Title_from_List NVARCHAR(255) NULL,
                Job_Title NVARCHAR(255) NULL,
                Company NVARCHAR(255) NULL,
                Company_Logo_URL NVARCHAR(MAX) NULL,
                Country NVARCHAR(100) NULL,
                Location NVARCHAR(255) NULL,
                Skills NVARCHAR(MAX) NULL,
                Salary_Info NVARCHAR(255) NULL,
                Source NVARCHAR(255) NULL,
                IngestionTimestamp DATETIME2 DEFAULT GETDATE()
            )
        END
        """
        cursor.execute(create_table_query)
        conn.commit()

        # Delete existing records to prevent primary key violations
        ids_to_insert = df['ID'].dropna().tolist()
        if ids_to_insert:
            placeholders = ','.join(['?'] * len(ids_to_insert))
            delete_query = f"DELETE FROM {db_config['table_name']} WHERE ID IN ({placeholders})"
            cursor.execute(delete_query, *ids_to_insert)
            conn.commit()
            print(f"Deleted {cursor.rowcount} old records to prepare for new insertion.")

        # Ensure correct column order
        columns = [
            'ID', 'Posted_date', 'Job_Title_from_List', 'Job_Title', 'Company',
            'Company_Logo_URL', 'Country', 'Location', 'Skills', 'Salary_Info', 'Source'
        ]
        df = df[columns]

        # Clean Posted_date column
        df['Posted_date'] = pd.to_datetime(df['Posted_date'], errors='coerce')
        df['Posted_date'] = df['Posted_date'].apply(lambda x: x.date() if pd.notnull(x) else None)

        # Prepare data for insertion
        rows_to_insert = df.values.tolist()

        insert_query = f"""
        INSERT INTO {db_config['table_name']} (
            ID, Posted_date, Job_Title_from_List, Job_Title, Company, 
            Company_Logo_URL, Country, Location, Skills, Salary_Info, Source
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

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
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()
            print("--- Connection to SQL Server closed. ---")


