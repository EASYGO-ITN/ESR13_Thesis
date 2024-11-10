from math import pow, log
import tikzplotlib
import matplotlib.pyplot as plt
import numpy as np

from CostConversion import Yref, convert_EUR_to_USD, calc_PPI

ccplantadjfactor = 1


class Geosphiresv2:

    @staticmethod
    def ORC_subcrit(T, Pow):
        MaxProducedTemperature = T
        ElectricityProduced = Pow

        if (MaxProducedTemperature < 150.):
            C3 = -1.458333E-3
            C2 = 7.6875E-1
            C1 = -1.347917E2
            C0 = 1.0075E4
            CCAPP1 = C3 * MaxProducedTemperature ** 3 + C2 * MaxProducedTemperature ** 2 + C1 * MaxProducedTemperature + C0
        else:
            CCAPP1 = 2231 - 2 * (MaxProducedTemperature - 150.)

        Cplantcorrelation = CCAPP1 * pow(ElectricityProduced / 15., -0.06) * ElectricityProduced * 1000. / 1E6

        Cplant = 1.12 * 1.15 * ccplantadjfactor * Cplantcorrelation * 1.02 * 1.1  # 1.02 to convert cost from 2012 to 2016 #factor 1.15 for 15% contingency and 1.12 for 12% indirect costs.

        return Cplant

    @staticmethod
    def ORC_supcrit(T, Pow):
        MaxProducedTemperature = T
        ElectricityProduced = Pow

        if (MaxProducedTemperature < 150.):
            C3 = -1.458333E-3
            C2 = 7.6875E-1
            C1 = -1.347917E2
            C0 = 1.0075E4
            CCAPP1 = C3 * MaxProducedTemperature ** 3 + C2 * MaxProducedTemperature ** 2 + C1 * MaxProducedTemperature + C0
        else:
            CCAPP1 = 2231 - 2 * (MaxProducedTemperature - 150.)

        Cplantcorrelation = 1.1 * CCAPP1 * pow(ElectricityProduced / 15., -0.06) * ElectricityProduced * 1000. / 1E6  # factor 1.1 to make supercritical 10% more expansive than subcritical

        Cplant = 1.12 * 1.15 * ccplantadjfactor * Cplantcorrelation * 1.02 * 1.1 # 1.02 to convert cost from 2012 to 2016 #factor 1.15 for 15% contingency and 1.12 for 12% indirect costs.

        return Cplant

    @staticmethod
    def Flash_single(T, Pow):
        MaxProducedTemperature = T
        ElectricityProduced = Pow

        if (ElectricityProduced < 10.):
            C2 = 4.8472E-2
            C1 = -35.2186
            C0 = 8.4474E3
            D2 = 4.0604E-2
            D1 = -29.3817
            D0 = 6.9911E3
            PLL = 5.
            PRL = 10.
        elif (ElectricityProduced < 25.):
            C2 = 4.0604E-2
            C1 = -29.3817
            C0 = 6.9911E3
            D2 = 3.2773E-2
            D1 = -23.5519
            D0 = 5.5263E3
            PLL = 10.
            PRL = 25.
        elif (ElectricityProduced < 50.):
            C2 = 3.2773E-2
            C1 = -23.5519
            C0 = 5.5263E3
            D2 = 3.4716E-2
            D1 = -23.8139
            D0 = 5.1787E3
            PLL = 25.
            PRL = 50.
        elif (ElectricityProduced < 75.):
            C2 = 3.4716E-2
            C1 = -23.8139
            C0 = 5.1787E3
            D2 = 3.5271E-2
            D1 = -24.3962
            D0 = 5.1972E3
            PLL = 50.
            PRL = 75.
        else:
            C2 = 3.5271E-2
            C1 = -24.3962
            C0 = 5.1972E3
            D2 = 3.3908E-2
            D1 = -23.4890
            D0 = 5.0238E3
            PLL = 75.
            PRL = 100.
        maxProdTemp = MaxProducedTemperature
        CCAPPLL = C2 * maxProdTemp ** 2 + C1 * maxProdTemp + C0
        CCAPPRL = D2 * maxProdTemp ** 2 + D1 * maxProdTemp + D0
        b = log(CCAPPRL / CCAPPLL) / log(PRL / PLL)
        a = CCAPPRL / PRL ** b

        Cplantcorrelation = 0.8 * a * pow(ElectricityProduced, b) * ElectricityProduced * 1000. / 1E6  # factor 0.75 to make double flash 25% more expansive than single flash

        Cplant = 1.12 * 1.15 * ccplantadjfactor * Cplantcorrelation * 1.02 * 1.1 # 1.02 to convert cost from 2012 to 2016 #factor 1.15 for 15% contingency and 1.12 for 12% indirect costs.

        return Cplant

    @staticmethod
    def Flash_dual(T, Pow):
        MaxProducedTemperature = T
        ElectricityProduced = Pow

        if (ElectricityProduced < 10.):
            C2 = 4.8472E-2
            C1 = -35.2186
            C0 = 8.4474E3
            D2 = 4.0604E-2
            D1 = -29.3817
            D0 = 6.9911E3
            PLL = 5.
            PRL = 10.
        elif (ElectricityProduced < 25.):
            C2 = 4.0604E-2
            C1 = -29.3817
            C0 = 6.9911E3
            D2 = 3.2773E-2
            D1 = -23.5519
            D0 = 5.5263E3
            PLL = 10.
            PRL = 25.
        elif (ElectricityProduced < 50.):
            C2 = 3.2773E-2
            C1 = -23.5519
            C0 = 5.5263E3
            D2 = 3.4716E-2
            D1 = -23.8139
            D0 = 5.1787E3
            PLL = 25.
            PRL = 50.
        elif (ElectricityProduced < 75.):
            C2 = 3.4716E-2
            C1 = -23.8139
            C0 = 5.1787E3
            D2 = 3.5271E-2
            D1 = -24.3962
            D0 = 5.1972E3
            PLL = 50.
            PRL = 75.
        else:
            C2 = 3.5271E-2
            C1 = -24.3962
            C0 = 5.1972E3
            D2 = 3.3908E-2
            D1 = -23.4890
            D0 = 5.0238E3
            PLL = 75.
            PRL = 100.
        maxProdTemp = MaxProducedTemperature
        CCAPPLL = C2 * maxProdTemp ** 2 + C1 * maxProdTemp + C0
        CCAPPRL = D2 * maxProdTemp ** 2 + D1 * maxProdTemp + D0
        b = log(CCAPPRL / CCAPPLL) / log(PRL / PLL)
        a = CCAPPRL / PRL ** b
        Cplantcorrelation = a * pow(ElectricityProduced, b) * ElectricityProduced * 1000. / 1E6

        Cplant = 1.12 * 1.15 * ccplantadjfactor * Cplantcorrelation * 1.02 * 1.1 # 1.02 to convert cost from 2012 to 2016 #factor 1.15 for 15% contingency and 1.12 for 12% indirect costs.

        return Cplant


class GeophiresX:

    @staticmethod
    def ORC_subcrit(T, Pow):

        MaxProducedTemperature = T
        ElectricityProduced = Pow

        if MaxProducedTemperature < 150.:
            C3 = -1.458333E-3
            C2 = 7.6875E-1
            C1 = -1.347917E2
            C0 = 1.0075E4
            CCAPP1 = C3 * MaxProducedTemperature ** 3 + C2 * MaxProducedTemperature ** 2 + C1 * MaxProducedTemperature + C0
        else:
            CCAPP1 = 2231 - 2 * (MaxProducedTemperature - 150.)
        x = ElectricityProduced*1
        y = ElectricityProduced*1
        if y == 0.0:
            y = 15.0
        z = pow(y / 15., -0.06)

        Cplantcorrelation = CCAPP1 * z * x * 1000. / 1E6

        # 1.02 to convert cost from 2012 to 2016 #factor 1.15 for 15% contingency and 1.12 for 12% indirect costs. factor 1.10 to convert from 2016 to 2022
        Cplant = 1.12 * 1.15 * ccplantadjfactor * Cplantcorrelation * 1.02 * 1.10

        return Cplant

    @staticmethod
    def ORC_supcrit(T, Pow):

        MaxProducedTemperature = T
        ElectricityProduced = Pow

        if MaxProducedTemperature < 150.:
            C3 = -1.458333E-3
            C2 = 7.6875E-1
            C1 = -1.347917E2
            C0 = 1.0075E4
            CCAPP1 = C3 * MaxProducedTemperature ** 3 + C2 * MaxProducedTemperature ** 2 + C1 * MaxProducedTemperature + C0
        else:
            CCAPP1 = 2231 - 2 * (MaxProducedTemperature - 150.)
        # factor 1.1 to make supercritical 10% more expansive than subcritical
        Cplantcorrelation = 1.1 * CCAPP1 * pow(ElectricityProduced / 15., -0.06) * ElectricityProduced * 1000. / 1E6

        # 1.02 to convert cost from 2012 to 2016 #factor 1.15 for 15% contingency and 1.12 for 12% indirect costs. factor 1.10 to convert from 2016 to 2022
        Cplant = 1.12 * 1.15 * ccplantadjfactor * Cplantcorrelation * 1.02 * 1.10

        return Cplant

    @staticmethod
    def Flash_single(T, Pow):

        MaxProducedTemperature = T
        ElectricityProduced = Pow

        if ElectricityProduced < 10.:
            C2 = 4.8472E-2
            C1 = -35.2186
            C0 = 8.4474E3
            D2 = 4.0604E-2
            D1 = -29.3817
            D0 = 6.9911E3
            PLL = 5.
            PRL = 10.
        elif ElectricityProduced < 25.:
            C2 = 4.0604E-2
            C1 = -29.3817
            C0 = 6.9911E3
            D2 = 3.2773E-2
            D1 = -23.5519
            D0 = 5.5263E3
            PLL = 10.
            PRL = 25.
        elif ElectricityProduced < 50.:
            C2 = 3.2773E-2
            C1 = -23.5519
            C0 = 5.5263E3
            D2 = 3.4716E-2
            D1 = -23.8139
            D0 = 5.1787E3
            PLL = 25.
            PRL = 50.
        elif ElectricityProduced < 75.:
            C2 = 3.4716E-2
            C1 = -23.8139
            C0 = 5.1787E3
            D2 = 3.5271E-2
            D1 = -24.3962
            D0 = 5.1972E3
            PLL = 50.
            PRL = 75.
        else:
            C2 = 3.5271E-2
            C1 = -24.3962
            C0 = 5.1972E3
            D2 = 3.3908E-2
            D1 = -23.4890
            D0 = 5.0238E3
            PLL = 75.
            PRL = 100.
        maxProdTemp = MaxProducedTemperature
        CCAPPLL = C2 * maxProdTemp ** 2 + C1 * maxProdTemp + C0
        CCAPPRL = D2 * maxProdTemp ** 2 + D1 * maxProdTemp + D0
        b = log(CCAPPRL / CCAPPLL) / log(PRL / PLL)
        a = CCAPPRL / PRL ** b
        # factor 0.75 to make double flash 25% more expansive than single flash
        Cplantcorrelation = (0.8 * a * pow(ElectricityProduced, b) * ElectricityProduced * 1000. / 1E6)

        # 1.02 to convert cost from 2012 to 2016 #factor 1.15 for 15% contingency and 1.12 for 12% indirect costs. factor 1.10 to convert from 2016 to 2022
        Cplant = 1.12 * 1.15 * ccplantadjfactor * Cplantcorrelation * 1.02 * 1.10

        return Cplant

    @staticmethod
    def Flash_double(T, Pow):

        MaxProducedTemperature = T
        ElectricityProduced = Pow

        if ElectricityProduced < 10.:
            C2 = 4.8472E-2
            C1 = -35.2186
            C0 = 8.4474E3
            D2 = 4.0604E-2
            D1 = -29.3817
            D0 = 6.9911E3
            PLL = 5.
            PRL = 10.
        elif ElectricityProduced < 25.:
            C2 = 4.0604E-2
            C1 = -29.3817
            C0 = 6.9911E3
            D2 = 3.2773E-2
            D1 = -23.5519
            D0 = 5.5263E3
            PLL = 10.
            PRL = 25.
        elif ElectricityProduced < 50.:
            C2 = 3.2773E-2
            C1 = -23.5519
            C0 = 5.5263E3
            D2 = 3.4716E-2
            D1 = -23.8139
            D0 = 5.1787E3
            PLL = 25.
            PRL = 50.
        elif ElectricityProduced < 75.:
            C2 = 3.4716E-2
            C1 = -23.8139
            C0 = 5.1787E3
            D2 = 3.5271E-2
            D1 = -24.3962
            D0 = 5.1972E3
            PLL = 50.
            PRL = 75.
        else:
            C2 = 3.5271E-2
            C1 = -24.3962
            C0 = 5.1972E3
            D2 = 3.3908E-2
            D1 = -23.4890
            D0 = 5.0238E3
            PLL = 75.
            PRL = 100.
        maxProdTemp = MaxProducedTemperature
        CCAPPLL = C2 * maxProdTemp ** 2 + C1 * maxProdTemp + C0
        CCAPPRL = D2 * maxProdTemp ** 2 + D1 * maxProdTemp + D0
        b = log(CCAPPRL / CCAPPLL) / log(PRL / PLL)
        a = CCAPPRL / PRL ** b

        Cplantcorrelation = (a * pow(ElectricityProduced, b) *ElectricityProduced * 1000. / 1E6)

        # 1.02 to convert cost from 2012 to 2016 #factor 1.15 for 15% contingency and 1.12 for 12% indirect costs. factor 1.10 to convert from 2016 to 2022
        Cplant = 1.12 * 1.15 * ccplantadjfactor * Cplantcorrelation * 1.02 * 1.10

        return Cplant


def Astolfi_():

    power = 10.21
    spec_cost = 1.046

    cost = spec_cost*power

    corr_currency = convert_EUR_to_USD(1, year=2014)

    yref = 2014

    corr_PPI = (calc_PPI("turbine", 2022)/calc_PPI("turbine", yref) + 2* calc_PPI("heat_exchanger", 2022)/calc_PPI("heat_exchanger", yref)) / 3

    cost *= corr_currency*corr_PPI

    return cost, cost/power

def cost_Astolfi():

    cost, spec = Astolfi_()

    return cost


def spec_Astolfi():
    cost, spec = Astolfi_()

    return spec



import matplotlib.pyplot as plt
from cycler import cycler

c = plt.get_cmap('tab20c').colors
plt.rcParams['axes.prop_cycle'] = cycler(color=c)


fia, ax = plt.subplots()
fib, bx = plt.subplots()

v2 = Geosphiresv2()
vX = GeophiresX()

ts = [150, 175, 200, 250]
ps = list(np.linspace(1, 100))

break_ps = []
break_Cs = []
break_specCs = []

ax.plot([1,100], [-1, -1], label="ORC", color=c[0])
ax.plot([1,100], [-1, -1], label="DSC", color=c[4])
ax.plot([1,100], [-10, -10], "o-", label="Break-even".format(150), color="red")
# ax.plot([10.21], [10.21*1.046*1.33*1.1], "*", label="Astolfi\\textsuperscript{a}", color=c[0])  # 1.33 conversion to USD, 1.1 increase in PPI (estimated)
ax.plot([10.21], [cost_Astolfi()], "*", label="Astolfi\\textsuperscript{a}", color=c[0])
ax.plot([1,100], [-1, -1], label="T={:.0f}".format(150), color=c[16])
ax.plot([1,100], [-1, -1], label="T={:.0f}".format(175), color=c[17])
ax.plot([1,100], [-1, -1], label="T={:.0f}".format(200), color=c[18])
ax.plot([1,100], [-1, -1], label="T={:.0f}".format(250), color=c[19])

bx.plot([1,100], [-1, -1], label="ORC", color=c[0])
bx.plot([1,100], [-1, -1], label="DSC", color=c[4])
bx.plot([1,100], [-1, -1], "o-", label="Break-even".format(150), color="red")
# bx.plot([10.21], [1.046*1.33*1.1], "*", label="Astolfi\\textsuperscript{a}", color=c[0])  # 1.33 conversion to USD, 1.1 increase in PPI (estimated)
bx.plot([10.21], [spec_Astolfi()], "*", label="Astolfi\\textsuperscript{a}", color=c[0])
bx.plot([1,100], [-1, -1], label="T={:.0f}".format(150), color=c[16])
bx.plot([1,100], [-1, -1], label="T={:.0f}".format(175), color=c[17])
bx.plot([1,100], [-1, -1], label="T={:.0f}".format(200), color=c[18])
bx.plot([1,100], [-1, -1], label="T={:.0f}".format(250), color=c[19])

for t in ts:
    vX_ORC_sub = np.array([vX.ORC_subcrit(t, p) for p in ps])
    vX_flash_sing = np.array([vX.Flash_single(t, p) for p in ps])

    diff = vX_ORC_sub-vX_flash_sing
    break_p = np.interp(0, diff, ps)
    break_C = np.interp(break_p, ps, vX_ORC_sub)

    break_ps.append(break_p)
    break_Cs.append(break_C)
    break_specCs.append(break_C/break_p)

for t in ts:
    vX_ORC_sub = [vX.ORC_subcrit(t, p) for p in ps]
    ax.plot(ps, vX_ORC_sub)

    vX_ORC_sub_spec = [vX.ORC_subcrit(t, p)/p for p in ps]
    bx.plot(ps, vX_ORC_sub_spec)

for t in ts:
    vX_flash_sing = [vX.Flash_single(t, p) for p in ps]
    ax.plot(ps, vX_flash_sing)

    vX_flash_sing_spec = [vX.Flash_single(t, p)/p for p in ps]
    bx.plot(ps, vX_flash_sing_spec)

ax.plot(break_ps, break_Cs, "o-", color="red")
bx.plot(break_ps, break_specCs, "o-", color="red")

ax.set_xlabel("Net power/\\unit{\\mega\\watt}")
ax.set_ylabel("Plant Cost/$2022")
ax.set_xscale("log")
ax.set_ylim(0, None)
ax.legend()

# bx.plot(break_ps, break_specCs, "o-", color="red")
bx.set_xlabel("Net power/\\unit{\\mega\\watt}")
bx.set_ylabel("Specific Plant Cost/\\unit{\\mega\\USD\\per\\mega\\watt}")
bx.set_xscale("log")
bx.set_ylim(0, None)
bx.legend()

tikzplotlib.save("PlantCost.tex", figure=fia)
tikzplotlib.save("PlantSpecCost.tex", figure=fib)


plt.show()




