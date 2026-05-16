import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

def concat_df_atnf():
    gal_path = DATA_DIR / "atnf_processed_galactic.parquet"
    ext_path = DATA_DIR / "atnf_processed_extragalactic.parquet"
    print(f"Reading galactic from: {gal_path} (exists: {gal_path.exists()})")
    print(f"Reading extragalactic from: {ext_path} (exists: {ext_path.exists()})")
    df_galactic = pd.read_parquet(gal_path)
    df_extragalactic = pd.read_parquet(ext_path)
    print(f"ATNF galactic: {len(df_galactic)} | extragalactic: {len(df_extragalactic)}")
    df_final = pd.concat([df_galactic, df_extragalactic], ignore_index=True)
    df_final.to_parquet(DATA_DIR / "atnf_full.parquet", index=False)

def concat_df_mcgill():
    df_extragalactic = pd.read_parquet(DATA_DIR / "mcgill_processed_extragalactic.parquet")
    df_galactic = pd.read_parquet(DATA_DIR / "mcgill_processed_galactic.parquet")
    df_final = pd.concat([df_galactic, df_extragalactic], ignore_index=True)
    df_final.to_parquet(DATA_DIR / "mcgill_full.parquet", index=False)

def concat_df_m7_and_cco():
    df_m7 = pd.read_parquet(DATA_DIR / "m7_processed.parquet")
    df_cco = pd.read_parquet(DATA_DIR / "cco_processed.parquet")
    df_final = pd.concat([df_m7, df_cco], ignore_index=True)
    df_final.to_parquet(DATA_DIR / "m7_and_cco_full.parquet", index=False)

def concat_all():
    atnf = pd.read_parquet(DATA_DIR / "atnf_full.parquet")
    mcgill = pd.read_parquet(DATA_DIR / "mcgill_full.parquet")
    m7_and_cco = pd.read_parquet(DATA_DIR / "m7_and_cco_full.parquet")
    print(f"ATNF: {len(atnf)} | McGill: {len(mcgill)} | M7+CCO: {len(m7_and_cco)}")
    ns_db = pd.concat([atnf, mcgill, m7_and_cco], ignore_index=True)
    ns_db.to_parquet(DATA_DIR / "NS_db_full.parquet", index=False)
    print(f"Concat successful: {len(ns_db)} total records")

if __name__ == "__main__":
    concat_df_atnf()
    concat_df_mcgill()
    concat_df_m7_and_cco()
    concat_all()