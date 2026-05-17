# Neutron Star Project

An interactive 3D catalog and analysis platform for neutron stars, built with Python and Three.js.

**https://viserac.github.io/neutron-star-project/index.html**

**API: https://neutron-star-api.mistyck.workers.dev**

---

## What it is

The Neutron Star Project aggregates data from multiple astronomical catalogs and renders known neutron stars in a navigable three-dimensional map of the Milky Way and its neighboring galaxies. Objects are color-coded by type and can be filtered, searched, and selected to view detailed information including coordinates, distance, period, period derivative, and links to Wikipedia and SIMBAD.

A REST API is available for programmatic access to the catalog data, suitable for use in Python scripts, Jupyter notebooks, and research pipelines.

**Catalogs included:**
- [ATNF Pulsar Catalogue](https://www.atnf.csiro.au/research/pulsar/psrcat/) — ~4,100 pulsars
- [McGill Magnetar Catalogue](https://www.physics.mcgill.ca/~pulsar/magnetar/main.html) — ~25 magnetars
- The Magnificent Seven — 7 isolated neutron stars (SIMBAD + Motch et al. 2007)
- Confirmed CCOs — 8 central compact objects (SIMBAD + De Luca)

---

## Repository structure

```
neutron-star-project/
├── pipeline/          # Data pipeline (fetch, transform, concat, export)
├── analysis/          # Python analysis scripts + Milky Way background image
├── worker/            # Cloudflare Worker API (worker.js + wrangler.toml)
├── scripts/           # Utility scripts (verify_outputs.py)
├── docs/              # Static site served by GitHub Pages
│   ├── index.html
│   ├── catalog.html
│   ├── import-export.html
│   ├── analysis.html
│   ├── api.html
│   ├── faq.html
│   ├── about.html
│   ├── data-sources.html
│   └── data/
│       ├── NS_db_full.json
│       └── NS_catalog_full.json
├── .github/workflows/
│   ├── update_catalog.yml   # Weekly pipeline run
│   └── deploy_worker.yml    # Auto-deploy API on worker changes
├── LICENSE
└── README.md
```

---

## REST API

Base URL: `https://neutron-star-api.mistyck.workers.dev`

```python
import requests

# Catalog statistics
requests.get("https://neutron-star-api.mistyck.workers.dev/stats").json()

# Search by name (regex supported)
requests.get("https://neutron-star-api.mistyck.workers.dev/search?name=J0534").json()

# Cone search (RA, Dec, radius in degrees)
requests.get("https://neutron-star-api.mistyck.workers.dev/cone?ra=83.8&dec=22.0&radius=1.0").json()

# Filtered catalog
requests.get("https://neutron-star-api.mistyck.workers.dev/catalog?type=magnetar").json()

# Single object
requests.get("https://neutron-star-api.mistyck.workers.dev/object?name=J0534+2200").json()
```

Full API documentation: https://viserac.github.io/neutron-star-project/api.html

---

## Dependencies

```
psrqpy astropy pandas scikit-learn pyarrow scipy matplotlib
```

The heatmap analysis requires `analysis/milkyway-full.webp`, a top-down infrared illustration of the Milky Way based on GLIMPSE survey data (Spitzer Space Telescope, NASA/JPL-Caltech). Calibrated with two reference points: Galactic center at pixel (2808, 2790) and the Sun at (2793, 3879), yielding ~0.00746 kpc/pixel.

---

## Automatic updates

The catalog data is updated automatically every Monday at 06:00 UTC via GitHub Actions. The pipeline fetches fresh data from ATNF and McGill, processes coordinates, and commits the updated JSON files to the repository.

---

## Citation

If you use this project in your work, please cite:

```
Victor Seraco. Neutron Star Project (2026). https://github.com/ViSerac/neutron-star-project
```

---

## License

Code: MIT License. Data: CC BY 4.0. See [LICENSE](LICENSE).

## Contact

seraco.nsproj@gmail.com
