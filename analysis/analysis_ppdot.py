import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def analyze_ppdot(input_path1 = "../data/atnf_full.parquet", input_path2 = "../data/mcgill_full.parquet"):
    df_atnf = pd.read_parquet(input_path1)
    df_mcgill = pd.read_parquet(input_path2)
    
    df_combined = pd.concat([df_atnf, df_mcgill], ignore_index=True)
    
    print(f"Total entries before filtering: {len(df_combined)}")
    df_filtered = df_combined.dropna(subset=["P", "PDOT"])
    print(f"Total entries after filtering: {len(df_filtered)}")

    df_filtered = df_filtered[df_filtered["PDOT"] > 0].copy()
    df_filtered["log_P"] = np.log10(df_filtered["P"])
    df_filtered["log_PDOT"] = np.log10(df_filtered["PDOT"])
    df_filtered["B"] = 3.2e19 * np.sqrt(df_filtered["P"] * df_filtered["PDOT"])
    df_filtered["tau_yr"] = df_filtered["P"] / (2 * df_filtered["PDOT"]) / 3.15e7

    print("Log(P) statistics:")
    print(df_filtered["log_P"].describe())

    print("\nLog(PDOT) statistics:")
    print(df_filtered["log_PDOT"].describe())

    log_P_range = np.linspace(df_filtered["log_P"].min() - 0.5, df_filtered["log_P"].max() + 0.5, 300)
    B_values = [1e12, 1e14, 1e15]
    B_labels = ["B = 10¹² G", "B = 10¹⁴ G", "B = 10¹⁵ G"]
    B_styles = ["--", "-.", ":"]

    catalog_colors = {"ATNF": (0x60/255, 0xa5/255, 0xfa/255), "McGill": (0xff/255, 0x4d/255, 0x1a/255)}

    plt.figure(figsize=(10, 6))
    for catalog, group in df_filtered.groupby("source_catalog"):
        color = catalog_colors.get(catalog, (0.5, 0.5, 0.5))
        plt.scatter(group["log_P"], group["log_PDOT"], alpha=0.6, color=color, label=catalog, s=20)

    for B, label, style in zip(B_values, B_labels, B_styles):
        log_PDOT_iso = 2 * np.log10(B) - 2 * np.log10(3.2e19) - log_P_range
        plt.plot(log_P_range, log_PDOT_iso, style, label=label, linewidth=1.5)

    yr_to_s = 3.15e7
    tau_values = [1e3, 1e6, 1e9]
    tau_labels = ["τ = 10³ yr", "τ = 10⁶ yr", "τ = 10⁹ yr"]
    tau_colors = ["tomato", "orange", "gold"]

    for tau_yr, label, color in zip(tau_values, tau_labels, tau_colors):
        tau_s = tau_yr * yr_to_s
        log_PDOT_tau = log_P_range - np.log10(2 * tau_s)
        plt.plot(log_P_range, log_PDOT_tau, color=color, linewidth=1.5, label=label)

    log_PDOT_death = np.log10(1.7e-20) + (11/4) * log_P_range
    plt.plot(log_P_range, log_PDOT_death, color="gray", linewidth=1.5, linestyle="-", label="Pulsar death line")

    plt.legend()
    plt.xlabel("log10(Period [s])")
    plt.ylabel("log10(Period Derivative [s/s])")
    plt.title("P-PDOT Diagram for Neutron Stars")
    save_path = "../plots/ppdot_diagram.png"
    plt.savefig(save_path)
    plt.show()
    
if __name__ == "__main__":
    analyze_ppdot()
