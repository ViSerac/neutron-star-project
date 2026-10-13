import io
import re
import urllib.request
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

VIZIER = "https://vizier.cds.unistra.fr/viz-bin/asu-tsv?-source={}&-out.all&-out.max=unlimited"

# XRBcats (Tuebingen). Only systems with direct evidence of a neutron star are kept:
# X-ray pulsations, type I bursts / burst oscillations, cyclotron lines, Z/atoll
# behaviour, a quiescent NS spectrum or a radio pulsar, or a measured spin period.
# Tags ending in "?" don't count.
CATALOGS = {
    "hmxb": {
        "source": "J/A+A/677/A134/hmxbcat",
        "source_catalog": "XRBcats HMXB",
        "type": "high-mass X-ray binary (NS)",
        "dist_col": "Dist",
        "ns_tags": {"XP", "XB", "CL"},
        # already in the project as ATNF pulsars / McGill candidate
        "exclude": {"PSR J0635+0533", "PSR B1259-63", "SGR 0755-2933"},
    },
    "lmxb": {
        "source": "J/A+A/675/A199/lmxbcat",
        "source_catalog": "XRBcats LMXB",
        "type": "low-mass X-ray binary (NS)",
        "dist_col": "MeanDist",
        "ns_tags": {"XB", "BO", "XP", "ZS", "AS", "QNS", "RP"},
        # transitional / binary MSPs already listed by ATNF under their PSR names
        "exclude": {"PSR J1023+0038", "XSS J12270-4859", "1FGL J1417.7-4407",
                    "PSR J1723-2837", "IGR J18245-2452"},
    },
}


def read_vizier_tsv(source):
    with urllib.request.urlopen(VIZIER.format(source), timeout=120) as res:
        text = res.read().decode("utf-8")
    lines = [l for l in text.splitlines() if l.strip() and not l.startswith("#")]
    # line 0 = column names, 1 = units, 2 = dashes
    df = pd.read_csv(io.StringIO("\n".join([lines[0]] + lines[3:])), sep="\t", dtype=str)
    df = df.apply(lambda c: c.str.strip())
    return df.replace({"": np.nan, "-": np.nan})


def select_neutron_stars(df, cfg, key):
    tags = df["XrayType"].fillna("").map(lambda s: set(re.split(r"[,;\s]+", s)))
    is_ns = tags.map(lambda t: bool(t & cfg["ns_tags"])) | df["Ppulse"].notna()
    if key == "lmxb":
        is_ns |= df["tMSPFlag"].eq("1")
    is_ns &= ~tags.map(lambda t: "BH" in t)
    # gamma Cas analogues: their long periodicities don't establish a NS (could be a WD)
    is_ns &= ~tags.map(lambda t: "Gcas" in t and "XP" not in t)
    df = df[is_ns & ~df["Name"].isin(cfg["exclude"])].copy()

    out = pd.DataFrame({
        "NS_NAME": df["Name"].values,
        "RAJ": df["RA_ICRS"].astype(float).values,
        "DECJ": df["DE_ICRS"].astype(float).values,
        "DIST": df[cfg["dist_col"]].astype(float).values / 1000,
        "P": df["Ppulse"].astype(float).values,
        "PDOT": np.nan,
        "xray_type": df["XrayType"].values,
    })
    out["type"] = cfg["type"]
    out["source_catalog"] = cfg["source_catalog"]
    out["wiki_url"] = out["NS_NAME"].str.replace(" ", "_").apply(lambda n: f"https://en.wikipedia.org/wiki/{n}")
    return out


def place_in_galaxy(df):
    df = df.dropna(subset=["RAJ", "DECJ", "DIST"]).copy()
    coords = SkyCoord(ra=df["RAJ"].values * u.deg, dec=df["DECJ"].values * u.deg,
                      distance=df["DIST"].values * u.kpc, frame="icrs")
    gal = coords.transform_to(GALCEN)
    df["x"] = gal.x.to(u.kpc).value
    df["y"] = gal.y.to(u.kpc).value
    df["z"] = gal.z.to(u.kpc).value
    df = df[df["z"].between(-5, 5) & (df["DIST"] < 20)]
    df["galaxy"] = "milky_way"
    return df


if __name__ == "__main__":
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    raw = pd.concat([select_neutron_stars(read_vizier_tsv(cfg["source"]), cfg, key)
                     for key, cfg in CATALOGS.items()], ignore_index=True)
    raw.to_parquet(DATA_DIR / "xrb_raw.parquet", index=False)
    placed = place_in_galaxy(raw)
    placed.reset_index(drop=True).to_parquet(DATA_DIR / "xrb_processed.parquet", index=False)
    print(f"XRB neutron stars: {len(raw)} total, {len(placed)} placed in 3D")
