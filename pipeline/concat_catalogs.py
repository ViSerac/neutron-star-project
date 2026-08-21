import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"

def concat_df_atnf():
    df = pd.concat([
        pd.read_parquet(DATA_DIR / "atnf_processed_galactic.parquet"),
        pd.read_parquet(DATA_DIR / "atnf_processed_extragalactic.parquet"),
    ], ignore_index=True)
    df.to_parquet(DATA_DIR / "atnf_full.parquet", index=False)

def concat_df_mcgill():
    df = pd.concat([
        pd.read_parquet(DATA_DIR / "mcgill_processed_galactic.parquet"),
        pd.read_parquet(DATA_DIR / "mcgill_processed_extragalactic.parquet"),
    ], ignore_index=True)
    df.to_parquet(DATA_DIR / "mcgill_full.parquet", index=False)

def concat_df_m7_and_cco():
    df = pd.concat([
        pd.read_parquet(DATA_DIR / "m7_processed.parquet"),
        pd.read_parquet(DATA_DIR / "cco_processed.parquet"),
    ], ignore_index=True)
    df.to_parquet(DATA_DIR / "m7_and_cco_full.parquet", index=False)

def concat_all():
    atnf      = pd.read_parquet(DATA_DIR / "atnf_full.parquet")
    mcgill    = pd.read_parquet(DATA_DIR / "mcgill_full.parquet")
    m7_cco    = pd.read_parquet(DATA_DIR / "m7_and_cco_full.parquet")
    print(f"ATNF: {len(atnf)} | McGill: {len(mcgill)} | M7+CCO: {len(m7_cco)}")
    ns_db = pd.concat([atnf, mcgill, m7_cco], ignore_index=True)
    ns_db.to_parquet(DATA_DIR / "NS_db_full.parquet", index=False)
    print(f"Concat successful: {len(ns_db)} total records")

if __name__ == "__main__":
    concat_df_atnf()
    concat_df_mcgill()
    concat_df_m7_and_cco()
    concat_all()
