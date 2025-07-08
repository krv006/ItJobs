import os

import pandas as pd


def to_csv(titles: list, file_name: str = "Title.csv"):
    data = {"Title": titles}

    df = pd.DataFrame(data)

    file_exists = os.path.exists(file_name)
    df.to_csv(
        file_name,
        index=False,
        mode="a",
        header=not file_exists
    )

    if file_exists:
        print(f"Data appended to the existing file '{file_name}'.")
    else:
        print(f"File '{file_name}' created with header.")
