import google.generativeai as genai
import json
from Title_tocsv import to_csv

key = "AIzaSyD3L_SL8M7HT2KGALhaw1A4DrQ1dNDTuXI"

def identify_tite(titles : str, skills : str):
    # Create a more robust input string
    prompt = f"""
You are an expert in job title matching. Match the provided job titles and skills to the closest job title from the predefined list below. 

### Predefined Job Titles (Only valid outputs):
- Backend developer
- Frontend developer
- Data analyst
- Data engineer
- Data scientist
- AI engineer
- Android developer
- IOS developer
- Game developer
- DevOps engineer
- IT project manager
- Network engineer
- Cybersecurity Analyst
- Cloud Architect
- Full stack developer

### Rules:
1. If **skills** are provided, match based on both job title and skills.
2. If **skills are missing or empty or N/A**, match based **only** on the job title.
3. If the **job title is unclear or vague**, but skills closely match a predefined role, use the skills to determine the best title.
4. If **neither the title nor the skills match**, return "unknown".
5. You **MUST** return only the predefined job titles in a comma-separated format. Do not invent or hallucinate new titles.
6. The number of output titles **MUST** match the number of input job titles. If no valid match is found for a title, return "unknown" for that position.

### Input:
Title : {titles}
skills : {skills}

### Output:
Return only the matched job titles in a comma-separated format (e.g., Data analyst, Data engineer, unknown).
"""

    # Configure the API key
    genai.configure(api_key=key)

    # Create a generative model
    model = genai.GenerativeModel("gemini-1.5-flash")

    try:
        # Get the response from the model
        response = model.generate_content(prompt)

        # Extract the text more robustly
        output_text = response.text.strip()
        output_list = [item.strip() for item in output_text.split(",")]
        print(output_list)
        
        print(len(output_list))

        to_csv(titles=output_list)



    except genai.APIError as e:
        print(f"API Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
