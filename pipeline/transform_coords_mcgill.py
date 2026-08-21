import pandas as pd
import numpy as np
from astropy.coordinates import SkyCoord, Galactocentric
from astropy import units as u
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"

GALCEN = Galactocentric(
    galcen_distance=8.122 * u.kpc,
    z_sun=20.8 * u.pc,
)

def convert_to_cartesian_galactic():
    input_path  = DATA_DIR / "mcgill_raw.parquet"
    output_path = DATA_DIR / "mcgill_processed_galactic.parquet"

    df = pd.read_parquet(input_path)
    df = df.dropna(subset=["RAJ", "DECJ", "DIST"])

    # McGill coordinates are strings in HH MM SS format
    raj_str  = df["RAJ"].astype(str).str.replace(":", " ", regex=False)
    decj_str = df["DECJ"].astype(str).str.replace(":", " ", regex=False)
    coords = SkyCoord(ra=raj_str.values, dec=decj_str.values,
                      distance=df["DIST"].values * u.kpc,
                      unit=(u.hourangle, u.deg), frame="icrs")

    df["RAJ"]  = coords.ra.deg
    df["DECJ"] = coords.dec.deg

    gal = coords.transform_to(GALCEN)
    df["x"] = gal.x.to(u.kpc).value
    df["y"] = gal.y.to(u.kpc).value
    df["z"] = gal.z.to(u.kpc).value
    df = df[df["z"].between(-5, 5)]
    df = df[df["DIST"] < 20]
    df["P"]    = df["P"].fillna(np.nan)
    df["PDOT"] = df["PDOT"].fillna(np.nan)
    df["galaxy"] = "milky_way"
    df["type"] = np.select(
        [df["NS_NAME"].str.endswith(" ##"), df["NS_NAME"].str.endswith(" #")],
        ["pulsar_outburst_2006", "candidate_magnetar"], default="magnetar")
    df["source_catalog"] = "McGill"
    df["wiki_url"] = df["NS_NAME"].str.replace(" ","_").apply(lambda n: f"https://en.wikipedia.org/wiki/{n}")
    df.reset_index(drop=True).to_parquet(output_path, index=False)
    print(f"Saved processed data to {output_path}")

def convert_to_cartesian_extragalactic():
    input_path  = DATA_DIR / "mcgill_raw.parquet"
    output_path = DATA_DIR / "mcgill_processed_extragalactic.parquet"

    df = pd.read_parquet(input_path)
    df = df.dropna(subset=["RAJ", "DECJ", "DIST"])
    df = df[df["DIST"].between(40, 70)]

    raj_str  = df["RAJ"].astype(str).str.replace(":", " ", regex=False)
    decj_str = df["DECJ"].astype(str).str.replace(":", " ", regex=False)
    coords = SkyCoord(ra=raj_str.values, dec=decj_str.values,
                      distance=df["DIST"].values * u.kpc,
                      unit=(u.hourangle, u.deg), frame="icrs")

    df["RAJ"]  = coords.ra.deg
    df["DECJ"] = coords.dec.deg

    gal = coords.transform_to(GALCEN)
    df["x"] = gal.x.to(u.kpc).value
    df["y"] = gal.y.to(u.kpc).value
    df["z"] = gal.z.to(u.kpc).value
    df["P"]    = df["P"].fillna(np.nan)
    df["PDOT"] = df["PDOT"].fillna(np.nan)

    lmc = SkyCoord(ra="05h23m35s", dec="-69d45m22s", distance=50*u.kpc,
                   unit=(u.hourangle, u.deg), frame="icrs")
    smc = SkyCoord(ra="00h52m38s", dec="-72d49m43s", distance=60*u.kpc,
                   unit=(u.hourangle, u.deg), frame="icrs")
    df["galaxy"] = np.where(lmc.separation_3d(coords) < smc.separation_3d(coords), "lmc", "smc")
    df["type"] = np.select(
        [df["NS_NAME"].str.endswith(" ##"), df["NS_NAME"].str.endswith(" #")],
        ["pulsar_outburst_2006", "candidate_magnetar"], default="magnetar")
    df["source_catalog"] = "McGill"
    df["wiki_url"] = df["NS_NAME"].str.replace(" ","_").apply(lambda n: f"https://en.wikipedia.org/wiki/{n}")
    df.reset_index(drop=True).to_parquet(output_path, index=False)
    print(f"Saved processed data to {output_path}")

if __name__ == "__main__":
    convert_to_cartesian_galactic()
    convert_to_cartesian_extragalactic()
