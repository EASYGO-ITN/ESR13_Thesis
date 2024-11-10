import matplotlib.pyplot as plt
from matplotlib import cm
import matplotlib

import tikzplotlib

matplotlib.use("pgf")

matplotlib.rcParams.update({
    "pgf.texsystem": "pdflatex",
       "figure.figsize" : (4.9, 3.5),
    'font.family': 'serif',
       "font.size":    12.0,
    'text.usetex': True,
       "text.latex.preamble": "\\usepackage{amsmath}\\usepackage{amssymb}\\usepackage{siunitx}",
    'pgf.rcfonts': False,
})

qs = [0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5]
qs = [q*100 for q in qs]
ts = [100, 105, 110, 115, 120, 125, 130, 135, 140, 145, 150, 155, 160, 165, 170, 175, 180, 185, 190, 195, 200]

pws = [[13, 18,	35,	53,	71,	88,	106,	123,	141,	159,	176],
       [15,	21,	38,	56,	75,	93,	112,	131,	149,	168,	186],
       [17,	24,	41,	59,	79,	98,	118,	137,	157,	177,	196],
       [19,	27,	44,	62,	82,	103,	124,	144,	165,	185,	206],
       [22,	30,	47,	65,	86,	108,	129,	151,	172,	194,	215],
       [25,	33,	50,	69,	90,	112,	134,	157,	179,	202,	224],
       [28,	36,	53,	72,	93,	116,	140,	163,	186,	210,	233],
       [31,	39,	56,	76,	97,	121,	145,	169,	193,	217,	241],
       [35,	42,	60,	79,	101,	125,	150,	175,	200,	225,	250],
       [39,	45,	63,	83,	105,	129,	155,	180,	206,	232,	258],
       [44,	48,	66,	86,	109,	133,	159,	186,	212,	239,	265],
       [49,	53,	70,	90,	112,	137,	164,	191,	218,	246,	273],
       [55,	60,	73,	94,	116,	141,	168,	196,	224,	252,	280],
       [61,	68,	77,	97,	120,	146,	173,	201,	230,	259,	288],
       [68,	76,	85,	101,	124,	150,	177,	206,	236,	265,	295],
       [74,	86,	97,	109,	129,	154,	181,	211,	241,	271,	301],
       [80,	91,	102,	113,	133,	158,	185,	216,	246,	277,	308],
       [85,	95,	106,	117,	137,	163,	190,	220,	251,	283,	314],
       [91,	108,	125,	142,	159,	176,	195,	224,	256,	288,	320],
       [98,	114,	131,	147,	164,	181,	200,	228,	261,	294,	326],
       [105,	121,	137,	153,	169,	185,	204,	233,	266,	299,	332]]

boundary_ts = [100,155,155,170,170,175,175,190,190,205,205,]
boundary_qs = [0.025, 0.025,0.075,0.075,0.125,0.125,0.175,0.175,0.225,0.225,0.275,]
boundary_qs = [q*100 for q in boundary_qs]

fig, ax = plt.subplots()

cs = ax.contourf(qs, ts, pws, cmap=cm.Oranges)
# fig.colorbar(cs, label="Specific net power/\\unit{\\kilo\\watt\\s\\per\\kg}")
fig.colorbar(cs, label="Specific net power/kW s kg-1")

ax.plot(boundary_qs, boundary_ts, color="grey")
ax.set_ylim((100, 200))

# ax.set_xlabel("Steam Quality/\\unit{\\percent}")
# ax.set_ylabel("Inlet Temperature/\\unit{\\degreeCelsius}")
#
ax.set_xlabel("Steam Quality/\\%")
ax.set_ylabel("Inlet Temperature/degC")

ax.annotate("ORC", (5, 182))
ax.annotate("DSC", (32, 150))

plt.tight_layout()

plt.savefig('PureWater_TQ_map.pgf')

# plt.show()