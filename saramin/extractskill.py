from job_skills_mapping import tools_list

import re

def extract_skills(text, skills_list=tools_list):
    full_text = " ".join(text).lower()
    extracted_skills = [skill for skill in skills_list if re.search(rf'\b{re.escape(skill.lower())}\b', full_text)]
    if len(extracted_skills)==0:
        return " "
    skills_text = ", ".join(list(set(extracted_skills)))
    return skills_text



