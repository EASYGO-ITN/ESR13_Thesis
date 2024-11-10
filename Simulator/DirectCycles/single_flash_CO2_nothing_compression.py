from ..cycle import Cycle
import Simulator
from Simulator import Tref
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

        self.turbine = Simulator.turbine(0.85, BaumannCorrection=True, cost_model="thermoflex")

        self.condenser = Simulator.heat_exchanger(deltaT_pinch=self.deltaT_pinch_liq, cost_model="condenser-smith")

        self.coolingpump = Simulator.pump(0.85, cost_model="fan")

        self.brine_pump = Simulator.pump(0.85, cost_model="default")
        self.condensate_pump = Simulator.pump(0.85, cost_model="default")

        self.geo_mix = Simulator.mixer()

    def __calc_flash_sep(self, flash, gfluid):

        P_in = self.geofluid_in.properties.P * 1.0

        P_flash = flash * P_in
        self.P_flash = P_flash

        self.flash_sep.set_inputs(gfluid, InputSpec="PH", Input1=P_flash, Input2=gfluid.properties.H)
        brine, vapour = self.flash_sep.calc()

        return brine, vapour

    def __calc_condenser(self, vap_turb_out):

        # switch the geofluid to the interpolation fluid
        if self.interpolation:
            vap_cond_in = self.geofluid_table.copy()
            vap_cond_in.fluid.update_composition(vap_turb_out.fluid.composition)
            vap_cond_in._update_quantity(vap_turb_out.m)
            vap_cond_in.update("PH", vap_turb_out.properties.P, vap_turb_out.properties.H)
        else:
            vap_cond_in = vap_turb_out.copy()

        # calculate the condensation temperature
        try:
            temp_vap = vap_cond_in.copy()
            temp_vap.update("PQ", self.Pmin, 0)
            T_min = temp_vap.properties.T - self.deltaT_subcool

            if T_min < self.T_ambient + self.deltaT_pinch_liq:
                T_min = self.T_ambient + self.deltaT_pinch_liq
        except:
            T_min = self.T_ambient + self.deltaT_pinch_liq + 1

        self.Tmin = T_min

        vap_cond_out = vap_cond_in.copy()
        vap_cond_out.update("PT", self.Pmin, T_min)

        # calculate the condenser
        P_cool_in = self.coolant.properties.P + self.condenser.deltaP_cold
        self.coolingpump.set_inputs(self.coolant, P_cool_in)
        self.coolant_in = self.coolingpump.calc()

        self.condenser.set_inputs(MassRatio=-1, Inlet_hot=vap_cond_in, Inlet_cold=self.coolant_in,
                                  Outlet_hot=vap_cond_out)
        vap_cond_out, self.coolant_out = self.condenser.calc()

        if self.interpolation:
            temp_vapour_out = vap_turb_out.copy()
            temp_vapour_out.update("PH", vap_cond_out.properties.P, vap_cond_out.properties.H)
        else:
            temp_vapour_out = vap_cond_out.copy()
        vap_cond_out = temp_vapour_out

        return vap_cond_out

    def update_mass_rate(self, m):

        ratio = m / self.geofluid.m

        self.geofluid._update_quantity(m)

        vapour = self.ncg_sep.inlet.copy()
        vapour._update_quantity(vapour.m * ratio)

        brine = self.brine_pump.inlet.copy()
        brine._update_quantity(brine.m * ratio)

        condensate = self.condensate_pump.inlet.copy()
        condensate._update_quantity(condensate.m * ratio)

        self.geofluid_in._update_quantity(m)
        self.geofluid_out._update_quantity(m)

        self.coolant._update_quantity(vapour.m * self.condenser.MassRatio)
        self.coolant_in._update_quantity(vapour.m * self.condenser.MassRatio)
        self.coolant_out._update_quantity(vapour.m * self.condenser.MassRatio)

        self.flash_sep.update_inlet_rate(vapour.m + brine.m)
        self.ncg_sep.update_inlet_rate(vapour.m)

        self.turbine.update_inlet_rate(vapour.m)

        self.condenser.update_inlet_rate(vapour.m, self.coolant.m)

        self.coolingpump.update_inlet_rate(self.coolant.m)
        self.brine_pump.update_inlet_rate(brine.m)
        self.condensate_pump.update_inlet_rate(condensate.m)

        self.geo_mix.update_inlet_rate([brine.m, condensate.m])

        self.__calc_performance()
        self.__calc_cost()

        self.calc_economics()


    def __calc_mass_rates(self, vapour, brine, ncg, condensate):

        vapour._update_quantity(self.geofluid.m*vapour.m)
        brine._update_quantity(self.geofluid.m*brine.m)
        ncg._update_quantity(self.geofluid.m * ncg.m)
        condensate._update_quantity(self.geofluid.m * condensate.m)

        self.geofluid_in._update_quantity(self.geofluid.m)
        self.geofluid_out._update_quantity(self.geofluid.m*self.geofluid_out.m)

        self.coolant._update_quantity(vapour.m * self.condenser.MassRatio)
        self.coolant_in._update_quantity(vapour.m * self.condenser.MassRatio)
        self.coolant_out._update_quantity(vapour.m * self.condenser.MassRatio)

        self.flash_sep.update_inlet_rate(vapour.m + brine.m)
        self.ncg_sep.update_inlet_rate(vapour.m)

        self.turbine.update_inlet_rate(vapour.m)

        self.condenser.update_inlet_rate(vapour.m, self.coolant.m)

        self.coolingpump.update_inlet_rate(self.coolant.m)
        self.brine_pump.update_inlet_rate(brine.m)
        self.condensate_pump.update_inlet_rate(condensate.m)

        self.geo_mix.update_inlet_rate([brine.m, condensate.m])

    def __calc_performance(self):

        self.cycle_power = self.turbine.work
        self.parasitic_power = self.brine_pump.work + self.condensate_pump.work + self.coolingpump.work
        self.net_power = self.cycle_power + self.parasitic_power

        # calculate the heat flow into and out of the plant
        self.Q_in = self.geofluid.m * (self.geofluid_in.properties.H - self.geofluid_out.properties.H)
        self.Q_in_max = self.geofluid.m * self.geofluid_in.properties.H
        self.Q_out = self.coolant.m * (self.coolant_out.properties.H - self.coolant_in.properties.H)

        # calculate the exergy flow into and out of the plant
        self.Ein = self.geofluid.m * (self.geofluid_in.properties.H - Tref * self.geofluid_in.properties.S)
        self.Ein += self.coolant.m * (self.coolant_in.properties.H - Tref * self.coolant_in.properties.S)
        self.Eout = self.geofluid.m * (self.geofluid_out.properties.H - Tref * self.geofluid_out.properties.S)
        self.Eout += self.coolant.m * (self.coolant_out.properties.H - Tref * self.coolant_out.properties.S)

        # perform exergy balance on all components
        self.flash_sep.calc_exergy_balance()
        self.ncg_sep.calc_exergy_balance()
        self.turbine.calc_exergy_balance()
        self.condenser.calc_exergy_balance()
        self.brine_pump.calc_exergy_balance()
        self.condensate_pump.calc_exergy_balance()
        self.geo_mix.calc_exergy_balance()

        self.Eloss = self.flash_sep.Eloss + self.ncg_sep.Eloss \
                     + self.turbine.Eloss + self.condenser.Eloss \
                     + self.brine_pump.Eloss + self.condensate_pump.Eloss\
                     + self.geo_mix.Eloss

        # this is to QC the results
        self.energy_balance = self.Q_in - self.Q_out + self.cycle_power  # this should be zero, though not necessarily in the case of direct cycles
        self.exergy_balance = self.Ein - self.Eout - self.Eloss - abs(self.cycle_power)  # this should be zero

        E_reinjected = self.geofluid.m * (self.geofluid_out.properties.H - Tref * self.geofluid_out.properties.S)
        E_rejected = self.coolant.m * (self.coolant_out.properties.H - Tref * self.coolant_out.properties.S)
        # E_vented = self.ncg_out.m*(self.ncg_out.properties.H - Tref*self.ncg_out.properties.S)

        self.exergy_losses = [{"equip": "Reinjected", "val": E_reinjected},
                              {"equip": "Rejected", "val": E_rejected},
                              # {"equip": "Vented", "val": E_vented},
                              {"equip": "FlashSep", "val": self.flash_sep.Eloss},
                              {"equip": "NCGSep", "val": self.ncg_sep.Eloss},
                              {"equip": "Turbine", "val": self.turbine.Eloss},
                              {"equip": "Condenser", "val": self.condenser.Eloss},
                              {"equip": "BrinePump", "val": self.brine_pump.Eloss},
                              {"equip": "CondensatePump", "val": self.condensate_pump.Eloss},
                              {"equip": "Mixer", "val": self.geo_mix.Eloss},
                              ]
        self.eta_I_cycle = -self.net_power / self.Q_in
        self.eta_I_recov = self.Q_in / self.Q_in_max
        self.eta_I_plant = self.eta_I_cycle * self.eta_I_recov

        self.eta_II_BF = -self.net_power / self.Ein
        self.eta_II_FUNC = -self.net_power / (self.Ein - self.Eout)

    def __calc_cost(self):

        cost = 0

        cost += self.flash_sep.calc_cost()
        cost += self.ncg_sep.calc_cost()
        cost += self.turbine.calc_cost()
        cost += self.condenser.calc_cost()
        cost += self.coolingpump.calc_cost()
        cost += self.brine_pump.calc_cost()
        cost += self.condensate_pump.calc_cost()
        cost += self.geo_mix.calc_cost()

        self.primary_equipment_cost = cost * 1e-6
        self.secondary_equipment_cost = 1.4 * cost * 1e-6  # control system, piping, etc.
        self.construction_cost = 0.7 * cost * 1e-6  # construction & materials

        self.cost = self.primary_equipment_cost + self.secondary_equipment_cost + self.construction_cost
        self.specific_cost = 1e3 * self.cost / abs(self.net_power * 1e-6)  # $€/kW

        self.costs = [{"equip": "FlashSep", "val": self.flash_sep.cost},
                      {"equip": "NCGSep", "val": self.ncg_sep.cost},
                      {"equip": "Turbine", "val": self.turbine.cost},
                      {"equip": "Condenser", "val": self.condenser.cost},
                      {"equip": "BrinePump", "val": self.brine_pump.cost},
                      {"equip": "CondensatePump", "val": self.condensate_pump.cost},
                      {"equip": "Mixer", "val": self.geo_mix.cost},
                      {"equip": "CoolingPump", "val": self.coolingpump.cost}
                      ]

    def calc(self, flash, P_min, *args):

        self.Pmin = P_min

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

        brine_in, vapour_in = self.__calc_flash_sep(flash, gfluid)

        P_turb_out = P_min + self.condenser.deltaP_hot
        self.turbine.set_inputs(vapour_in, P_turb_out)
        vap_turb_out = self.turbine.calc()

        vap_cond_out = self.__calc_condenser(vap_turb_out)

        self.ncg_sep.set_inputs(vap_cond_out)
        condensate, ncg = self.ncg_sep.calc()

        # repressurisation
        self.brine_pump.set_inputs(brine_in, self.geofluid_in.properties.P)
        brine_out = self.brine_pump.calc()

        self.condensate_pump.set_inputs(condensate, self.geofluid_in.properties.P)
        condensate_out = self.condensate_pump.calc()

        self.geo_mix.set_inputs(brine_out, condensate_out)
        self.geofluid_out = self.geo_mix.calc()

        self.__calc_mass_rates(vapour_in, brine_in, ncg, condensate)

        self.__calc_performance()

        self.__calc_cost()

        self.calc_economics()

        return self.net_power * 1.0

    def plot_TS(self):

        # the geofluid separation
        h_tot = self.geofluid_in.properties.H
        h_liq = self.flash_sep.outlet[0].properties.H
        h_vap = self.flash_sep.outlet[1].properties.H
        x = (h_tot - h_liq) / (h_vap - h_liq)

        s_liq = self.flash_sep.outlet[0].properties.S
        s_vap = self.flash_sep.outlet[1].properties.S
        s_tot = (1 - x) * s_liq + x * s_vap

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

        plt.title("NetPower: {:.2f} kW/(kg/s)".format(-self.net_power / 1000))

        plt.show()


    def plot_Eloss(self):

        def sortFunc(e):
            return e["val"]

        self.exergy_losses.sort(key=sortFunc, reverse=True)

        labels = [x["equip"] for x in self.exergy_losses]
        values = [x["val"] for x in self.exergy_losses]

        fig, ax = plt.subplots()
        ax.pie(values, labels=labels, autopct='%1.1f%%')
        plt.show()

    def plot_costs(self):

        def sortFunc(e):
            return e["val"]

        self.costs.sort(key=sortFunc, reverse=True)

        labels = [x["equip"] for x in self.costs]
        values = [x["val"] for x in self.costs]

        fig, ax = plt.subplots()
        ax.pie(values, labels=labels, autopct='%1.1f%%')
        plt.show()
