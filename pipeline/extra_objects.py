import numpy as np
import pandas as pd
from astropy.coordinates import SkyCoord, Galactocentric
from astropy import units as u
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"

GALCEN = Galactocentric(
    galcen_distance=8.122 * u.kpc,
    z_sun=20.8 * u.pc,
)

# Neutron stars that no regularly updated catalogue covers. Positions from SIMBAD;
# distances are those of the host galaxy; P is the spin period at discovery
# (ULX pulsars spin up quickly, so it changes between epochs).
OBJECTS = [
    # name,                       RA (deg),    Dec (deg),   DIST (kpc), P (s), galaxy,     type
    ("M82 X-2",                   148.962667,  69.679303,   3600,  1.37,  "M82",      "ULX pulsar"),
    ("NGC 7793 P13",              359.46208,  -32.62406,    3900,  0.42,  "NGC 7793", "ULX pulsar"),
    ("NGC 5907 ULX1",             228.99417,   56.30278,   17100,  1.13,  "NGC 5907", "ULX pulsar"),
    ("NGC 300 ULX1",               13.77025,  -37.69547,    2000, 31.6,   "NGC 300",  "ULX pulsar"),
    ("NGC 1313 X-2",               49.59167,  -66.60119,    4200,  1.5,   "NGC 1313", "ULX pulsar"),
    ("M51 ULX-7",                 202.50421,   47.22886,    8600,  2.8,   "M51",      "ULX pulsar"),
    ("SMC X-3",                    13.02344,  -72.43451,   62.44,  7.8,   "smc",      "ULX pulsar"),
    ("RX J0209.6-7427",            32.39390,  -74.45328,   62.44,  9.3,   "smc",      "ULX pulsar"),
    # JWST emission lines ionised by a compact source (Fransson+2024, Science 383, 898)
    ("SN 1987A compact object",    83.86662,  -69.26975,    51.4, np.nan, "lmc",      "SN 1987A compact object (candidate)"),
]

WIKI = {
    "SN 1987A compact object": "https://en.wikipedia.org/wiki/SN_1987A",
}


def build():
    df = pd.DataFrame(OBJECTS, columns=["NS_NAME", "RAJ", "DECJ", "DIST", "P", "galaxy", "type"])
    df["PDOT"] = np.nan
    df["source_catalog"] = "Literature"
    df["wiki_url"] = df["NS_NAME"].map(WIKI).fillna(
        df["NS_NAME"].str.replace(" ", "_").apply(lambda n: f"https://en.wikipedia.org/wiki/{n}"))
    return df


if __name__ == "__main__":
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    raw = build()
    raw.to_parquet(DATA_DIR / "extra_raw.parquet", index=False)

    # Only the Magellanic Cloud objects fit in the 3D scene; the rest are Mpc away
    placed = raw[raw["galaxy"].isin(["lmc", "smc"])].copy()
    coords = SkyCoord(ra=placed["RAJ"].values * u.deg, dec=placed["DECJ"].values * u.deg,
                      distance=placed["DIST"].values * u.kpc, frame="icrs")
    gal = coords.transform_to(GALCEN)
    placed["x"] = gal.x.to(u.kpc).value
    placed["y"] = gal.y.to(u.kpc).value
    placed["z"] = gal.z.to(u.kpc).value
    placed.reset_index(drop=True).to_parquet(DATA_DIR / "extra_processed.parquet", index=False)
    print(f"Extra objects: {len(raw)} total, {len(placed)} placed in 3D")
