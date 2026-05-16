import pandas as pd
import numpy as np
from astropy.coordinates import SkyCoord, Galactocentric
from astropy import units as u
from sklearn.cluster import DBSCAN
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

def convert_to_cartesian_galactic(
    input_path = DATA_DIR / "atnf_raw.parquet",
    output_path = DATA_DIR / "atnf_processed_galactic.parquet"
):
    df_galactic = pd.read_parquet(input_path)

    df_galactic = df_galactic.dropna(subset=["DIST", "RAJ", "DECJ"])

    coords = SkyCoord(
        ra=df_galactic["RAJ"].values,
        dec=df_galactic["DECJ"].values,
        distance=df_galactic["DIST"].values * u.kpc,
        unit=(u.hourangle, u.deg),
        frame="icrs"
    )

    gal = coords.transform_to(Galactocentric())

    df_galactic["x"] = gal.x.to(u.kpc).value
    df_galactic["y"] = gal.y.to(u.kpc).value
    df_galactic["z"] = gal.z.to(u.kpc).value
    df_galactic = df_galactic[df_galactic["z"].between(-5, 5)]
    df_galactic = df_galactic[df_galactic["DIST"] < 20]
    
    df_galactic["P"] = df_galactic["P"].fillna(np.nan)
    df_galactic["PDOT"] = df_galactic["PDOT"].fillna(np.nan)
    
    df_galactic["galaxy"] = "milky_way"
    df_galactic["type"] = "pulsar"
    df_galactic["source_catalog"] = "ATNF"

    df_galactic["wiki_url"] = df_galactic["NS_NAME"].apply(lambda name: f"https://en.wikipedia.org/wiki/{name}")
    print(f"Saving galactic to: {output_path} ({len(df_galactic)} records)")
    df_galactic.to_parquet(output_path, index=False)
    # print(df_galactic["z"].describe())
    # print(df_galactic[["x", "y", "z"]].head())
    # print(df_galactic["DIST"].describe())
    print(f"Saved processed data to {output_path}")

def convert_to_cartesian_extragalactic(
    input_path = DATA_DIR / "atnf_raw.parquet",
    output_path = DATA_DIR / "atnf_processed_extragalactic.parquet"
):
    df_extragalactic = pd.read_parquet(input_path)

    df_extragalactic = df_extragalactic.dropna(subset=["DIST", "RAJ", "DECJ"])

    coords = SkyCoord(
        ra=df_extragalactic["RAJ"].values,
        dec=df_extragalactic["DECJ"].values,
        distance=df_extragalactic["DIST"].values * u.kpc,
        unit=(u.hourangle, u.deg),
        frame="icrs"
    )

    gal = coords.transform_to(Galactocentric())

    df_extragalactic["x"] = gal.x.to(u.kpc).value
    df_extragalactic["y"] = gal.y.to(u.kpc).value
    df_extragalactic["z"] = gal.z.to(u.kpc).value
    df_extragalactic = df_extragalactic[df_extragalactic["DIST"].between(40, 70)]
    
    coords_array = df_extragalactic[["x", "y", "z"]].values

    clustering = DBSCAN(eps=5, min_samples=5).fit(coords_array)
    labels = clustering.labels_
    df_extragalactic["cluster"] = labels
    
    counts = df_extragalactic.groupby("cluster")["NS_NAME"].count()
    cluster_lmc = counts.idxmax()
    cluster_smc = counts.idxmin()
    
    df_extragalactic["P"] = df_extragalactic["P"].fillna(np.nan)
    df_extragalactic["PDOT"] = df_extragalactic["PDOT"].fillna(np.nan)
    
    df_extragalactic["galaxy"] = "unknown" 
    df_extragalactic.loc[df_extragalactic["cluster"] == cluster_lmc, "galaxy"] = "lmc"
    df_extragalactic.loc[df_extragalactic["cluster"] == cluster_smc, "galaxy"] = "smc"

    df_extragalactic["type"] = "pulsar"
    df_extragalactic["source_catalog"] = "ATNF"

    df_extragalactic["wiki_url"] = df_extragalactic["NS_NAME"].apply(lambda name: f"https://en.wikipedia.org/wiki/{name}")
    print(f"Saving extragalactic to: {output_path} ({len(df_extragalactic)} records)")
    df_extragalactic.to_parquet(output_path, index=False)
    
    # print(set(labels))
    # print(df_extragalactic["galaxy"].value_counts())
    # print(df_extragalactic["cluster"].value_counts())
    # print(df_extragalactic.groupby("galaxy")[["x","y","z"]].mean())
    # print(df_extragalactic["z"].describe())
    # print(df_extragalactic[["x", "y", "z"]].head())
    # print(df_extragalactic["DIST"].describe())
    print(f"Saved processed data to {output_path}")
    
if __name__ == "__main__":
    convert_to_cartesian_galactic()
    convert_to_cartesian_extragalactic()