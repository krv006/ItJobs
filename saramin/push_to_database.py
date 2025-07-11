# push_to_database.py
import pyodbc


def get_connection():
    return pyodbc.connect(
        'Driver={SQL Server};'
        'Server=WIN-LORQJU2719N;'
        'Database=IT_JOBS;'
        'Trusted_Connection=yes;'
    )


def create_table_if_not_exists():
    conn = get_connection()
    cursor = conn.cursor()

    create_table_query = """
        IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'JobListings')
        BEGIN
            CREATE TABLE JobListings (
                ID INT,
                Posted_date NVARCHAR(100),
                Job_Title_from_List NVARCHAR(255),
                Job_Title NVARCHAR(255),
                Company NVARCHAR(255),
                Company_Logo_URL NVARCHAR(MAX),
                Country NVARCHAR(50),
                Location NVARCHAR(255),
                Skills NVARCHAR(MAX),
                Salary_Info NVARCHAR(255),
                Source NVARCHAR(255)
            )
        END
    """
    cursor.execute(create_table_query)
    conn.commit()
    cursor.close()
    conn.close()


# Call once before inserting
create_table_if_not_exists()


def insert_single_row_to_sql(row):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        insert_query = """
            INSERT INTO JobListings (
                ID, Posted_date, Job_Title_from_List, Job_Title, Company, Company_Logo_URL,
                Country, Location, Skills, Salary_Info, Source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        row_id = int(row.get('ID', 0)) if str(row.get('ID', '')).isdigit() else 0

        cursor.execute(insert_query,
                       row_id,
                       row.get('Posted_date', 'N/A'),
                       row.get('Job Title from List', 'N/A'),
                       row.get('Job Title', 'N/A'),
                       row.get('Company', 'N/A'),
                       row.get('Company Logo URL', 'N/A'),
                       row.get('Country', 'N/A'),
                       row.get('Location', 'N/A'),
                       row.get('Skills', 'N/A'),
                       row.get('Salary Info', 'N/A'),
                       row.get('Source', 'N/A'))

        conn.commit()
        cursor.close()
        conn.close()

    except Exception as e:
        print(f"⚠️ Ma'lumot insert qilinmadi: {e}")
