import json, math
import pandas as pd
from pathlib import Path
from datetime import datetime, timezone

DATA_DIR      = Path(__file__).resolve().parent / "data"
SITE_DATA_DIR = Path(__file__).resolve().parent.parent / "docs" / "data"

COLUMNS = ["NS_NAME","RAJ","RAJ_ERR","DECJ","DECJ_ERR","DIST","P","PDOT","x","y","z","galaxy","type","source_catalog","wiki_url"]

def clean(val):
    if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
        return None
    return val

if __name__ == "__main__":
    SITE_DATA_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_parquet(DATA_DIR / "NS_db_full.parquet")
    cols = [c for c in COLUMNS if c in df.columns]
    df = df[cols]
    records = [{k: clean(v) for k,v in row.items()} for row in df.to_dict(orient="records")]
    with open(SITE_DATA_DIR / "NS_db_full.json", "w") as f:
        json.dump(records, f)
    print(f"Export successful: {len(records)} records")
