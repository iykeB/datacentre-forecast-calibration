"""Figures for the data centre forecast calibration paper.

Reads results/*.json and data/; writes figures/Figure_1..5 (vector PDF, Arial embedded, plus PNG).
Run: python code/make_figures.py
"""
import csv, json, os, collections
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = lambda *p: os.path.join(R, *p)
os.makedirs(D("figures"), exist_ok=True)

BLUE, ORANGE, AQUA, VIOLET, RED = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7", "#e34948"
INK, INK2, MUTED, GRID = "#0b0b0b", "#52514e", "#8a8984", "#e6e5e1"
plt.rcParams.update({
    "font.family": "Arial", "font.size": 7.5, "axes.labelsize": 7.5, "xtick.labelsize": 7,
    "ytick.labelsize": 7, "legend.fontsize": 7, "axes.edgecolor": INK2, "axes.labelcolor": INK,
    "xtick.color": INK2, "ytick.color": INK2, "axes.linewidth": 0.6, "axes.spines.top": False,
    "axes.spines.right": False, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.5,
    "axes.axisbelow": True, "legend.frameon": False, "lines.linewidth": 1.4,
    "pdf.fonttype": 42, "ps.fonttype": 42, "mathtext.fontset": "custom",
    "mathtext.rm": "Arial", "mathtext.it": "Arial:italic", "mathtext.bf": "Arial:bold",
})
MM = 1 / 25.4
S = json.load(open(D("results/ireland_scoring.json")))
O = json.load(open(D("results/ireland_outlook_exergy.json")))
X = json.load(open(D("results/external_checks.json")))


def save(fig, name):
    fig.savefig(D("figures", name + ".pdf"), bbox_inches="tight", facecolor="white")
    fig.savefig(D("figures", name + ".png"), bbox_inches="tight", facecolor="white", dpi=600)
    plt.close(fig)


def panel(ax, letter):
    ax.text(-0.01, 1.03, f"({letter})", transform=ax.transAxes, fontsize=8.5, fontweight="bold",
            ha="right", va="bottom", color=INK)


def edition_cbar(fig, ax, eds, cmap):
    import matplotlib as mpl
    yrs = [edition_year(e) for e in eds]
    norm = mpl.colors.Normalize(vmin=min(yrs), vmax=max(yrs))
    sm = mpl.cm.ScalarMappable(norm=mpl.colors.Normalize(0, 1), cmap=mpl.colors.ListedColormap([cmap(0.35 + 0.6 * i / 99) for i in range(100)]))
    cb = fig.colorbar(sm, ax=ax, fraction=0.04, pad=0.02)
    cb.set_ticks([(y - min(yrs)) / (max(yrs) - min(yrs)) for y in (2015, 2018, 2021, 2023, 2026)])
    cb.set_ticklabels(["2015", "2018", "2021", "2023", "2026"]); cb.set_label("Edition year", fontsize=7); cb.outline.set_visible(False)
    cb.ax.tick_params(labelsize=6.5)


def edition_year(e):
    return int(e.split()[1][:4])


def cso_series():
    a = collections.defaultdict(lambda: collections.defaultdict(float))
    for x in csv.DictReader(open(D("data/cso/mec02.csv"), encoding="utf-8-sig")):
        a[x["Electricity Consumption"]][int(x["Quarter"][:4])] += float(x["VALUE"]) / 1000
    return a


# ---------------------------------------------------------------- Figure 1: framework schematic
def fig1():
    fig, ax = plt.subplots(figsize=(180 * MM, 78 * MM))
    ax.set_xlim(0, 100); ax.set_ylim(0, 44); ax.axis("off")

    def box(x, y, w, h, title, body, edge):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4,rounding_size=1.2",
                                    fc="white", ec=edge, lw=1.0))
        ax.text(x + w / 2, y + h - 1.6, title, ha="center", va="top", fontsize=7.5, fontweight="bold", color=INK)
        ax.text(x + w / 2, y + h - 5.0, body, ha="center", va="top", fontsize=6.6, color=INK2, linespacing=1.35)

    def arrow(x1, y1, x2, y2):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=8, lw=0.9, color=INK2))

    box(1, 25, 22, 17, "Published outlooks", "EirGrid capacity statements\n11 editions, 2015 to 2026\nLow, Median, High\nby target year", BLUE)
    box(1, 3, 22, 17, "Metered outcomes", "CSO data centre and\ntotal metered electricity\n2015 to 2025; ratio r\n(Eq. 1)", BLUE)
    box(28, 14, 20, 17, "1  Score editions", "coverage of the published\nrange, signed error, interval\nscore, CRPS by horizon\n(Eqs. 2 to 5)", VIOLET)
    box(53, 14, 20, 17, "2  Recalibrate", "horizon scaled log errors\nsplit conformal quantiles\nleave one edition out\n(Eqs. 6 to 8)", VIOLET)
    box(78, 25, 21, 17, "3  Calibrated outlook", "total demand and the\ndata centre component\nto 2035\n(Eqs. 9, 10)", ORANGE)
    box(78, 3, 21, 17, "4  Energy and exergy", "balances by stage,\navoidable destruction,\nrecoverable heat exergy\n(Eqs. 11 to 16)", ORANGE)
    arrow(23.5, 33, 28, 25); arrow(23.5, 11.5, 28, 20)
    arrow(48.5, 22.5, 53, 22.5); arrow(73.5, 25, 78, 31); arrow(88.5, 25, 88.5, 20.5)
    ax.text(50.5, 8.5, "External checks: Netherlands (CBS, PBL)\nand Great Britain (DESNZ, NESO);\nforecaster baselines and scenario\nranges against metered data",
            ha="center", va="top", fontsize=6.6, color=AQUA, style="italic")
    save(fig, "Figure_1")


# ---------------------------------------------------------------- Figure 2: editions against outcomes
def fig2():
    rows = list(csv.DictReader(open(D("data/eirgrid_gcs/ter_vintages.csv"))))
    med = collections.defaultdict(dict)
    for x in rows:
        if x["scenario"].lower().startswith("med") and x["ter_twh_ireland"] and x["note"] == "forecast":
            med[x["edition"].split(" (")[0]][int(x["year"])] = float(x["ter_twh_ireland"])
    eds = sorted(med, key=edition_year)
    cmap = plt.get_cmap("Blues")
    fig, (a, b) = plt.subplots(1, 2, figsize=(180 * MM, 66 * MM), gridspec_kw=dict(width_ratios=[1.35, 1]))
    for i, e in enumerate(eds):
        ys = sorted(med[e]); c = cmap(0.35 + 0.6 * i / (len(eds) - 1))
        a.plot(ys, [med[e][y] for y in ys], color=c, lw=1.1)
    rep = {int(k): v for k, v in S["outcome"]["reported"].items()}
    der = {int(k): v for k, v in S["outcome"]["derived"].items()}
    a.plot(sorted(rep), [rep[y] for y in sorted(rep)], "o", ms=3.6, color=INK, label="Outcome reported by EirGrid", zorder=5)
    a.plot(sorted(der), [der[y] for y in sorted(der)], "o", ms=3.6, mfc="white", mec=INK, label="Outcome from CSO metered data (Eq. 1)", zorder=5)
    a.plot([], [], color=cmap(0.7), label="Median forecast, by edition year")
    edition_cbar(fig, a, eds, cmap)
    a.set_xticks(range(2015, 2036, 5)); a.set_xlim(2013.5, 2035.8); a.set_ylabel("Total electricity requirement (TWh)"); a.set_xlabel("Target year")
    a.legend(loc="upper left"); panel(a, "a")
    c = cso_series(); yrs = list(range(2015, 2026))
    b.plot(yrs, [c["Data centres"][y] for y in yrs], "-o", ms=3, color=ORANGE, label="Data centres")
    b.plot(yrs, [c["Customers other than data centres"][y] for y in yrs], "-s", ms=3, color=BLUE, label="All other customers")
    b.set_ylabel("Metered electricity (TWh)"); b.set_xlabel("Year"); b.set_ylim(0, 28)
    b.legend(loc="center left"); panel(b, "b")
    fig.tight_layout(w_pad=2.0); save(fig, "Figure_2")


# ---------------------------------------------------------------- Figure 3: scores
def fig3():
    P = S["published_ranges"]; bands = ["1-2", "3-5", "6-10"]
    cal = collections.defaultdict(list)
    ks = {l["edition"]: l["kappa"] for l in S["leave_one_edition_out"]["by_edition"]}
    import math
    for p in S["pairs"]:
        k = ks[p["edition"]]; r = math.sqrt(p["h"])
        lo = min(p["M"] * math.exp(k[0] * r), p["L"]); hi = max(p["M"] * math.exp(k[1] * r), p["H"])
        for bnd in bands:
            l, u = map(int, bnd.split("-"))
            if l <= p["h"] <= u: cal[bnd].append(lo <= p["A"] <= hi)
    fig, (a, b) = plt.subplots(1, 2, figsize=(180 * MM, 66 * MM), gridspec_kw=dict(width_ratios=[1, 1.3]))
    x = np.arange(len(bands)); w = 0.36
    pub = [100 * P[k]["coverage"] for k in bands]; cc = [100 * np.mean(cal[k]) for k in bands]
    a.bar(x - w / 2 - 0.01, pub, w, color=BLUE, label="Published Low to High range")
    a.bar(x + w / 2 + 0.01, cc, w, color=ORANGE, label="Recalibrated, edition held out")
    for i in range(len(bands)):
        a.text(x[i] - w / 2, pub[i] + 1.5, f"{pub[i]:.0f}", ha="center", fontsize=6.5, color=INK2)
        a.text(x[i] + w / 2, cc[i] + 1.5, f"{cc[i]:.0f}", ha="center", fontsize=6.5, color=INK2)
    a.axhline(90, color=INK, lw=0.8, ls="--"); a.text(2.62, 91.5, "90% target", fontsize=6.5, ha="right", color=INK)
    a.set_xticks(x); a.set_xticklabels([f"{k.replace('-', chr(8211))} years\n(n = {P[k]['n']})" for k in bands])
    a.set_ylim(0, 112); a.set_ylabel("Outcomes inside the interval (%)"); a.set_xlabel("Forecast horizon")
    a.legend(loc="lower left", bbox_to_anchor=(0, 1.04), ncol=1); panel(a, "a")
    by = collections.defaultdict(list)
    for p in S["pairs"]: by[p["edition"]].append(p)
    eds = sorted(by, key=edition_year); cmap = plt.get_cmap("Blues")
    for i, e in enumerate(eds):
        ps = sorted(by[e], key=lambda p: p["year"]); c = cmap(0.35 + 0.6 * i / (len(eds) - 1))
        b.plot([p["year"] for p in ps], [p["err_pct"] for p in ps], "-o", ms=2.6, color=c, lw=1.0)
    b.axhline(0, color=INK, lw=0.8); edition_cbar(fig, b, eds, cmap)
    b.set_ylabel("Median forecast error (%)"); b.set_xlabel("Target year"); b.set_xlim(2014.5, 2025.5)
    b.text(2014.8, 11, "forecast above outcome", fontsize=6.5, color=INK2); b.text(2014.8, -15.5, "forecast below outcome", fontsize=6.5, color=INK2)
    panel(b, "b")
    fig.tight_layout(w_pad=2.0); save(fig, "Figure_3")


# ---------------------------------------------------------------- Figure 4: external checks
def fig4():
    fig, (a, b, c) = plt.subplots(1, 3, figsize=(180 * MM, 62 * MM), gridspec_kw=dict(width_ratios=[1.15, 1, 1]))
    bl = X["baseline"]; bl = sorted(bl, key=lambda r: (r["country"], r["source"], r["year"]))
    y = np.arange(len(bl))
    for i, r in enumerate(bl):
        col = BLUE if r["country"] == "GB" else ORANGE
        a.plot([1, r["ratio"]], [i, i], color=col, lw=1.0); a.plot(r["ratio"], i, "o", ms=3.6, color=col)
    a.axvline(1, color=INK, lw=0.8)
    a.set_yticks(y); a.set_yticklabels([f"{r['source'].replace('NESO ', '')}, {r['year']}" for r in bl], fontsize=6.3)
    a.set_xlabel("Stated baseline / metered value"); a.invert_yaxis(); a.grid(axis="y", visible=False)
    a.plot([], [], "o", color=BLUE, label="Great Britain"); a.plot([], [], "o", color=ORANGE, label="Netherlands")
    a.legend(loc="lower right"); panel(a, "a")
    fs = X["fes_scores"]; lab = [f"{s['edition'][2:]}{chr(8594)}{str(s['year'])[2:]}" for s in fs]; xx = np.arange(len(fs))
    for i, s in enumerate(fs):
        b.plot([i, i], [s["level"]["lo"], s["level"]["hi"]], color=BLUE, lw=5, solid_capstyle="butt", alpha=0.55)
        b.plot(i, s["metered"], "D", ms=4, color=INK)
        g = s["growth"]; c.plot([i, i], [g["lo"], g["hi"]], color=BLUE, lw=5, solid_capstyle="butt", alpha=0.55)
        c.plot(i, g["metered"], "D", ms=4, color=INK)
    for ax_, yl, L in ((b, "Data centre demand (TWh)", "b"), (c, "Growth from base year (ratio)", "c")):
        ax_.set_xticks(xx); ax_.set_xticklabels(lab, fontsize=6.3, rotation=45, ha="right", rotation_mode="anchor"); ax_.set_xlabel("FES edition " + chr(8594) + " target year (20xx)"); ax_.set_ylabel(yl); ax_.set_xlim(-0.6, len(fs) - 0.4); panel(ax_, L)
    b.plot([], [], color=BLUE, lw=5, alpha=0.55, label="FES scenario range"); b.plot([], [], "D", color=INK, ms=4, label="DESNZ metered")
    b.legend(loc="upper left")
    fig.tight_layout(w_pad=1.6); save(fig, "Figure_4")


# ---------------------------------------------------------------- Figure 5: calibrated outlook
def fig5():
    Y = sorted(O["years"], key=int); yr = [int(y) for y in Y]; g = lambda k, i: [O["years"][y][k][i] for y in Y]
    fig, (a, b) = plt.subplots(1, 2, figsize=(180 * MM, 64 * MM))
    pubL = [O["years"][y]["published"]["low"] for y in Y]; pubH = [O["years"][y]["published"]["high"] for y in Y]
    pubM = [O["years"][y]["published"]["median"] for y in Y]
    a.fill_between(yr, g("ter_calibrated", 0), g("ter_calibrated", 2), color=ORANGE, alpha=0.25, lw=0, label="Calibrated 90% interval")
    a.plot(yr, pubM, color=BLUE, label="Published Median"); a.plot(yr, pubL, color=BLUE, ls="--", lw=0.9, label="Published Low and High"); a.plot(yr, pubH, color=BLUE, ls="--", lw=0.9)
    a.set_ylabel("Total electricity requirement (TWh)"); a.set_ylim(33, 62); a.legend(loc="upper left"); panel(a, "a")
    b.fill_between(yr, g("dc_metered", 0), g("dc_metered", 2), color=ORANGE, alpha=0.25, lw=0)
    b.plot(yr, g("dc_metered", 1), color=ORANGE, label="Facility energy, calibrated median and 90% interval")
    b.plot(yr, g("E_it", 1), color=VIOLET, ls="--", label="IT energy, median")
    cs = cso_series(); hy = list(range(2015, 2026))
    b.plot(hy, [cs["Data centres"][y] for y in hy], "o", ms=2.8, color=INK, label="CSO metered")
    b.set_ylabel("Data centre energy (TWh)"); b.set_ylim(0, 27); b.set_xticks(range(2015, 2036, 5)); b.legend(loc="upper left"); panel(b, "b")
    for ax_ in (a, b): ax_.set_xlabel("Year")
    fig.tight_layout(w_pad=2.0); save(fig, "Figure_5")


# ---------------------------------------------------------------- Figure 6: exergy accounting and sensitivity
def fig6():
    yrs = ["2025", "2030", "2035"]
    parts = [("D_it", "Destroyed: electricity to heat in IT", "#9a9a95"), ("D_ht", "Destroyed: chip to coolant transfer", VIOLET),
             ("D_cool", "Destroyed: cooling", BLUE), ("D_pc", "Destroyed: power conversion", ORANGE),
             ("Ex_rej", "Exergy of rejected heat", AQUA)]
    fig, (a, b) = plt.subplots(1, 2, figsize=(180 * MM, 70 * MM), gridspec_kw=dict(width_ratios=[1.05, 1]))
    x = np.arange(len(yrs)); bottom = np.zeros(len(yrs))
    for k, lab, col in parts:
        v = np.array([100 * O["years"][y]["share"][k][1] for y in yrs])
        a.bar(x, v, 0.55, bottom=bottom, color=col, label=lab, edgecolor="white", lw=0.6)
        for i in range(len(yrs)):
            if v[i] > 4: a.text(x[i], bottom[i] + v[i] / 2, f"{v[i]:.1f}", ha="center", va="center", fontsize=6.5, color="white" if k != "Ex_rej" else INK)
        bottom += v
    a.set_xticks(x); a.set_xticklabels(yrs); a.set_ylabel("Share of exergy input (%)"); a.set_ylim(0, 100)
    a.set_xlim(-0.5, 6.2); hs, ls = a.get_legend_handles_labels()
    a.legend(hs[::-1], ls[::-1], loc="center left", fontsize=6.3, bbox_to_anchor=(0.45, 0.5)); a.grid(axis="x", visible=False)
    a.spines["bottom"].set_bounds(-0.5, 2.5); panel(a, "a")
    keys = [("demand", "Demand (calibrated)"), ("pue", "PUE"), ("T_supply", "Heat supply temperature"), ("f_cap", "Capture fraction"), ("T0", "Dead state"), ("T_chip", "Chip temperature")]
    s1 = O["years"]["2030"]["sobol_first_Ex_rec"]; s2 = O["years"]["2030"]["sobol_first_D_av"]
    yy = np.arange(len(keys)); hgt = 0.36
    b.barh(yy - hgt / 2, [s1[k] for k, _ in keys], hgt, color=AQUA, label="Recoverable heat exergy")
    b.barh(yy + hgt / 2, [s2[k] for k, _ in keys], hgt, color=ORANGE, label="Avoidable exergy destruction")
    b.set_yticks(yy); b.set_yticklabels([l for _, l in keys]); b.invert_yaxis(); b.set_xlim(0, 0.8)
    b.set_xlabel("First order sensitivity index, 2030"); b.legend(loc="lower right"); b.grid(axis="y", visible=False); panel(b, "b")
    fig.tight_layout(w_pad=2.0); save(fig, "Figure_6")


if __name__ == "__main__":
    for f in (fig1, fig2, fig3, fig4, fig5, fig6): f()
    print("figures written to", D("figures"))
