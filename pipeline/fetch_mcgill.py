import pandas as pd
import os, pathlib

os.chdir(pathlib.Path(__file__).parent)

mcgill_csv = "https://www.physics.mcgill.ca/~pulsar/magnetar/TabO1.csv"
output_path = "../data/mcgill_raw.parquet"

def fetch_mcgill_data():
    df = pd.read_csv(mcgill_csv)
    df.rename(columns={"Dist": "DIST", "Name": "NS_NAME", "RA": "RAJ", "Decl": "DECJ", "RA_Err": "RAJ_ERR", "Decl_Err": "DECJ_ERR", "Period": "P", "Pdot": "PDOT"}, inplace=True)
    df.to_parquet(output_path, index=False)
    
    print(f"Saved raw McGill data to {output_path}")
    
if __name__ == "__main__":
    fetch_mcgill_data()