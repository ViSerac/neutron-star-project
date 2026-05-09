import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.image import imread
from scipy.stats import gaussian_kde
from astropy.coordinates import Galactocentric
import astropy.units as u

def load_milkyway_background():
    img = imread("milkyway-full.webp")  # same folder as analysis/
    gc = Galactocentric()
    sun_dist_kpc = gc.galcen_distance.to_value(u.kpc)

    cx_px, cy_px = 2808, 2790
    sx_px, sy_px = 2793, 3879
    dist_px = np.sqrt((sx_px - cx_px)**2 + (sy_px - cy_px)**2)
    kpc_per_px = sun_dist_kpc / dist_px

    img_h, img_w = img.shape[:2]
    # pixel y cresce para baixo → y_kpc = -(py - cy_px) * kpc_per_px
    left   = -cx_px * kpc_per_px
    right  = (img_w - cx_px) * kpc_per_px
    top    =  cy_px * kpc_per_px
    bottom = -(img_h - cy_px) * kpc_per_px
    return img, [left, right, bottom, top]

def add_milkyway_background(ax, alpha=0.6):
    img, extent = load_milkyway_background()
    ax.imshow(img, extent=extent, origin="upper", aspect="equal", alpha=alpha, zorder=0)

def analyze_heatmap(input_path="../data/NS_db_full.parquet"):
    df = pd.read_parquet(input_path)
    df_mw = df[df["galaxy"] == "milky_way"].dropna(subset=["x", "y"])

    print(f"Milky Way objects: {len(df_mw)}")

    type_colors = {
        "pulsar":                       (0x60/255, 0xa5/255, 0xfa/255),  # azul claro
        "magnetar":                     (1.0, 0.3, 0.1),                 # vermelho
        "candidate_magnetar":           (1.0, 0.6, 0.2),                 # laranja
        "pulsar_outburst_2006":         (0.7, 0.3, 1.0),                 # roxo
        "M7 isolated neutron star":     (0.4, 0.9, 1.0),                 # ciano
        "central compact object (CCO)": (0.8, 1.0, 0.2),                 # amarelo-verde
    }

    # Raw scatter — all combined
    fig, ax = plt.subplots(figsize=(8, 8))
    add_milkyway_background(ax)
    ax.scatter(df_mw["x"], df_mw["y"], s=2, alpha=0.7, zorder=1)
    ax.set_xlabel("x (kpc)")
    ax.set_ylabel("y (kpc)")
    ax.set_title("Neutron Stars — Milky Way (raw scatter)")
    ax.set_aspect("equal")
    plt.tight_layout()
    plt.savefig("../plots/heatmap_scatter.png")
    plt.show()

    # Raw scatter — pulsars vs magnetars
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    for ax, (title, group) in zip(axes, {
        "Pulsars (ATNF)":     df_mw[df_mw["source_catalog"] == "ATNF"],
        "Magnetars (McGill)": df_mw[df_mw["source_catalog"] == "McGill"],
    }.items()):
        add_milkyway_background(ax)
        for t, subgroup in group.groupby("type"):
            color = type_colors.get(t, (0.5, 0.5, 0.5))
            ax.scatter(subgroup["x"], subgroup["y"], s=5, alpha=0.8, color=color, label=t, zorder=1)
        ax.legend(fontsize=7, markerscale=2)
        ax.set_xlabel("x (kpc)")
        ax.set_ylabel("y (kpc)")
        ax.set_title(f"Raw scatter — {title}")
        ax.set_aspect("equal")
    plt.tight_layout()
    plt.savefig("../plots/heatmap_scatter_by_type.png")
    plt.show()

    # Hexbin heatmap — all combined
    fig, ax = plt.subplots(figsize=(8, 8))
    add_milkyway_background(ax)
    hb = ax.hexbin(df_mw["x"], df_mw["y"], gridsize=50, cmap="inferno", mincnt=1, alpha=1.0, zorder=1)
    plt.colorbar(hb, ax=ax, label="Count")
    ax.set_xlabel("x (kpc)")
    ax.set_ylabel("y (kpc)")
    ax.set_title("Neutron Stars — Milky Way (hexbin density)")
    ax.set_aspect("equal")
    plt.tight_layout()
    plt.savefig("../plots/heatmap_hexbin.png")
    plt.show()

    # Hexbin heatmap — pulsars vs magnetars
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    for ax, (title, group) in zip(axes, {
        "Pulsars (ATNF)":     df_mw[df_mw["source_catalog"] == "ATNF"],
        "Magnetars (McGill)": df_mw[df_mw["source_catalog"] == "McGill"],
    }.items()):
        gridsize = 50 if len(group) > 100 else 10
        add_milkyway_background(ax)
        hb = ax.hexbin(group["x"], group["y"], gridsize=gridsize, cmap="inferno", mincnt=1, alpha=1.0, zorder=1)
        plt.colorbar(hb, ax=ax, label="Count")
        ax.set_xlabel("x (kpc)")
        ax.set_ylabel("y (kpc)")
        ax.set_title(f"Hexbin — {title}")
        ax.set_aspect("equal")
    plt.tight_layout()
    plt.savefig("../plots/heatmap_hexbin_by_type.png")
    plt.show()

    # KDE heatmap
    x = df_mw["x"].values
    y = df_mw["y"].values

    kde = gaussian_kde(np.vstack([x, y]))

    _, img_extent = load_milkyway_background()
    x_grid = np.linspace(img_extent[0], img_extent[1], 200)
    y_grid = np.linspace(img_extent[2], img_extent[3], 200)
    xx, yy = np.meshgrid(x_grid, y_grid)
    zz = kde(np.vstack([xx.ravel(), yy.ravel()])).reshape(xx.shape)

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_facecolor("black")
    add_milkyway_background(ax)
    cf = ax.contourf(xx, yy, zz, levels=30, cmap="inferno", alpha=0.65, zorder=1)
    plt.colorbar(cf, ax=ax, label="Density")
    ax.set_xlabel("x (kpc)")
    ax.set_ylabel("y (kpc)")
    ax.set_title("Neutron Stars — Milky Way (KDE density)")
    ax.set_aspect("equal")
    ax.set_xlim(img_extent[0], img_extent[1])
    ax.set_ylim(img_extent[2], img_extent[3])
    plt.tight_layout()
    plt.savefig("../plots/heatmap_kde.png")
    plt.show()


if __name__ == "__main__":
    analyze_heatmap()
