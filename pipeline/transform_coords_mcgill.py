import pandas as pd
import numpy as np
from astropy.coordinates import SkyCoord, Galactocentric
from astropy import units as u

def convert_to_cartesian_galactic():
    input_path = "../data/mcgill_raw.parquet"
    output_path = "../data/mcgill_processed_galactic.parquet"
    
    df_galactic = pd.read_parquet(input_path)
    df_galactic = df_galactic.dropna(subset=["RAJ", "DECJ", "DIST"])
    
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
    
    df_galactic["type"] = np.select(
        condlist=[df_galactic["NS_NAME"].str.endswith(' ##'), df_galactic["NS_NAME"].str.endswith(' #')],
        choicelist=["pulsar_outburst_2006", "candidate_magnetar"],
        default="magnetar"
    )
        
    df_galactic["source_catalog"] = "McGill"
    df_galactic["wiki_url"] = df_galactic["NS_NAME"].str.replace(" ", "_").apply(lambda name: f"https://en.wikipedia.org/wiki/{name}")
    
    df_galactic.to_parquet(output_path, index=False)
    
    print(f"Saved processed data to {output_path}")

def convert_to_cartesian_extragalactic():
    input_path = "../data/mcgill_raw.parquet"
    output_path = "../data/mcgill_processed_extragalactic.parquet"
    
    df_extragalactic = pd.read_parquet(input_path)
    df_extragalactic = df_extragalactic.dropna(subset=["RAJ", "DECJ", "DIST"])
    
    df_extragalactic = df_extragalactic[df_extragalactic["DIST"].between(40, 70)]
        
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

    df_extragalactic["P"] = df_extragalactic["P"].fillna(np.nan)
    df_extragalactic["PDOT"] = df_extragalactic["PDOT"].fillna(np.nan)
    
    coords_lmc = SkyCoord(
        ra="05h23m35s",
        dec="-69d45m22s",
        distance=50 * u.kpc,
        unit=(u.hourangle, u.deg),
        frame="icrs"
    )
    
    coords_smc = SkyCoord(
        ra="00h52m38s",
        dec="-72d49m43s",
        distance=60 * u.kpc,
        unit=(u.hourangle, u.deg),
        frame="icrs"
    )
    
    closest_lmc = coords_lmc.separation_3d(coords)
    closest_smc = coords_smc.separation_3d(coords)
   
    df_extragalactic["galaxy"] = np.where(
        closest_lmc<closest_smc, "lmc", "smc"
    )
    
    df_extragalactic["type"] = np.select(
        condlist=[df_extragalactic["NS_NAME"].str.endswith(' ##'), df_extragalactic["NS_NAME"].str.endswith(' #')],
        choicelist=["pulsar_outburst_2006", "candidate_magnetar"],
        default="magnetar"
    )
    
    df_extragalactic["source_catalog"] = "McGill"
    df_extragalactic["wiki_url"] = df_extragalactic["NS_NAME"].str.replace(" ", "_").apply(lambda name: f"https://en.wikipedia.org/wiki/{name}")
    
    df_extragalactic.to_parquet(output_path, index=False)
    
    print(f"Saved processed data to {output_path}")

if __name__ == "__main__":
    convert_to_cartesian_galactic()
    convert_to_cartesian_extragalactic()
