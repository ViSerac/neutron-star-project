import numpy as np
import pandas as pd
from astropy.coordinates import SkyCoord
from astropy import units as u
from pathlib import Path

from magellanic import disk_distance
from xrb import GALCEN, read_vizier_tsv

DATA_DIR = Path(__file__).resolve().parent / "data"

# Haberl & Sturm 2016 has no name column. Names were matched once in SIMBAD by
# position: the SXP identifier closest to the catalogue spin period (within 2%),
# else the conventional SXP name built from the period. Keyed by catalogue Seq.
SXP_NAMES = {
    "1": "SMC X-1", "3": "SMC X-2", "4": "SXP 2.76", "6": "SXP 5.05", "7": "SXP 6.85",
    "10": "SXP 7.92", "11": "SXP 8.88", "12": "SXP 9.13", "13": "SXP 11.48",
    "14": "SXP 11.6", "15": "SXP 11.87", "16": "SXP 15.3", "18": "SXP 18.3",
    "19": "SXP 22.07", "20": "SXP 25.5", "21": "SXP 31.0", "22": "SXP 46.6",
    "23": "SXP 59", "24": "SXP 65.8", "25": "SXP 74.7", "26": "SXP 82.4",
    "27": "SXP 91.1", "29": "SXP 101", "30": "SXP 138", "31": "SXP 140",
    "33": "SXP 152", "35": "SXP 169.3", "36": "SXP 172", "37": "SXP 175",
    "38": "SXP 202", "39": "SXP 202B", "40": "SXP 214", "41": "SXP 264",
    "42": "SXP 265", "43": "SXP 280.4", "44": "SXP 291", "45": "SXP 292",
    "46": "SXP 304", "47": "SXP 323", "48": "SXP 325", "49": "SXP 342",
    "50": "SXP 343", "51": "SXP 455", "52": "SXP 504", "53": "SXP 523",
    "54": "SXP 565", "55": "SXP 645", "56": "SXP 701", "57": "SXP 726",
    "58": "SXP 755.5", "59": "SXP 893", "60": "SXP 967", "61": "SXP 1062",
    "62": "SXP 1323",
}
# SMC X-3 (Seq 9) is already in the project as a ULX pulsar (extra_objects.py)
SMC_EXCLUDE_SEQ = {"9"}


def to_degrees(ra, dec):
    """VizieR returns sexagesimal strings for some tables and degrees for others."""
    ra, dec = ra.astype(str), dec.astype(str)
    if ra.str.contains(" ").any():
        c = SkyCoord(ra.values, dec.values, unit=(u.hourangle, u.deg), frame="icrs")
        return c.ra.deg, c.dec.deg
    return ra.astype(float).values, dec.astype(float).values


def smc_pulsars():
    df = read_vizier_tsv("J/A+A/586/A81/table5")
    # firm spin periods only ("ps:" marks the authors' uncertain detections)
    df = df[(df["ps"] == "ps") & ~df["Seq"].isin(SMC_EXCLUDE_SEQ)].copy()
    # position: confidently identified optical counterpart, else a usable X-ray position
    # (RXTE-only sources have ~1 deg errors and are dropped)
    opt = df["RAO"].notna() & (df["oi"] == "oi")
    df = df[opt | (df["e_Pos"].astype(float) <= 60)].copy()
    opt = opt[df.index]
    ra_o, de_o = to_degrees(df["RAO"].fillna(df["RAJ2000"]), df["DEO"].fillna(df["DEJ2000"]))
    ra_x, de_x = to_degrees(df["RAJ2000"], df["DEJ2000"])
    p = df["Pspin"].astype(float)
    fallback = p.map(lambda v: f"SXP {v:.2f}" if v < 10 else f"SXP {v:.1f}" if v < 100 else f"SXP {v:.0f}")
    return pd.DataFrame({
        "NS_NAME": df["Seq"].map(SXP_NAMES).fillna(fallback).values,
        "RAJ": np.where(opt, ra_o, ra_x),
        "DECJ": np.where(opt, de_o, de_x),
        "DIST": np.nan,
        "P": p.values,
        "galaxy": "smc",
        "source_catalog": "SMC HMXB (Haberl+2016)",
    })


def lmc_pulsars():
    df = read_vizier_tsv("J/A+A/707/A225/catalog")
    # neutron stars = X-ray pulsars; the Be/white dwarf candidates have no spin period anyway
    df = df[df["Pspin"].notna() & ~df["Type"].fillna("").str.contains("WD")].copy()
    gaia = df["RAGdeg"].notna()
    ra_x, de_x = to_degrees(df["RAJ2000"], df["DEJ2000"])
    return pd.DataFrame({
        "NS_NAME": df["XrayName"].values,
        "RAJ": np.where(gaia, df["RAGdeg"].astype(float), ra_x),
        "DECJ": np.where(gaia, df["DEGdeg"].astype(float), de_x),
        "DIST": np.nan,
        "P": df["Pspin"].astype(float).values,
        "galaxy": "lmc",
        "source_catalog": "LMC HMXB (eRASS1)",
    })


if __name__ == "__main__":
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.concat([smc_pulsars(), lmc_pulsars()], ignore_index=True)
    # no individual distances: place each pulsar on its galaxy's tilted plane
    for galaxy in ("smc", "lmc"):
        sel = df["galaxy"] == galaxy
        df.loc[sel, "DIST"] = disk_distance(df.loc[sel, "RAJ"], df.loc[sel, "DECJ"], galaxy)
    df["PDOT"] = np.nan
    df["type"] = "high-mass X-ray binary (NS)"
    df["wiki_url"] = df["NS_NAME"].str.replace(" ", "_").apply(lambda n: f"https://en.wikipedia.org/wiki/{n}")
    df.to_parquet(DATA_DIR / "mc_hmxb_raw.parquet", index=False)

    coords = SkyCoord(ra=df["RAJ"].values * u.deg, dec=df["DECJ"].values * u.deg,
                      distance=df["DIST"].values * u.kpc, frame="icrs")
    gal = coords.transform_to(GALCEN)
    df["x"] = gal.x.to(u.kpc).value
    df["y"] = gal.y.to(u.kpc).value
    df["z"] = gal.z.to(u.kpc).value
    df.to_parquet(DATA_DIR / "mc_hmxb_processed.parquet", index=False)
    print(f"Magellanic Cloud HMXB pulsars: {(df.galaxy == 'smc').sum()} SMC, {(df.galaxy == 'lmc').sum()} LMC")
