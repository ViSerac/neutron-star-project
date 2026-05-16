import pandas as pd
from psrqpy import QueryATNF
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

def fetch_atnf_data():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    query = QueryATNF(params=[
        'JNAME',
        'RAJ',
        'DECJ',
        'DIST',
        'P0',
        'P1',
    ])
 
    df = query.pandas
 
    df.rename(columns={"JNAME": "NS_NAME", "P0": "P", "P1": "PDOT"}, inplace=True)
 
    m7_overlap = ["J0720-3125", "J2143+0654", "J1308+2127", "J1856-3754", "J1605+3249", "J0806-4123", "J0420-5022"]
    df = df[~df["NS_NAME"].isin(m7_overlap)]
 
    output_path = DATA_DIR / "atnf_raw.parquet"
    df.to_parquet(output_path, index=False)
    print(f"fetch len ATNF: {len(df)}")
    print(f"Saved raw ATNF data to {output_path}")
 
 
if __name__ == "__main__":
    fetch_atnf_data()