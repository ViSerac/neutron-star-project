# Neutron Star Project

An interactive 3D catalog visualizer for neutron stars, built with Python and Three.js.

**https://viserac.github.io/neutron-star-project/index.html**

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
├── pipeline/          # Data pipeline (fetch, transform, concat, export)
├── analysis/          # Python analysis scripts + Milky Way background image
├── docs/              # Static site served by GitHub Pages
│   ├── index.html
│   ├── import-export.html
│   ├── analysis.html
│   ├── faq.html
│   ├── about.html
│   ├── data-sources.html
│   └── data/
│       └── NS_db_full.json
├── LICENSE
└── README.md
```

---

## Dependencies

```
psrqpy astropy pandas scikit-learn pyarrow scipy matplotlib
```

The heatmap analysis requires `analysis/milkyway-full.webp`, a top-down infrared illustration of the Milky Way based on GLIMPSE survey data (Spitzer Space Telescope, NASA/JPL-Caltech). Calibrated with two reference points: Galactic center at pixel (2808, 2790) and the Sun at (2793, 3879), yielding ~0.00746 kpc/pixel.

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
Victor Seraco. Neutron Star Project (2025). https://github.com/ViSerac/neutron-star-project
```

---

## License

Code: MIT License. Data: CC BY 4.0. See [LICENSE](LICENSE).

## Contact

seraco.nsproj@gmail.com
