import Simulator
from Simulator.cycle import Cycle
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

        self.flash_sep_HP = Simulator.separator()
        self.flash_sep_LP = Simulator.separator()

        self.ncg_sep = Simulator.separator()

        self.turbine_HP = Simulator.turbine(0.85, BaumannCorrection=True, cost_model="thermoflex")
        self.turbine_LP = Simulator.turbine(0.85, BaumannCorrection=True, cost_model="thermoflex")

        self.vap_mix = Simulator.mixer()

        self.condenser = Simulator.heat_exchanger(deltaT_pinch=self.deltaT_pinch_liq, cost_model="condenser-smith")

        self.coolingpump = Simulator.pump(0.6, cost_model="fan")

        self.brine_pump = Simulator.pump(0.75, cost_model="default")
        self.condensate_pump = Simulator.pump(0.75, cost_model="default")

        self.ncg_pump = Simulator.multistage_compression(0.7, 1, cost_model="default")

        self.geo_mix = Simulator.mixer()

    def __calc_flash_sep(self, flash1, flash2, gfluid):

        P_in = self.geofluid_in.properties.P * 1.0

        P_flash_HP = flash1 * P_in
        P_flash_LP = flash2 * P_in
        self.P_flash_HP = P_flash_HP
        self.P_flash_LP = P_flash_LP

        self.flash_sep_HP.set_inputs(gfluid, InputSpec="PH", Input1=P_flash_HP, Input2=gfluid.properties.H)
        brine, vapour_HP = self.flash_sep_HP.calc()

        self.flash_sep_LP.set_inputs(brine, InputSpec="PH", Input1=P_flash_LP, Input2=brine.properties.H)
        brine, vapour_MP = self.flash_sep_LP.calc()

        return brine, vapour_HP, vapour_MP

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
            T_min = self.T_ambient + self.deltaT_pinch_liq + 0.2

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

        vapour_HP = self.turbine_HP.inlet.copy()
        vapour_HP._update_quantity(vapour_HP.m * ratio)

        vapour_LP = self.turbine_LP.inlet.copy()
        vapour_LP._update_quantity(vapour_HP.m * ratio)

        m_vap_tot = vapour_HP.m + vapour_LP.m

        brine_HP = self.flash_sep_LP.inlet.copy()
        brine_HP._update_quantity(brine_HP.m * ratio)

        brine_MP = self.brine_pump.inlet.copy()
        brine_MP._update_quantity(brine_MP.m * ratio)

        ncg = self.ncg_pump.inlet.copy()
        ncg._update_quantity(ncg.m * ratio)

        condensate = self.condensate_pump.inlet.copy()
        condensate._update_quantity(condensate.m * ratio)

        self.geofluid_in._update_quantity(m)
        self.geofluid_out._update_quantity(m)

        self.coolant._update_quantity(m_vap_tot * self.condenser.MassRatio)
        self.coolant_in._update_quantity(m_vap_tot * self.condenser.MassRatio)
        self.coolant_out._update_quantity(m_vap_tot * self.condenser.MassRatio)

        self.flash_sep_HP.update_inlet_rate(m_vap_tot + brine_MP.m)
        self.flash_sep_LP.update_inlet_rate(brine_HP.m)
        self.ncg_sep.update_inlet_rate(m_vap_tot)

        self.turbine_LP.update_inlet_rate(vapour_LP.m)
        self.turbine_HP.update_inlet_rate(vapour_HP.m)

        self.condenser.update_inlet_rate(m_vap_tot, self.coolant.m)

        self.coolingpump.update_inlet_rate(self.coolant.m)
        self.brine_pump.update_inlet_rate(brine_MP.m)
        self.condensate_pump.update_inlet_rate(condensate.m)
        self.ncg_pump.update_inlet_rate(ncg.m)

        self.geo_mix.update_inlet_rate([brine_MP.m, condensate.m, ncg.m])

        self.__calc_performance()
        self.__calc_cost()

        self.calc_economics()

    def __calc_mass_rates(self, vapour_HP_in, vapour_MP_in, brine_MP, ncg, condensate):

        vapour_HP_in._update_quantity(self.geofluid.m*vapour_HP_in.m)
        vapour_MP_in._update_quantity(self.geofluid.m*vapour_MP_in.m)
        brine_MP._update_quantity(self.geofluid.m*brine_MP.m)
        ncg._update_quantity(self.geofluid.m * ncg.m)
        condensate._update_quantity(self.geofluid.m * condensate.m)

        self.geofluid_in._update_quantity(self.geofluid.m)
        self.geofluid_out._update_quantity(self.geofluid.m*self.geofluid_out.m)

        self.coolant._update_quantity((vapour_HP_in.m + vapour_MP_in.m) * self.condenser.MassRatio)
        self.coolant_in._update_quantity((vapour_HP_in.m + vapour_MP_in.m) * self.condenser.MassRatio)
        self.coolant_out._update_quantity((vapour_HP_in.m + vapour_MP_in.m) * self.condenser.MassRatio)

        self.flash_sep_HP.update_inlet_rate((vapour_HP_in.m + vapour_MP_in.m) + brine_MP.m)

        self.ncg_sep.update_inlet_rate((vapour_HP_in.m + vapour_MP_in.m))

        self.turbine_HP.update_inlet_rate(vapour_HP_in.m)
        self.turbine_LP.update_inlet_rate((vapour_HP_in.m + vapour_MP_in.m))

        self.condenser.update_inlet_rate((vapour_HP_in.m + vapour_MP_in.m), self.coolant.m)

        self.coolingpump.update_inlet_rate(self.coolant.m)
        self.brine_pump.update_inlet_rate(brine_MP.m)
        self.condensate_pump.update_inlet_rate(condensate.m)
        self.ncg_pump.update_inlet_rate(ncg.m)

        self.geo_mix.update_inlet_rate([brine_MP.m, condensate.m, ncg.m])

    def __calc_performance(self):

        self.cycle_power = self.turbine_LP.work + self.turbine_HP.work
        self.parasitic_power = self.brine_pump.work + self.condensate_pump.work + self.ncg_pump.work + self.coolingpump.work
        self.net_power = self.cycle_power + self.parasitic_power

        self.cycle_power_elec = self.turbine_LP.power_elec + self.turbine_HP.power_elec
        self.parasitic_power_elec = self.brine_pump.power_elec + self.condensate_pump.power_elec + self.ncg_pump.power_elec + self.coolingpump.power_elec
        self.net_power_elec = self.cycle_power_elec + self.parasitic_power_elec

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
        self.flash_sep_HP.calc_exergy_balance()
        self.flash_sep_LP.calc_exergy_balance()
        self.ncg_sep.calc_exergy_balance()
        self.turbine_HP.calc_exergy_balance()
        self.turbine_LP.calc_exergy_balance()
        self.condenser.calc_exergy_balance()
        self.brine_pump.calc_exergy_balance()
        self.condensate_pump.calc_exergy_balance()
        self.ncg_pump.calc_exergy_balance()
        self.geo_mix.calc_exergy_balance()

        self.Eloss = self.flash_sep_HP.Eloss + self.flash_sep_LP.Eloss\
                     + self.ncg_sep.Eloss + self.condenser.Eloss\
                     + self.turbine_HP.Eloss + self.turbine_LP.Eloss \
                     + self.brine_pump.Eloss + self.condensate_pump.Eloss\
                     + self.ncg_pump.Eloss + self.geo_mix.Eloss

        # this is to QC the results
        self.energy_balance = self.Q_in - self.Q_out + self.cycle_power  # this should be zero, though not necessarily in the case of direct cycles
        self.exergy_balance = self.Ein - self.Eout - self.Eloss - abs(self.cycle_power)  # this should be zero

        E_reinjected = self.geofluid.m * (self.geofluid_out.properties.H - Tref * self.geofluid_out.properties.S)
        E_rejected = self.coolant.m * (self.coolant_out.properties.H - Tref * self.coolant_out.properties.S)

        self.exergy_losses = [{"equip": "Reinjected", "val": E_reinjected},
                              {"equip": "Rejected", "val": E_rejected},
                              {"equip": "FlashSepHP", "val": self.flash_sep_HP.Eloss},
                              {"equip": "FlashSepLP", "val": self.flash_sep_LP.Eloss},
                              {"equip": "NCGSep", "val": self.ncg_sep.Eloss},
                              {"equip": "TurbineHP", "val": self.turbine_HP.Eloss},
                              {"equip": "TurbineLP", "val": self.turbine_LP.Eloss},
                              {"equip": "Condenser", "val": self.condenser.Eloss},
                              {"equip": "BrinePump", "val": self.brine_pump.Eloss},
                              {"equip": "CondensatePump", "val": self.condensate_pump.Eloss},
                              {"equip": "NCGComp", "val": self.ncg_pump.Eloss},
                              {"equip": "Mixer", "val": self.geo_mix.Eloss},
                              ]

        self.eta_I_cycle = -self.net_power / self.Q_in
        self.eta_I_recov = self.Q_in / self.Q_in_max
        self.eta_I_plant = self.eta_I_cycle * self.eta_I_recov

        self.eta_II_BF = -self.net_power / self.Ein
        self.eta_II_FUNC = -self.net_power / (self.Ein - self.Eout)

    def __calc_cost(self):

        cost = 0

        cost += self.flash_sep_HP.calc_cost()
        cost += self.flash_sep_LP.calc_cost()
        cost += self.ncg_sep.calc_cost()
        cost += self.turbine_HP.calc_cost()
        cost += self.turbine_LP.calc_cost()
        cost += self.condenser.calc_cost()
        cost += self.coolingpump.calc_cost()
        cost += self.brine_pump.calc_cost()
        cost += self.condensate_pump.calc_cost()
        cost += self.ncg_pump.calc_cost()
        cost += self.geo_mix.calc_cost()

        self.primary_equipment_cost = cost * 1e-6
        self.secondary_equipment_cost = 1.4 * cost * 1e-6  # control system, piping, etc.
        self.construction_cost = 0.7 * cost * 1e-6  # construction & materials

        self.cost = self.primary_equipment_cost + self.secondary_equipment_cost + self.construction_cost
        self.specific_cost = 1e3 * self.cost / abs(self.net_power * 1e-6)  # $€/kW

        self.costs = [{"equip": "FlashSepHP", "val": self.flash_sep_HP.cost},
                      {"equip": "FlashSepLP", "val": self.flash_sep_LP.cost},
                      {"equip": "NCGSep", "val": self.ncg_sep.cost},
                      {"equip": "TurbineHP", "val": self.turbine_HP.cost},
                      {"equip": "TurbineLP", "val": self.turbine_LP.cost},
                      {"equip": "Condenser", "val": self.condenser.cost},
                      {"equip": "BrinePump", "val": self.brine_pump.cost},
                      {"equip": "CondensatePump", "val": self.condensate_pump.cost},
                      {"equip": "NCGComp", "val": self.ncg_pump.cost},
                      {"equip": "Mixer", "val": self.geo_mix.cost},
                      {"equip": "CoolingPump", "val": self.coolingpump.cost}
                      ]

    def calc(self, flash1, flash2, P_min, *args):

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

        brine_MP, vapour_HP_in, vapour_MP_in = self.__calc_flash_sep(flash1, flash2, gfluid)

        P_turb_HP_out = self.geofluid_in.properties.P * flash2
        self.turbine_HP.set_inputs(vapour_HP_in, P_turb_HP_out)
        vap_turb_out = self.turbine_HP.calc()

        self.vap_mix.set_inputs(vap_turb_out, vapour_MP_in)
        vapour_MP_turb_in = self.vap_mix.calc()

        P_turb_LP_out = P_min + self.condenser.deltaP_hot
        self.turbine_LP.set_inputs(vapour_MP_turb_in, P_turb_LP_out)
        vap_turb_out = self.turbine_LP.calc()

        vap_cond_out = self.__calc_condenser(vap_turb_out)

        self.ncg_sep.set_inputs(vap_cond_out)
        condensate, ncg = self.ncg_sep.calc()

        # repressurisation
        self.brine_pump.set_inputs(brine_MP, self.geofluid_in.properties.P)
        brine_out = self.brine_pump.calc()

        self.condensate_pump.set_inputs(condensate, self.geofluid_in.properties.P)
        condensate_out = self.condensate_pump.calc()

        self.ncg_pump.set_inputs(ncg, self.geofluid_in.properties.P, findN=True)
        ncg_out = self.ncg_pump.calc()

        self.geo_mix.set_inputs(brine_out, condensate_out, ncg_out)
        self.geofluid_out = self.geo_mix.calc()

        self.__calc_mass_rates(vapour_HP_in, vapour_MP_in, brine_MP, ncg, condensate)

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

if __name__ == "__main__":

    from FluidProperties.fluid import Fluid
    from Simulator.streams import MaterialStream
    from time import perf_counter

    Cycle = DirectCycle()
    Cycle.condenser.deltaP_cold = 120
    Cycle.coolingpump.eta_isentropic = 0.6

    hot_fluid = Fluid(["water", 1])
    hot_fluid_stream = MaterialStream(hot_fluid, m=50)
    hot_fluid_stream.update("TQ", 200+273, 0.05)

    Cycle.set_geofluid(hot_fluid_stream)

    cold_fluid = Fluid(["air", 1])
    cold_fluid_stream = MaterialStream(cold_fluid, m= 1)
    Cycle.set_coolant(cold_fluid_stream)

    flash1 = 0.66
    flash2 = 0.33
    Pcond = 0.1e5


    START=perf_counter()
    Cycle.calc(flash1, flash2, Pcond)
    END = perf_counter()

    print(END - START)

    print()
