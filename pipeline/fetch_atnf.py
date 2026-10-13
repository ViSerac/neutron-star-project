import pandas as pd
import numpy as np
from psrqpy import QueryATNF
from astropy.coordinates import SkyCoord
from astropy import units as u
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"

def fetch_atnf_data():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    query = QueryATNF(params=['JNAME','RAJ','DECJ','DIST','P0','P1','TYPE'])
    df = query.pandas
    df.rename(columns={"JNAME":"NS_NAME","P0":"P","P1":"PDOT"}, inplace=True)

    m7_overlap = ["J0720-3125","J2143+0654","J1308+2127","J1856-3754","J1605+3249","J0806-4123","J0420-5022"]
    cco_overlap = ["J0821-4300","J1210-5226","J1852+0040"]
    mcgill_overlap = ["J1846-0258"]
    # 1A 0535-66, taken from the LMC HMXB catalogue (mc_hmxb.py)
    xrb_overlap = ["J0535-66"]

    timing_cols = ["NS_NAME", "P", "P0_ERR", "PDOT", "P1_ERR"]
    df[df["NS_NAME"].isin(m7_overlap + cco_overlap)][timing_cols].to_parquet(
        DATA_DIR / "atnf_overlap_timing.parquet", index=False)

    df = df[~df["NS_NAME"].isin(m7_overlap + cco_overlap + mcgill_overlap + xrb_overlap)]

    # ATNF tags magnetars as AXP under J-names; McGill lists the same objects
    # under their historical names, so name matching can't dedupe them.
    is_magnetar = df["TYPE"].fillna("").astype(str).str.contains("AXP")
    df = df[~is_magnetar].drop(columns=["TYPE"])

    # Convert RAJ/DECJ to decimal degrees — format-independent across psrqpy versions
    raj_str  = df["RAJ"].astype(str).str.replace(":", " ", regex=False)
    decj_str = df["DECJ"].astype(str).str.replace(":", " ", regex=False)
    coords = SkyCoord(ra=raj_str.values, dec=decj_str.values,
                      unit=(u.hourangle, u.deg), frame="icrs")
    df["RAJ"]  = coords.ra.deg
    df["DECJ"] = coords.dec.deg

    output_path = DATA_DIR / "atnf_raw.parquet"
    df.to_parquet(output_path, index=False)
    print(f"Saved raw ATNF data to {output_path}")

if __name__ == "__main__":
    fetch_atnf_data()
