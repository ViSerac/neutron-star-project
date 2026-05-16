import pandas as pd
import numpy as np
from astropy.coordinates import SkyCoord, Galactocentric
from astropy import units as u
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

def convert_to_cartesian_m7():
    output_path = DATA_DIR / "m7_processed.parquet"
    
    m7data = {
        "NS_NAME": ["RX J0720.4-3125", "1RXS J214303.7+065419", "1RXS J130848.6+212708", "RX J1856.5-3754", "RX J1605.3+3249", "RX J0806.4-4123", "RX J0420.0-5022"],
        "RAJ": ["07 20 24.961", "21 43 03.8", "13 08 48.7", "18 56 35.11", "16 05 18.9", "08 06 23.0", "04 20 02.2"],
        "DECJ": ["-31 25 50.21", "+06 54 20", "+21 27 08", "-37 54 30.5", "+32 49 07", "-41 22 33", "-50 22 46"],
        "parallax_mas": [485, 400, 297, 91.5, 410, 120, 170],  # Paralax (mas) media: https://arxiv.org/pdf/0712.0342
    }
    
    df = pd.DataFrame(m7data)
    df["DIST"] = 1000 / df["parallax_mas"]
    # df["DIST"] = df["DIST"] / 1000
    
    coords = SkyCoord(
        ra=df["RAJ"].values,
        dec=df["DECJ"].values,
        distance=df["DIST"].values * u.kpc,
        unit=(u.hourangle, u.deg),
        frame="icrs"
    )
    
    gal = coords.transform_to(Galactocentric())
    
    df["x"] = gal.x.to(u.kpc).value
    df["y"] = gal.y.to(u.kpc).value
    df["z"] = gal.z.to(u.kpc).value
    
    df["galaxy"] = "milky_way"
    df["type"] = "M7 isolated neutron star"
    df["source_catalog"] = "SIMBAD Magnificent Seven"
    
    df["wiki_url"] = np.select(condlist=[df["NS_NAME"] == "RX J1856.5-3754", df["NS_NAME"] == "RX J0720.4-3125"],
                               choicelist=[f"https://en.wikipedia.org/wiki/RX_J1856-3754", f"https://en.wikipedia.org/wiki/RX_J0720.4-3125"],
                               default=f"https://en.wikipedia.org/wiki/The_Magnificent_Seven_(neutron_stars)")
    
    df.to_parquet(output_path, index=False)
    print(f"Saved processed data to {output_path}")
    
def convert_to_carterian_cco():
    output_path = DATA_DIR / "cco_processed.parquet"
    
    cco_data = {
        "NS_NAME": ["RX J0822.0-4300", "CXOU J085201.4-461753", "1E 1207.4-5209", "CXOU J160103.1-513353", "1WGA J1713.4-3949", "XMMU J172054.5-372652", "CXOU J185238.6+004020", "CXOU J232327.9+584842"],
        "RAJ": ["08 21 57.3653", "08 52 01.38", "12 10 00.91", "16 01 03.14", "17 13 28.3", "17 20 54.5", "18 52 38.57", "23 23 27.94"],
        "DECJ": ["-43 00 17.074", "-46 17 53.34", "-52 26 28.35", "-51 33 53.6", "-39 49 53", "-37 26 52", "+00 40 19.8", "+58 48 42.5"],
        "DIST": [2.2, 1.0, 2.2, 5.0, 1.3, 4.5, 7.0, 3.4]
    }
    
    df = pd.DataFrame(cco_data)
    
    coords = SkyCoord(
        ra=df["RAJ"].values,
        dec=df["DECJ"].values,
        distance=df["DIST"].values * u.kpc,
        unit=(u.hourangle, u.deg),
        frame="icrs"
    )
    
    gal = coords.transform_to(Galactocentric())
    
    df["x"] = gal.x.to(u.kpc).value
    df["y"] = gal.y.to(u.kpc).value
    df["z"] = gal.z.to(u.kpc).value
    
    df["galaxy"] = "milky_way"
    df["type"] = "central compact object (CCO)"
    df["source_catalog"] = "SIMBAD CCOs"
    
    df["wiki_url"] = df["NS_NAME"].str.replace(" ", "_").apply(lambda name: f"https://en.wikipedia.org/wiki/{name}")
    
    df.to_parquet(output_path, index=False)
    print(f"Saved processed data to {output_path}")

if __name__ == "__main__":
    convert_to_cartesian_m7()
    convert_to_carterian_cco()