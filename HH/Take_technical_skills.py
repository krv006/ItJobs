import pandas as pd

from Extract_skills import extract_skills

df = pd.read_csv("cleaned_job_titles.csv", keep_default_na=False, encoding='utf-8')

df['Skills'] = df['Skills'].apply(
    lambda x: extract_skills(x) if isinstance(x, str) and x.strip() else "N/A"
)

df.to_csv("updated_job_titles.csv", index=False)

print("Skills column updated successfully!")
