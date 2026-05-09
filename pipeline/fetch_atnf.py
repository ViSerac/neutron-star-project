from psrqpy import QueryATNF
import pandas as pd
import numpy as np

def fetch_atnf_data(output_path = "../data/atnf_raw.parquet"):
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

    # salvar bruto
    df.to_parquet(output_path, index=False)

    print(f"Saved raw ATNF data to {output_path}")


if __name__ == "__main__":
    fetch_atnf_data()