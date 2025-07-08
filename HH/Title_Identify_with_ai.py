import google.generativeai as genai

from Title_to_csv import to_csv

key = "AIzaSyDAhcvX5-iAwOk8XQXZKFQdcQVszvwnTXI"


def identify_title(titles: str, skills: str):
    prompt = f"""
You are an expert in job title matching. Match the provided job titles and skills to the closest job title from the predefined list below. 

### Predefined Job Titles (Only valid outputs):
- Backend Developer
- Frontend Developer
- Full Stack Developer
- Data Analyst
- Data Engineer
- Data Scientist
- AI Engineer
- Android Developer
- IOS Developer
- Game Developer
- DevOps Engineer
- IT Project Manager
- Network Engineer
- Cybersecurity Analyst
- Cloud Architect

### Rules:
1. If **skills** are provided, match based on both job title and skills using keyword-based matching. For example:
   - Keywords like "TensorFlow", "PyTorch", or "machine learning" map to "AI Engineer".
   - Keywords like "SQL", "ETL", or "data pipelines" map to "Data Engineer".
   - Keywords like "JavaScript" and "React" map to "Frontend Developer".
2. If **skills are missing, empty, or N/A**, match based **only** on the job title.
3. If the **job title is unclear or vague** (e.g., "Engineer"), but skills closely match a predefined role, prioritize skills to determine the best title.
4. If **neither the title nor the skills match**, return "unknown".
5. The number of output titles **MUST** match the number of input job titles. If no valid match is found for a title, return "unknown" for that position.
6. **Output Format:** 
   - Return only the matched job titles in a **comma-separated format** (e.g., Data analyst, Data engineer, unknown).
   - Do NOT invent new titles or hallucinate outputs.
7.  !!! if the title name not match with  provided titles just rerutn "unknown" and if the job title contains same word with provided titles it does not mean it related to
    to this title please pay more attantion to meaning and skills (if available)  not to same words

### Input:
Title: {titles}
Skills: {skills}

### Output:
Return the matched job titles in a comma-separated format, ensuring the number of titles matches the input.
"""

    genai.configure(api_key=key)

    model = genai.GenerativeModel("gemini-1.5-flash")

    try:
        response = model.generate_content(prompt)

        output_text = response.text.strip()
        if not output_text:
            raise ValueError("Empty response from the API.")

        output_list = [item.strip() for item in output_text.split(",")]

        if len(output_list) != len(titles):
            raise ValueError("Input and output not at same size")

        print(output_list)
        print(f"Number of matched titles: {len(output_list)}")

        to_csv(titles=output_list)

    except genai.APIError as e:
        print(f"API Error: {e}")
    except ValueError as e:
        print(f"Validation Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
