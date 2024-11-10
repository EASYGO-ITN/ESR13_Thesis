import numpy as np
import matplotlib.pyplot as plt
import tikzplotlib
from cycler import cycler

ts=[100,110,120,130,140,150,160,170,180,190,200]
s_NaCl=[0,0.1,0.2,0.3]
s_NCG=[0,0.025,0.05,0.075]
ps_NaCl=[[1.01332883,1.43206525,1.98382281,2.69831838,3.60897491,4.75292844,6.17099981,7.90766027,10.0109236,12.5323195,15.5268135],[0.953434508,1.34769276,1.86737105,2.54055782,3.39885964,4.47640207,5.8140898,7.45136415,9.43748458,11.8168986,14.6430085],[0.886120221,1.25302271,1.73691634,2.36410994,3.16423413,4.17024883,5.41799728,6.94708898,8.80210229,11.0260644,13.6686461],[0.817598089,1.15669107,1.60416042,2.18445831,2.92513654,3.85684996,5.01332359,6.42975023,8.14905756,10.2127584,12.663908]]
ps_NCG=[[1.01332883,1.43206525,1.98382281,2.69831838,3.60897491,4.75292844,6.17099981,7.90766027,10.0109236,12.5323195,15.5268135],[1.11771903,1.57991823,2.18919427,2.97856163,3.98522846,5.25065772,6.82055935,8.74487943,11.0777943,13.8776023,17.2069516],[1.22225823,1.72805284,2.39508611,3.25969806,4.36302273,5.75093743,7.47423692,9.58862852,12.1547321,15.2383372,18.9103017],[1.32694489,1.87646689,2.60146395,3.54174579,4.74234333,6.25375799,8.13206051,10.4389907,13.242035,16.6149404,20.637636]]

c = plt.get_cmap('tab20c').colors
plt.rcParams['axes.prop_cycle'] = cycler(color=c)

fig, ax = plt.subplots()

offset = 4
ps_NCG.reverse()
s_NCG.reverse()

ax.plot(ts, [-0.5 for t in ts], color=c[offset], label="NCG content/\\unit{\\kg\\per\\kg}")
for i, ps in enumerate(ps_NCG):
    if i != 3:
        ax.plot(ts, ps, color= c[offset+i], label="\\quad{:.3f}".format(s_NCG[i]))
    # else:
    #

ax.plot(ts, ps_NCG[-1], label="Pure Water")

offset = 12
for i, ps in enumerate(ps_NaCl):
    if i != 0:
        ax.plot(ts, ps, color= c[offset-i-1], label="\\quad{:.1f}".format(s_NaCl[i]))
    else:
        ax.plot(ts, [-0.5 for t in ts], color=c[offset-4], label="Salinity/\\unit{\\kg\\per\\kg}")


ax.set_xlabel("Temperature/\\unit{\\degreeCelsius}")
ax.set_ylabel("Saturation Pressure/\\unit{\\bar}")
ax.set_ylim((0, None))

ax.legend()


tikzplotlib.save("DeltaPsat.tex")

plt.show()