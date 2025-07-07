import pandas as pd
import os

def to_csv(titles: list, file_name: str = "Title.csv"):
    # Create a dictionary with the data
    data = {"Title": titles}
    
    # Convert the dictionary into a DataFrame
    df = pd.DataFrame(data)
    
    # Check if the file already exists
    file_exists = os.path.exists(file_name)
    
    # Write to the file, appending if it exists
    df.to_csv(
        file_name,
        index=False,
        mode="a",  # Append mode
        header=not file_exists  # Write header only if the file does not exist
    )
    
    if file_exists:
        print(f"Data appended to the existing file '{file_name}'.")
    else:
        print(f"File '{file_name}' created with header.")

