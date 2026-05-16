from pathlib import Path
from datetime import datetime, timezone

import json
import math
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
SITE_DATA_DIR = BASE_DIR.parent / "site" / "data"

ATNF_PATH = DATA_DIR / "atnf_raw.parquet"
MCGILL_PATH = DATA_DIR / "mcgill_raw.parquet"
OUTPUT_PATH = SITE_DATA_DIR / "NS_catalog_full.json"


def clean(val):
    if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
        return None
    return val


def export_catalog():
    if not ATNF_PATH.exists():
        raise FileNotFoundError(f"Missing ATNF parquet file: {ATNF_PATH}")
    if not MCGILL_PATH.exists():
        raise FileNotFoundError(f"Missing McGill parquet file: {MCGILL_PATH}")

    SITE_DATA_DIR.mkdir(parents=True, exist_ok=True)

    df_atnf = pd.read_parquet(ATNF_PATH)
    df_mcgill = pd.read_parquet(MCGILL_PATH)

    df_atnf.rename(columns={"P0_ERR": "P_ERR", "P1_ERR": "PDOT_ERR"}, inplace=True)
    df_atnf["source_catalog"] = "ATNF"

    df_mcgill.rename(columns={"Period_Err": "P_ERR", "Pdot_Err": "PDOT_ERR"}, inplace=True)
    df_mcgill["source_catalog"] = "McGill"

    df = pd.concat([df_atnf, df_mcgill], ignore_index=True)

    records = [
        {k: clean(v) for k, v in row.items()}
        for row in df.to_dict(orient="records")
    ]

    output = {
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "records": records,
    }

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False)

    print(f"Export successful: {len(records)} records -> {OUTPUT_PATH}")


if __name__ == "__main__":
    export_catalog()