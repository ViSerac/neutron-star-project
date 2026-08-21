import pandas as pd
import numpy as np
from astropy.coordinates import SkyCoord, Galactocentric
from astropy import units as u
from sklearn.cluster import DBSCAN
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"

GALCEN = Galactocentric(
    galcen_distance=8.122 * u.kpc,
    z_sun=20.8 * u.pc,
)

def convert_to_cartesian_galactic():
    input_path  = DATA_DIR / "atnf_raw.parquet"
    output_path = DATA_DIR / "atnf_processed_galactic.parquet"

    df = pd.read_parquet(input_path)
    df = df.dropna(subset=["DIST", "RAJ", "DECJ"])

    coords = SkyCoord(ra=df["RAJ"].values, dec=df["DECJ"].values,
                      distance=df["DIST"].values * u.kpc,
                      unit=(u.deg, u.deg), frame="icrs")
    gal = coords.transform_to(GALCEN)

    df["x"] = gal.x.to(u.kpc).value
    df["y"] = gal.y.to(u.kpc).value
    df["z"] = gal.z.to(u.kpc).value
    df = df[df["z"].between(-5, 5)]
    df = df[df["DIST"] < 20]
    df["P"]    = df["P"].fillna(np.nan)
    df["PDOT"] = df["PDOT"].fillna(np.nan)
    df["galaxy"]         = "milky_way"
    df["type"]           = "pulsar"
    df["source_catalog"] = "ATNF"
    df["wiki_url"]       = df["NS_NAME"].apply(lambda n: f"https://en.wikipedia.org/wiki/{n}")
    df.reset_index(drop=True).to_parquet(output_path, index=False)
    print(f"Saved {len(df)} galactic records to {output_path}")

def convert_to_cartesian_extragalactic():
    input_path  = DATA_DIR / "atnf_raw.parquet"
    output_path = DATA_DIR / "atnf_processed_extragalactic.parquet"

    df = pd.read_parquet(input_path)
    df = df.dropna(subset=["DIST", "RAJ", "DECJ"])

    coords = SkyCoord(ra=df["RAJ"].values, dec=df["DECJ"].values,
                      distance=df["DIST"].values * u.kpc,
                      unit=(u.deg, u.deg), frame="icrs")
    gal = coords.transform_to(GALCEN)

    df["x"] = gal.x.to(u.kpc).value
    df["y"] = gal.y.to(u.kpc).value
    df["z"] = gal.z.to(u.kpc).value
    df = df[df["DIST"].between(40, 70)]

    clustering = DBSCAN(eps=5, min_samples=5).fit(df[["x","y","z"]].values)
    df["cluster"] = clustering.labels_
    counts = df.groupby("cluster")["NS_NAME"].count()
    df["galaxy"] = "unknown"
    df.loc[df["cluster"] == counts.idxmax(), "galaxy"] = "lmc"
    df.loc[df["cluster"] == counts.idxmin(), "galaxy"] = "smc"

    df["P"]    = df["P"].fillna(np.nan)
    df["PDOT"] = df["PDOT"].fillna(np.nan)
    df["type"]           = "pulsar"
    df["source_catalog"] = "ATNF"
    df["wiki_url"]       = df["NS_NAME"].apply(lambda n: f"https://en.wikipedia.org/wiki/{n}")
    df.reset_index(drop=True).to_parquet(output_path, index=False)
    print(f"Saved {len(df)} extragalactic records to {output_path}")

if __name__ == "__main__":
    convert_to_cartesian_galactic()
    convert_to_cartesian_extragalactic()
