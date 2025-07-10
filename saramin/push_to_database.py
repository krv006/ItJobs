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
                # ID ni xavfsiz int ga aylantirish (agar bo‘sh bo‘lsa, 0 beriladi)
                row_id = int(row['ID']) if str(row['ID']).isdigit() else 0

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

                conn.commit()  # Har bir muvaffaqiyatli yozuvdan keyin commit

            except Exception as e:
                print(f"⚠️ Row {i} insert qilinmadi: {e}")

        cursor.close()
        conn.close()

        print("🎉 Barcha ma’lumotlar bazaga saqlandi!")

    except Exception as e:
        print(f"❌ Bazaga saqlashda xatolik: {e}")
