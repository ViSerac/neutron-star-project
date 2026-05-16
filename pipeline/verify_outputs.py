import json
import sys

files = [
    "docs/data/NS_db_full.json",
    "docs/data/NS_catalog_full.json",
]

errors = []
for path in files:
    with open(path) as f:
        data = json.load(f)
    count = len(data) if isinstance(data, list) else len(data.get("records", []))
    print(f"{path}: {count} records")
    if count < 1000:
        errors.append(f"ERROR: {path} has only {count} records — expected ~4000+")

if errors:
    for e in errors:
        print(e)
    sys.exit(1)
else:
    print("Verification passed.")
