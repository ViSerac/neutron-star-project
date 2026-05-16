import json
import pandas as pd
import math

filename = "../data/NS_db_full.parquet"

def clean(val):
    if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
        return None
    return val

def export_json(records, filename):
    with open(filename, 'w') as f:
        json.dump(records, f)

if __name__ == "__main__":
    df = pd.read_parquet(filename)
    colunas = ["NS_NAME", "RAJ", "RAJ_ERR", "DECJ", "DECJ_ERR", "DIST", "P", "PDOT", "x", "y", "z", "galaxy", "type", "source_catalog", "wiki_url"]
    df = df[colunas]
    records = [{k: clean(v) for k, v in row.items()} for row in df.to_dict(orient='records')]
    export_json(records, "../site/data/NS_db_full.json")
    print("Export successful")