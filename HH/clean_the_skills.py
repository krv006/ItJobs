import os

import pandas as pd


def clean_hard_skills(csv_file, column_name="Hard Skills", unwanted_skills=["Project", "Office"]):
    df = pd.read_csv(csv_file)

    def clean_skills(skills):
        if pd.isna(skills) or skills.strip() == "":
            return "N/A"
        cleaned_skills = [skill.strip() for skill in skills.split(",") if skill.strip() not in unwanted_skills]
        return ", ".join(cleaned_skills) if cleaned_skills else "N/A"

    df[column_name] = df[column_name].apply(clean_skills)

    cleaned_file_path = os.path.join(os.path.dirname(csv_file), "cleaned_" + os.path.basename(csv_file))

    df.to_csv(cleaned_file_path, index=False)

    print(f"✅ Data cleaning complete! Saved as '{cleaned_file_path}'")
    return df


cleaned_df = clean_hard_skills(r"Data\job_data.csv")
