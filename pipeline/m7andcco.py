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

def add_atnf_timing(df):
    timing = pd.read_parquet(DATA_DIR / "atnf_overlap_timing.parquet")
    timing = timing.rename(columns={"NS_NAME": "ATNF_NAME"})
    return df.merge(timing, on="ATNF_NAME", how="left").drop(columns=["ATNF_NAME"])

def convert_to_cartesian_m7():
    output_path = DATA_DIR / "m7_processed.parquet"
    m7data = {
        "NS_NAME": ["RX J0720.4-3125","1RXS J214303.7+065419","1RXS J130848.6+212708","RX J1856.5-3754","RX J1605.3+3249","RX J0806.4-4123","RX J0420.0-5022"],
        "RAJ":  ["07 20 24.961","21 43 03.8","13 08 48.7","18 56 35.11","16 05 18.9","08 06 23.0","04 20 02.2"],
        "DECJ": ["-31 25 50.21","+06 54 20","+21 27 08","-37 54 30.5","+32 49 07","-41 22 33","-50 22 46"],
        # Motch et al. 2007 (arXiv:0712.0342), Table 1. RBS 1223 (J1308) is the midpoint
        # of 76-670 pc; J1605 and J0420 are upper limits (<410, <=340 pc).
        "dist_pc": [360,400,373,178,410,240,340],
        # J1605+3249 left unmatched: ATNF's 6.88 s is a 2.5-sigma candidate (Pires+2014)
        # not confirmed by Pires+2019 or Malacaria+2019 (ApJ 880, 74).
        "ATNF_NAME": ["J0720-3125","J2143+0654","J1308+2127","J1856-3754",None,"J0806-4123","J0420-5022"],
    }
    df = add_atnf_timing(pd.DataFrame(m7data))
    df["DIST"] = df["dist_pc"] / 1000

    coords = SkyCoord(ra=df["RAJ"].values, dec=df["DECJ"].values,
                      distance=df["DIST"].values * u.kpc,
                      unit=(u.hourangle, u.deg), frame="icrs")

    # Store as decimal degrees for consistency
    df["RAJ"]  = coords.ra.deg
    df["DECJ"] = coords.dec.deg

    gal = coords.transform_to(GALCEN)
    df["x"] = gal.x.to(u.kpc).value
    df["y"] = gal.y.to(u.kpc).value
    df["z"] = gal.z.to(u.kpc).value
    df["galaxy"]         = "milky_way"
    df["type"]           = "M7 isolated neutron star"
    df["source_catalog"] = "SIMBAD Magnificent Seven"
    df["wiki_url"] = np.select(
        [df["NS_NAME"]=="RX J1856.5-3754", df["NS_NAME"]=="RX J0720.4-3125"],
        ["https://en.wikipedia.org/wiki/RX_J1856-3754","https://en.wikipedia.org/wiki/RX_J0720.4-3125"],
        default="https://en.wikipedia.org/wiki/The_Magnificent_Seven_(neutron_stars)")
    df.to_parquet(output_path, index=False)
    print(f"Saved processed data to {output_path}")

def convert_to_cartesian_cco():
    output_path = DATA_DIR / "cco_processed.parquet"
    cco_data = {
        "NS_NAME": ["RX J0822.0-4300","CXOU J085201.4-461753","1E 1207.4-5209","CXOU J160103.1-513353","1WGA J1713.4-3949","XMMU J172054.5-372652","CXOU J185238.6+004020","CXOU J232327.9+584842"],
        "RAJ":  ["08 21 57.3653","08 52 01.38","12 10 00.91","16 01 03.14","17 13 28.3","17 20 54.5","18 52 38.57","23 23 27.94"],
        "DECJ": ["-43 00 17.074","-46 17 53.34","-52 26 28.35","-51 33 53.6","-39 49 53","-37 26 52","+00 40 19.8","+58 48 42.5"],
        "DIST": [2.2,1.0,2.2,5.0,1.3,4.5,7.0,3.4],
        "ATNF_NAME": ["J0821-4300",None,"J1210-5226",None,None,None,"J1852+0040",None],
    }
    df = add_atnf_timing(pd.DataFrame(cco_data))
    coords = SkyCoord(ra=df["RAJ"].values, dec=df["DECJ"].values,
                      distance=df["DIST"].values * u.kpc,
                      unit=(u.hourangle, u.deg), frame="icrs")

    df["RAJ"]  = coords.ra.deg
    df["DECJ"] = coords.dec.deg

    gal = coords.transform_to(GALCEN)
    df["x"] = gal.x.to(u.kpc).value
    df["y"] = gal.y.to(u.kpc).value
    df["z"] = gal.z.to(u.kpc).value
    df["galaxy"]         = "milky_way"
    df["type"]           = "central compact object (CCO)"
    df["source_catalog"] = "SIMBAD CCOs"
    df["wiki_url"] = df["NS_NAME"].str.replace(" ","_").apply(lambda n: f"https://en.wikipedia.org/wiki/{n}")
    df.to_parquet(output_path, index=False)
    print(f"Saved processed data to {output_path}")

if __name__ == "__main__":
    convert_to_cartesian_m7()
    convert_to_cartesian_cco()
