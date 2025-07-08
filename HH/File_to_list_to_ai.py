import os
import re
import time

import pandas as pd

from Title_Identify_with_ai import identify_title


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

        batch_size = 10
        for i in range(0, len(cleaned_titles), batch_size):
            titles_batch = cleaned_titles[i:i + batch_size]
            skills_batch = skills[i:i + batch_size]
            print(f"\nProcessing AI batch {i // batch_size + 1}...")
            try:
                identify_title(titles=titles_batch, skills=skills_batch)
                print(f"Sent batch to AI: {titles_batch}")
            except Exception as ai_call_error:
                print(f"ERROR calling identify_title for batch starting at index {i}: {ai_call_error}")

            time.sleep(5)
        print("\nFinished AI processing.")

    except FileNotFoundError:
        print(f"Error in give_to_ai: File not found at '{raw_csv_path}'")
    except Exception as e:
        print(f"An error occurred in give_to_ai: {e}")
        import traceback
        traceback.print_exc()
