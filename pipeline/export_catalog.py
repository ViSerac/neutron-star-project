import json
import math
import pandas as pd

ATNF_PATH   = "../data/atnf_raw.parquet"
MCGILL_PATH = "../data/mcgill_raw.parquet"
OUTPUT_PATH = "../site/data/NS_catalog_full.json"

def clean(val):
    if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
        return None
    return val

def export_catalog():
    df_atnf   = pd.read_parquet(ATNF_PATH)
    df_mcgill = pd.read_parquet(MCGILL_PATH)

    df_atnf.rename(columns={"P0_ERR": "P_ERR", "P1_ERR": "PDOT_ERR"}, inplace=True)
    df_atnf["source_catalog"] = "ATNF"

    df_mcgill.rename(columns={"Period_Err": "P_ERR", "Pdot_Err": "PDOT_ERR"}, inplace=True)
    df_mcgill["source_catalog"] = "McGill"

    df = pd.concat([df_atnf, df_mcgill], ignore_index=True)

    records = [{k: clean(v) for k, v in row.items()} for row in df.to_dict(orient="records")]

    with open(OUTPUT_PATH, "w") as f:
        json.dump(records, f)

    print(f"Export successful - {len(records)} records -> {OUTPUT_PATH}")

if __name__ == "__main__":
    export_catalog()
