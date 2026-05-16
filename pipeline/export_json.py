from pathlib import Path

import json
import math
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
SITE_DATA_DIR = BASE_DIR.parent / "docs" / "data"
SITE_DATA_DIR.mkdir(parents=True, exist_ok=True)

INPUT_FILE = DATA_DIR / "NS_db_full.parquet"
OUTPUT_FILE = SITE_DATA_DIR / "NS_db_full.json"


def clean(val):
    if isinstance(val, float) and (
        math.isnan(val) or math.isinf(val)
    ):
        return None

    return val


def export_json(records, output_file):
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False)


if __name__ == "__main__":
    df = pd.read_parquet(INPUT_FILE)

    columns = ["NS_NAME", "RAJ", "RAJ_ERR", "DECJ", "DECJ_ERR", "DIST", "P", "PDOT", "x", "y", "z", "galaxy", "type", "source_catalog", "wiki_url"]
    
    df = df[columns]

    records = [
        {k: clean(v) for k, v in row.items()}
        for row in df.to_dict(orient="records")
    ]

    export_json(records, OUTPUT_FILE)

    print(f"Export successful: {OUTPUT_FILE}")