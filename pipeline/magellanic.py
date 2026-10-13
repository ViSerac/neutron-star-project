"""Distances inside the Magellanic Clouds from a tilted-plane model of their young stars.

Objects with no individual distance are placed where their line of sight crosses the
plane traced by Classical Cepheids, instead of all at the mean galaxy distance.

LMC: mean distance 49.59 kpc (Pietrzynski+2019); inclination 25.05 deg and line of
     nodes at PA 150.76 deg (Inno+2016), so the near side points to PA 60.76 deg (NE).
SMC: mean distance 62.44 kpc (Graczyk+2020); inclination 74 deg with the near side
     towards PA 66 deg, NE (Haschke+2012). The young SMC population is really an
     elongated structure rather than a thin disk (Ripepi+2017), so this plane is an
     approximation that reproduces its NE-closer, tens-of-kpc line-of-sight extent.
"""
import numpy as np

GEOMETRY = {
    #        centre RA, Dec (deg)   D0 (kpc)  incl (deg)  PA of near side (deg, N through E)
    "lmc": dict(ra=80.894, dec=-69.756, d0=49.59, incl=25.05, near_pa=150.76 - 90),
    "smc": dict(ra=12.54,  dec=-73.11,  d0=62.44, incl=74.0,  near_pa=66.0),
}


def _unit(ra, dec):
    ra, dec = np.radians(ra), np.radians(dec)
    return np.stack([np.cos(dec) * np.cos(ra), np.cos(dec) * np.sin(ra), np.sin(dec)], axis=-1)


def disk_distance(ra_deg, dec_deg, galaxy):
    """Distance (kpc) at which each line of sight meets the galaxy's tilted plane."""
    g = GEOMETRY[galaxy]
    u0 = _unit(g["ra"], g["dec"])
    # sky basis at the centre: east and north tangent vectors
    ra0, dec0 = np.radians(g["ra"]), np.radians(g["dec"])
    east = np.array([-np.sin(ra0), np.cos(ra0), 0.0])
    north = np.array([-np.sin(dec0) * np.cos(ra0), -np.sin(dec0) * np.sin(ra0), np.cos(dec0)])
    pa = np.radians(g["near_pa"])
    near = np.cos(pa) * north + np.sin(pa) * east          # sky direction of the near side
    nodes = np.cross(u0, near)                              # line of nodes, in the plane and the sky
    incl = np.radians(g["incl"])
    downhill = np.cos(incl) * near - np.sin(incl) * u0      # in-plane direction moving towards us
    normal = np.cross(nodes, downhill)
    u = _unit(np.asarray(ra_deg, float), np.asarray(dec_deg, float))
    return g["d0"] * (normal @ u0) / (u @ normal)
