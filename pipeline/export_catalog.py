import json, math
import numpy as np
import pandas as pd
from astropy.coordinates import SkyCoord
from astropy import units as u
from pathlib import Path
from datetime import datetime, timezone

DATA_DIR      = Path(__file__).resolve().parent / "data"
SITE_DATA_DIR = Path(__file__).resolve().parent.parent / "docs" / "data"

def clean(val):
    if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
        return None
    return val

if __name__ == "__main__":
    SITE_DATA_DIR.mkdir(parents=True, exist_ok=True)
    df_atnf   = pd.read_parquet(DATA_DIR / "atnf_raw.parquet")
    df_mcgill = pd.read_parquet(DATA_DIR / "mcgill_raw.parquet")
    df_atnf.rename(columns={"P0_ERR":"P_ERR","P1_ERR":"PDOT_ERR"}, inplace=True)
    df_atnf["source_catalog"] = "ATNF"
    df_atnf["type"] = "pulsar"
    df_mcgill.rename(columns={"Period_Err":"P_ERR","Pdot_Err":"PDOT_ERR"}, inplace=True)
    df_mcgill["source_catalog"] = "McGill"
    # McGill positions are sexagesimal strings; the other sources are decimal degrees
    has_pos = df_mcgill["RAJ"].notna() & df_mcgill["DECJ"].notna()
    pos = SkyCoord(ra=df_mcgill.loc[has_pos, "RAJ"].astype(str).values,
                   dec=df_mcgill.loc[has_pos, "DECJ"].astype(str).values,
                   unit=(u.hourangle, u.deg), frame="icrs")
    df_mcgill["RAJ"] = df_mcgill["RAJ"].astype(object)
    df_mcgill["DECJ"] = df_mcgill["DECJ"].astype(object)
    df_mcgill.loc[has_pos, "RAJ"] = pos.ra.deg
    df_mcgill.loc[has_pos, "DECJ"] = pos.dec.deg
    df_mcgill["type"] = np.select(
        [df_mcgill["NS_NAME"].str.endswith(" ##"), df_mcgill["NS_NAME"].str.endswith(" #")],
        ["pulsar_outburst_2006", "candidate_magnetar"], default="magnetar")
    df_m7_cco = pd.read_parquet(DATA_DIR / "m7_and_cco_full.parquet")
    df_m7_cco = df_m7_cco[["NS_NAME", "RAJ", "DECJ", "DIST", "P", "P0_ERR", "PDOT", "P1_ERR", "source_catalog", "type"]]
    df_m7_cco = df_m7_cco.rename(columns={"P0_ERR":"P_ERR","P1_ERR":"PDOT_ERR"})
    df_xrb = pd.read_parquet(DATA_DIR / "xrb_raw.parquet")
    df_xrb = df_xrb[["NS_NAME", "RAJ", "DECJ", "DIST", "P", "source_catalog", "type", "xray_type"]]
    df_extra = pd.read_parquet(DATA_DIR / "extra_raw.parquet")
    df_extra = df_extra[["NS_NAME", "RAJ", "DECJ", "DIST", "P", "source_catalog", "type", "galaxy"]]
    df_extra = df_extra.rename(columns={"galaxy": "host_galaxy"})
    df_mc = pd.read_parquet(DATA_DIR / "mc_hmxb_raw.parquet")
    df_mc = df_mc[["NS_NAME", "RAJ", "DECJ", "DIST", "P", "source_catalog", "type"]]
    df = pd.concat([df_atnf, df_mcgill, df_m7_cco, df_xrb, df_mc, df_extra], ignore_index=True)

    # galaxy is known for objects placed in 3D (those with a usable distance) and for
    # extragalactic objects whose host is listed explicitly
    placed = pd.read_parquet(DATA_DIR / "NS_db_full.parquet")[["NS_NAME", "source_catalog", "galaxy"]]
    df = df.merge(placed, on=["NS_NAME", "source_catalog"], how="left")
    df["galaxy"] = df["galaxy"].fillna(df.pop("host_galaxy"))
    records = [{k: clean(v) for k,v in row.items()} for row in df.to_dict(orient="records")]
    output = {
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "records": records,
    }
    with open(SITE_DATA_DIR / "NS_catalog_full.json", "w") as f:
        json.dump(output, f)
    print(f"Export successful: {len(records)} records")
