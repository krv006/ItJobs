def insert_data_to_sql():
    import pyodbc
    import pandas as pd

    try:
        print("📁 CSV fayl o‘qilmoqda...")
        final_dataframe = pd.read_csv("cleaned_job_titles.csv", keep_default_na=False, encoding='utf-8')

        if final_dataframe.empty:
            print("❌ CSV faylda hech qanday ma’lumot yo‘q.")
            return

        print(f"✅ {len(final_dataframe)} ta yozuv yuklandi.")

        # NaNlarni tozalash
        for col in ['Salary Info', 'Company Logo URL', 'Location', 'Posted_date']:
            if col in final_dataframe.columns:
                final_dataframe[col] = final_dataframe[col].fillna('N/A').replace('', 'N/A')

        # Ulanish
        conn = pyodbc.connect(
            'Driver={SQL Server};'
            'Server=WIN-LORQJU2719N;'
            'Database=IT_JOBS;'
            'Trusted_Connection=yes;'
        )

        cursor = conn.cursor()

        print("🗃 Jadval tekshirilmoqda...")
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

        print("📥 Ma’lumotlar bazaga yozilmoqda...")
        insert_query = """
            INSERT INTO JobListings (
                ID, Posted_date, Job_Title_from_List, Job_Title, Company, Company_Logo_URL,
                Country, Location, Skills, Salary_Info, Source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        for i, row in final_dataframe.iterrows():
            try:
                cursor.execute(insert_query,
                               int(row['ID']),
                               row['Posted_date'],
                               row['Job Title from List'],
                               row['Job Title'],
                               row['Company'],
                               row['Company Logo URL'],
                               row['Country'],
                               row['Location'],
                               row['Skills'],
                               row['Salary Info'],
                               row['Source']
                               )
            except Exception as e:
                print(f"⚠️ Row {i} insert qilinmadi: {e}")

        conn.commit()
        cursor.close()
        conn.close()

        print("🎉 Barcha ma’lumotlar bazaga saqlandi!")

    except Exception as e:
        print(f"❌ Bazaga saqlashda xatolik: {e}")
