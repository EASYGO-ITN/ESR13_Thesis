from ..cycle import Cycle
import Simulator
from Simulator.streams import MaterialStream
from FluidProperties.fluid import Fluid
import matplotlib.pyplot as plt
from scipy.optimize import root_scalar

"""

      *--------------> Turb ----*
      |                         |
      |             *---------- Recup <---- Pump <----*
      |             |               |                 |
----> Evap ----> PreH ---->         *----> Cond ------*
         |       |
         *-------*

"""


class DirectCycle(Cycle):

    def __init__(self):

        super().__init__()

        self.flash_sep = Simulator.separator()
        self.ncg_sep = Simulator.separator()

        self.turbine = Simulator.turbine(0.85, BaumannCorrection=True)

        self.condenser = Simulator.heat_exchanger(deltaT_pinch=self.deltaT_pinch_liq)

        self.coolingpump = Simulator.pump(0.85)

        self.brine_pump = Simulator.pump(0.85)
        self.condensate_pump = Simulator.pump(0.85)

        self.ncg_pump = Simulator.multistage_compression(0.85, 1)
        self.ncg_pressure = 101325

        self.geo_mix = Simulator.mixer()

    def calc(self, flash, P_min, P_flash=None):

        self.geofluid_in = self.geofluid.copy()
        self.coolant_in = self.coolant.copy()

        # (re)initialise the stream mass rates
        gfluid = self.geofluid.copy()
        gfluid._update_quantity(1.0)
        if self.interpolation:
            gfluid_table = self.geofluid_table.copy()
            gfluid_table._update_quantity(1.0)
        cfluid = self.coolant.copy()
        cfluid._update_quantity(1.0)

        P_in = self.geofluid_in.properties.P * 1.0
        if P_flash is None:
            P_flash = flash * P_in

        self.flash_sep.set_inputs(gfluid, InputSpec="PH", Input1=P_flash, Input2=gfluid.properties.H)
        brine, vapour = self.flash_sep.calc()

        self.brine_pump.set_inputs(brine, self.geofluid_in.properties.P)
        brine_out = self.brine_pump.calc()

        P_turb_out = P_min + self.condenser.deltaP_hot
        self.turbine.set_inputs(vapour, P_turb_out)
        vapour_lowP = self.turbine.calc()

        # switch the geofluid to the interpolation fluid
        if self.interpolation:
            temp_vapour = self.geofluid_table.copy()
            temp_vapour.fluid.update_composition(vapour_lowP.fluid.composition)
            temp_vapour._update_quantity(vapour_lowP.m)
            temp_vapour.update("PH", vapour_lowP.properties.P, vapour_lowP.properties.H)
        else:
            temp_vapour = vapour_lowP.copy()

        try:
            temp_vap = vapour.copy()
            temp_vap.update("PQ", P_min, 0)
            T_min = temp_vap.properties.T - self.deltaT_subcool

            if T_min < self.T_ambient + self.deltaT_pinch_liq:
                T_min = self.T_ambient + self.deltaT_pinch_liq
        except:
            T_min = self.T_ambient + self.deltaT_pinch_liq + 0.1

        temp_vapour_out = temp_vapour.copy()
        temp_vapour_out.update("PT", P_min, T_min)

        # calculate the condenser
        P_cool_in = self.coolant.properties.P + self.condenser.deltaP_cold
        self.coolingpump.set_inputs(self.coolant, P_cool_in)
        self.coolant_in = self.coolingpump.calc()

        self.condenser.set_inputs(MassRatio=-1, Inlet_hot=temp_vapour, Inlet_cold=self.coolant_in, Outlet_hot=temp_vapour_out)
        vapour_lowP, self.coolant_out = self.condenser.calc()

        if self.interpolation:
            temp_vapour_out = vapour.copy()
            temp_vapour_out.update("PH", vapour_lowP.properties.P, vapour_lowP.properties.H)
        else:
            temp_vapour_out = vapour_lowP.copy()

        vapour_lowP = temp_vapour_out

        self.ncg_sep.set_inputs(vapour_lowP)
        condensate, ncg = self.ncg_sep.calc()

        self.condensate_pump.set_inputs(condensate, self.geofluid_in.properties.P)
        condensate_out = self.condensate_pump.calc()

        # if ncg.fluid.engine == "geoprop":
        #     if "carbondioxide" in ncg.fluid.components:
        #         molefrac_CO2 = ncg.fluid.composition[ncg.fluid.components.index("carbondioxide")]
        #         if molefrac_CO2 > 0.999:
        #             CO2 = MaterialStream(Fluid(["carbondioxide", 1]), m=ncg.m)
        #             CO2.update("PT", ncg.properties.P, ncg.properties.T)
        #             ncg = CO2

        self.ncg_pump.set_inputs(ncg, self.ncg_pressure, findN=True)
        ncg_out = self.ncg_pump.calc()

        self.geo_mix.set_inputs(brine_out, condensate_out, ncg_out)
        self.geofluid_out = self.geo_mix.calc()

        self.coolant._update_quantity(vapour_lowP.m * self.condenser.MassRatio)
        self.coolant_in._update_quantity(vapour_lowP.m * self.condenser.MassRatio)
        self.coolant_out._update_quantity(vapour_lowP.m * self.condenser.MassRatio)

        self.cycle_power = self.turbine.work
        self.parasitic_power = self.brine_pump.work + self.condensate_pump.work + self.ncg_pump.work + self.coolant.m*self.coolingpump.work
        self.net_power = self.cycle_power + self.parasitic_power

        return self.net_power * 1.0

    def plot_TS(self):

        # the geofluid separation
        h_tot = self.geofluid_in.properties.H
        h_liq = self.flash_sep.outlet[0].properties.H
        h_vap = self.flash_sep.outlet[1].properties.H
        x = (h_tot - h_liq) / (h_vap - h_liq)

        s_liq = self.flash_sep.outlet[0].properties.S
        s_vap = self.flash_sep.outlet[1].properties.S
        s_tot = (1-x)*s_liq + x* s_vap

        s = [self.geofluid_in.properties.S, s_tot]
        T = [self.geofluid_in.properties.T, self.flash_sep.outlet[1].properties.T]
        plt.plot(s, T, label="flash_sep")

        s = [s_tot, s_liq]
        T = [self.flash_sep.inlet.properties.T, self.flash_sep.outlet[1].properties.T]
        plt.plot(s, T, label="brine")

        s = [s_tot, s_vap]
        T = [self.flash_sep.inlet.properties.T, self.flash_sep.outlet[1].properties.T]
        plt.plot(s, T, label="vapour")

        # the brine repressurisation
        s = [self.brine_pump.inlet.properties.S, self.brine_pump.outlet.properties.S]
        T = [self.brine_pump.inlet.properties.T, self.brine_pump.outlet.properties.T]
        plt.plot(s, T, label="brine pump")

        # the vapour expansion
        s = [self.turbine.inlet.properties.S, self.turbine.outlet.properties.S]
        T = [self.turbine.inlet.properties.T, self.turbine.outlet.properties.T]
        plt.plot(s, T, label="turbine")

        s = self.condenser.S_profile[0]
        T = self.condenser.T_profile[0]
        plt.plot(s, T, label="condenser")

        # the ncg separator
        s_cond = self.ncg_sep.outlet[0].properties.S
        s_ncg = self.ncg_sep.outlet[1].properties.S
        s_tot = self.condenser.outlet[0].properties.S

        s = [s_tot, s_cond]
        T = [self.condenser.outlet[0].properties.T, self.ncg_sep.outlet[0].properties.T]
        plt.plot(s, T, label="condensate")

        s = [s_tot, s_ncg]
        T = [self.condenser.outlet[0].properties.T, self.ncg_sep.outlet[1].properties.T]
        plt.plot(s, T, label="ncg")




        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        plt.legend(by_label.values(), by_label.keys(), loc=0)

        plt.xlabel("Specific Entropy, J/kg/K")
        plt.ylabel("Temperature, K")

        plt.title("NetPower: {:.2f} kW/(kg/s)".format(-self.net_power/1000))

        plt.show()