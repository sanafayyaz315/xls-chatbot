import pandas as pd

# load excel or csv files
def load_file(filepath):
    if filepath.endswith('.csv'):
        df = pd.read_csv(filepath)
    elif filepath.endswith('.xls') or filepath.endswith('.xlsx'):
        df = pd.read_excel(filepath)
    else:
        raise ValueError("Unsupported file type")
    return df

# preprocess df
def preprocess_data(df):
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
    return df



 
