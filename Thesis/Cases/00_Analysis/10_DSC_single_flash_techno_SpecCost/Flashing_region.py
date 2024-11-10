import CoolProp as cp
import json
import numpy as np
import matplotlib.pyplot as plt
from CoolProp.CoolProp import PropsSI
import tikzplotlib
from matplotlib import cm
import matplotlib


with open("../../10_DSC_single_flash_techno_specCost/sensitivity_results.json", "r") as file:
    results = json.load(file)

ts = []
qs = []
for result in results:
    if result:
        ts.append(result["Hot fluid input1"])
        qs.append(result["Hot fluid input2"])

ts = list(set(ts))
ts.sort()
qs = list(set(qs))
qs.sort()

Pins = [[np.NAN + 0 for q in qs] for t in ts]
Xflashs = [[np.NAN + 0 for q in qs] for t in ts]

for result in results:
    if result:

        t_id = ts.index(result["Hot fluid input1"])
        q_id = qs.index(result["Hot fluid input2"])

        Pins[t_id][q_id] = result["Pin"]
        Xflashs[t_id][q_id] = result["Xflash"]

if __name__ == "__main__":
    fig, ax = plt.subplots()

    water = cp.AbstractState("?", "water")

    Tcrit = water.T_critical()
    water.update(cp.QT_INPUTS, 0, 423.15)
    Tmin = 298

    Nt = 50
    ts_ = np.linspace(Tcrit, Tmin, Nt)
    qs_ = [0.0, 0.15, 0.7, 1.0]
    for i, q in enumerate(qs_):
        ps_ = np.zeros(Nt)
        hs_ = np.zeros(Nt)

        for j, t in enumerate(ts_):
            water.update(cp.QT_INPUTS, q, t)
            ps_[j] = water.p()
            hs_[j] = water.hmass()

        if q in [0.0, 1.0]:
            ax.plot(hs_*1e-3, ps_*1e-5, "k")
        else:
            ax.plot(hs_*1e-3, ps_*1e-5, "k:")

            water.update(cp.PQ_INPUTS, 0.1e5, q)
            h = water.hmass()*1e-3
            label = "\\(x=" + "{:.0f}".format(q * 100) + "\\)\\unit{\\percent}"
            ax.annotate(label, (h + 50, 0.1*1.1), size=12)

    Tmax = 548.15
    water.update(cp.QT_INPUTS, 0, Tmax)
    Pmax = water.p()*1e-5
    ax.plot([0, 3000], [Pmax,Pmax], color="tab:red")
    label="\\(T_{geo}=" + "{:.0f}".format(Tmax) + "\\)\\unit{\\K}"
    ax.annotate(label, (0, Pmax*1.15), size=12)

    Tmin = 423.15
    water.update(cp.QT_INPUTS, 0, Tmin)
    Pmin = water.p()*1e-5
    ax.plot([0, 3000], [Pmin,Pmin], color="tab:blue")
    label = "\\(T_{geo}=" + "{:.0f}".format(Tmin) + "\\)\\unit{\\K}"
    ax.annotate(label, (0, Pmin*1.15), size=12)

    Tins = [Tmax, Tmin]
    for t in Tins:

        water.update(cp.QT_INPUTS, 0.15, t)
        hin = water.hmass()
        pin = water.p()

        p = pin * 0.5
        h = hin

        water.update(cp.HmassP_INPUTS, h, p)
        x = water.Q()

        ax.plot([hin*1e-3, h*1e-3], [pin*1e-5, p*1e-5], "o-")
        label = "\\(x=" + "{:.0f}".format(x*100) + "\\)\\unit{\\percent}"
        ax.annotate(label, (hin*1e-3 + 50, p*1e-5*0.9), size=12)

    Tins = [Tmax, Tmin]
    for t in Tins:

        water.update(cp.QT_INPUTS, 0.7, t)
        hin = water.hmass()
        pin = water.p()

        p = pin * 0.5
        h = hin

        water.update(cp.HmassP_INPUTS, h, p)
        x = water.Q()

        ax.plot([hin*1e-3, h*1e-3], [pin*1e-5, p*1e-5], "o-")
        label = "\\(x=" + "{:.0f}".format(x * 100) + "\\)\\unit{\\percent}"
        ax.annotate(label, (hin*1e-3 + 75, p*1e-5*0.9), size=12)


    ax.set_xlabel("Specific Enthalpy/\\unit{\\kilo\\joule\\per\\kg}")
    ax.set_ylabel("Pressure/\\unit{\\bar}")
    ax.set_ylim(0.1, 300)
    ax.set_yscale("log")

tikzplotlib.save("Plots/SingleFlash_flashing_degree.tex")

plt.show()

if __name__ == "__main__":

    matplotlib.use("pgf")

    matplotlib.rcParams.update({
        "pgf.texsystem": "pdflatex",
        "figure.figsize": (4.9, 3.5),
        'font.family': 'serif',
        "font.size": 12.0,
        'text.usetex': True,
        "text.latex.preamble": "\\usepackage{amsmath}\\usepackage{amssymb}\\usepackage{siunitx}",
        'pgf.rcfonts': False,
    })

    Xflash_ = np.empty((len(Xflashs), len(qs)))

    for i, Xflash in enumerate(Xflashs):
        for j, x in enumerate(Xflash):

            Xflash_[i][j] = (1 - x)*100


    def fmt(x):
        s = f"{x:.1f}"
        if s.endswith("0"):
            s = f"{x:.0f}"
        return rf"{s} \%" if plt.rcParams["text.usetex"] else f"{s} %"


    qs_per = [q*100 for q in qs]

    fig, ax = plt.subplots()
    cs = ax.contourf(qs_per, ts, Xflash_, levels=20, cmap=cm.Oranges, vmin=0.0, vmax=100)

    bs = ax.contour(qs_per, ts, Xflash_, linewidths=1, linestyles="--", colors="k", levels=[10, 20, 40, 60, 80, 100], vmin=0.0, vmax=100)
    ax.clabel(bs, bs.levels, inline=True, fmt=fmt, fontsize=9)

    ax.set_xlabel("Geofluid Vapour Quality/percent")
    ax.set_ylabel("Geofluid Temperature/K")

    fig.colorbar(cs, label="Degree of Flashing/percent")

    plt.tight_layout()
    plt.savefig('Plots/SingleFlash_flashing_region.pgf')

# This is now LEGACY
if __name__ == "__main_":
    target_xflash = [0.95, 0.9, 0.8, 0.6, 0.3]
    ps = [[] for tar in target_xflash]
    hs = [[] for tar in target_xflash]

    for i, target in enumerate(target_xflash):

        for j, Xflash in enumerate(Xflashs):

            diff = np.array(Xflash) - target
            if diff.min() < 0.0 < diff.max():
                break_q = np.interp(0, diff, qs)

                p = Pins[j][0]
                water.update(cp.PQ_INPUTS, p, break_q)
                h = water.hmass() * 1.e-3

                ps[i].append(p)
                hs[i].append(h)

    qs_per = [q * 100 for q in qs]
    ps_bar = [[p*1e-5 for p in t] for t in ps]
    ps_env_bar = [p*1e-5 for p in envelope.p]
    h_env_kilo = [h*1e-3/0.018 for h in envelope.hmolar_vap]


    h_high = [PropsSI("Hmass", "T", max(ts), "Q", 0, "water")*1e-3,
              PropsSI("Hmass", "T", max(ts), "Q", 1, "water")*1e-3]
    p_high = [PropsSI("P", "T", max(ts), "Q", 0, "water"),
              PropsSI("P", "T", max(ts), "Q", 1, "water")]
    p_high_bar = [p*1e-5 for p in p_high]
    t_high = max(ts)

    h_low = [PropsSI("Hmass", "T", min(ts), "Q", 0, "water")*1e-3,
              PropsSI("Hmass", "T", min(ts), "Q", 1, "water")*1e-3]
    p_low = [PropsSI("P", "T", min(ts), "Q", 0, "water"),
              PropsSI("P", "T", min(ts), "Q", 1, "water")]
    p_low_bar = [p*1e-5 for p in p_low]
    t_low = min(ts)


    fig, ax = plt.subplots()

    ax.plot(h_env_kilo, ps_env_bar, "k--", label="Saturation Line")

    ax.plot(h_high, p_high_bar, "k")
    ax.annotate("{:.0f} K".format(t_high), (h_high[0], p_high_bar[0]), )

    ax.plot(h_low, p_low_bar, "k")
    ax.annotate("{:.0f} K".format(t_low), (h_low[0], p_low_bar[0]), )

    for i, p in enumerate(ps_bar):
        ax.plot(hs[i], ps_bar[i],)
        ax.plot(hs[i], ps_bar[i],)

    ax.annotate("Flash", ((h_high[0] + h_low[0])/2*1.3, (p_high_bar[0] + p_low_bar[0])/2*0.8), )
    ax.annotate("No-Flash", ((h_high[1] + h_low[1])/2*0.8, (p_high_bar[1] + p_low_bar[1])/2*0.5), )

    ax.set_yscale("log")
    ax.set_ylim(0.1, 400)

    ax.set_xlabel("Specific Enthalpy/\\unit{\\joule\\per\\kg}")
    ax.set_ylabel("Pressure/\\unit{\\bar}")

    # tikzplotlib.save("Plots/SingleFlash_flashing_region.tex")





