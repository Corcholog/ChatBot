import pandas as pd

# Load the CSV into a Pandas DataFrame
df = pd.read_csv('C:/Users/Julian/Desktop/cork/games-data.csv')

# Analyze each column
for column in df.columns:
    if df[column].dtype == 'object':  # Textual data
        max_length = df[column].str.len().max()
        if max_length > 255:
            print(f"{column}: TEXT")
        else:
            print(f"{column}: VARCHAR({max_length})")
    elif df[column].dtype == 'int64':  # Integer data
        print(f"{column}: INTEGER")
    elif df[column].dtype == 'float64':  # Float data
        max_val = df[column].max()
        min_val = df[column].min()
        if min_val >= -32768 and max_val <= 32767:
            print(f"{column}: SMALLINT")
        elif min_val >= -2147483648 and max_val <= 2147483647:
            print(f"{column}: INTEGER")
        else:
            print(f"{column}: BIGINT")


