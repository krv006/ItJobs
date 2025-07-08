import re

from Skills_mapping import tools_list


def extract_skills(text, skills_list=tools_list):
    if not isinstance(text, str):
        return "N/A"

    text = text.lower().strip()
    found_skills = set()
    sorted_skills = sorted(skills_list, key=len, reverse=True)

    for skill in sorted_skills:
        pattern = re.compile(rf'(?<!\w){re.escape(skill.lower())}(?!\w)')
        if pattern.search(text):
            found_skills.add(skill)

    return ", ".join(sorted(found_skills)) if found_skills else "N/A"
