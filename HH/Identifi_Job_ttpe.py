import re


def identify_job_type(job_title: str) -> str:
    cleaned_title = re.sub(r'[\(\)\-"“”]', ' ', job_title).lower()

    if re.search(r'\btrainee\b', cleaned_title):
        return "Trainee"
    elif re.search(r'\bintern\b', cleaned_title):
        return "Intern"
    else:
        return "Work"
