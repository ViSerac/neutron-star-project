# Neutron Star Project

An interactive 3D catalog visualizer for neutron stars, built with Python and Three.js.

Live at: **https://viserac.github.io/neutron-star-project/site/**

---

## What it is

The Neutron Star Project aggregates data from multiple astronomical catalogs and renders known neutron stars in a navigable three-dimensional map of the Milky Way and its neighboring galaxies. Objects are color-coded by type and can be filtered, searched, and selected to view detailed information including coordinates, distance, period, period derivative, and links to Wikipedia and SIMBAD.

**Catalogs included:**
- [ATNF Pulsar Catalogue](https://www.atnf.csiro.au/research/pulsar/psrcat/) — ~4,056 pulsars
- [McGill Magnetar Catalogue](https://www.physics.mcgill.ca/~pulsar/magnetar/main.html) — ~25 magnetars
- The Magnificent Seven — 7 isolated neutron stars (SIMBAD + Motch et al. 2007)
- Confirmed CCOs — 8 central compact objects (SIMBAD + De Luca)

---

## Repository structure

```
neutron-star-project/
├── pipeline/
│   ├── fetch_atnf.py
│   ├── fetch_mcgill.py
│   ├── transform_coords_atnf.py
│   ├── transform_coords_mcgill.py
│   ├── m7andcco.py
│   ├── concat_catalogs.py
│   └── export_json.py
├── analysis/
│   ├── analysis_ppdot.py
│   └── analysis_heatmap.py
├── site/
│   ├── index.html
│   ├── import-export.html
│   ├── faq.html
│   ├── about.html
│   ├── data-sources.html
│   └── data/
│       └── NS_db_full.json
├── LICENSE
└── README.md
```

---

## Running the pipeline

```bash
pip install psrqpy astropy pandas scikit-learn pyarrow scipy matplotlib

python pipeline/fetch_atnf.py
python pipeline/fetch_mcgill.py
python pipeline/transform_coords_atnf.py
python pipeline/transform_coords_mcgill.py
python pipeline/m7andcco.py
python pipeline/concat_catalogs.py
python pipeline/export_json.py
```

---

## Running the analyses

```bash
python analysis/analysis_ppdot.py
python analysis/analysis_heatmap.py
```

The heatmap requires a Milky Way background image (`milkyway-full.webp`) in the project root, calibrated using the GLIMPSE survey image from NASA/JPL.

---

## Running the site locally

```bash
cd site
python -m http.server 8000
```

---

## Controls

| Action | Control |
|---|---|
| Rotate | Left click + drag |
| Zoom | Scroll wheel |
| Pan | Right click + drag or Middle click + drag |
| Select object | Left click on a point |

---

## Citation

If you use this project in your work, please cite:

```
Seraco. Neutron Star Project (2025). https://github.com/ViSerac/neutron-star-project
```

---

## License

Code: MIT License. Data: CC BY 4.0. See [LICENSE](LICENSE).

## Contact

seraco.nsproj@gmail.com
