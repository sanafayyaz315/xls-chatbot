# actions

def execute_pandas(action_input, df):
    """
    Takes a python code string and a DataFrame and returns the result after executing the code on the dataframe.
    Example input: "df["customer_id"].nunique().count()"
    """
    return eval(action_input, {'df': df}, {})

# get schema details
def get_schema(df):
    schema = []
    for col in df.columns:
        schema.append({"column_name":col, 
                       "data_type": str(df[col].dtype), 
                       "sample_values": df[col].dropna().unique()[:2].tolist()
        })

    return schema

# if __name__ == "__main__":
    