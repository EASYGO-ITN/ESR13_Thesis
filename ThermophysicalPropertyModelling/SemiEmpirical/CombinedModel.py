import CoolProp as cp
from CoolProp.CoolProp import PropsSI
import math
import numpy as np
import thermofun as tf
from SP2009 import SpycherPruss2009


Pref = 101325
Tref = 298

# set the new reference conditions
wat_rho = PropsSI("Dmolar",  "P", Pref, "T", Tref, "Water")
co2_rho = PropsSI("Dmolar", "P", Pref, "T", Tref, "CO2")

cp.CoolProp.set_reference_state('Water', Tref, wat_rho, 0, 0)
cp.CoolProp.set_reference_state('CO2', Tref, co2_rho, 0, 0)


class Model:

    def __init__(self):
        # instantiate the relevant models
        self.sp = SpycherPruss2009()

        self.water = cp.AbstractState("?", "water")
        self.aux_water = cp.AbstractState("?", "water")
        self.carbondioxide = cp.AbstractState("?", "CO2")
        self.aux_carbondioxide = cp.AbstractState("?", "CO2")

        self.engine = tf.ThermoEngine("C:/Users/trist/PycharmProjects/Thesis/ThermophysicalPropertyModelling/SemiEmpirical/CO2aq_database.json")

        props = self.engine.thermoPropertiesSubstance(Tref, Pref, "CO2@")
        self.co3_h0 = props.enthalpy.val
        self.co3_s0 = props.entropy.val

    def calc_activity_vap(self, t, p, yH2O, yCO2):
        fug_CO2_0 = self.sp.fugacity_coefficients(t, p, 1, 0)[0]
        fug_H2O_0 = self.sp.fugacity_coefficients(t, p, 0, 1)[1]
        fug_CO2, fug_H2O = self.sp.fugacity_coefficients(t, p, yCO2, yH2O)

        activity_CO2 = 8.314 * t * math.log(fug_CO2 / fug_CO2_0)
        activity_H2O = 8.314 * t * math.log(fug_H2O / fug_H2O_0)

        return activity_H2O, activity_CO2

    def calc_dadP_vap(self, t, p, yH2O, yCO2):
        delta = 1e-8

        activity_est = self.calc_activity_vap(t, p * (1 + delta), yH2O, yCO2)
        activity = self.calc_activity_vap(t, p, yH2O, yCO2)

        dadP_H2O = (activity_est[0] - activity[0]) / (delta * p)
        dadP_CO2 = (activity_est[1] - activity[1]) / (delta * p)

        return dadP_H2O, dadP_CO2

    def calc_dadT_vap(self, t, p, yH2O, yCO2):
        delta = 1e-8

        activity_est = self.calc_activity_vap(t * (1 + delta), p, yH2O, yCO2)
        activity = self.calc_activity_vap(t, p, yH2O, yCO2)

        dadT_H2O = -(activity_est[0] - activity[0]) / (delta * t)
        dadT_CO2 = -(activity_est[1] - activity[1]) / (delta * t)

        return dadT_H2O, dadT_CO2

    def calc_dadTinv_vap(self, t, p, yH2O, yCO2):
        delta = 1e-8

        activity_est = self.calc_activity_vap(t * (1 + delta), p, yH2O, yCO2)
        activity = self.calc_activity_vap(t, p, yH2O, yCO2)

        dadTinv_H2O = (activity_est[0] / (t * (1 + delta)) - activity[0] / t) / (1 / (t * (1 + delta)) - 1 / t)
        dadTinv_CO2 = (activity_est[1] / (t * (1 + delta)) - activity[1] / t) / (1 / (t * (1 + delta)) - 1 / t)

        return dadTinv_H2O, dadTinv_CO2

    def _extrapolation(self, t, p, tsat):

        # we need to extrapolate the vapour properties to T
        dHdT = self.aux_water.first_partial_deriv(cp.iHmolar, cp.iT, cp.iP)
        dSdT = self.aux_water.first_partial_deriv(cp.iSmolar, cp.iT, cp.iP)

        def calc_dVdT(tau):
            rho = self.aux_water.rhomolar()
            self.aux_water.update(cp.PT_INPUTS, p, tau * (1 + 1e-6))
            rho_ = self.aux_water.rhomolar()

            self.aux_water.update(cp.PT_INPUTS, p, tau * (1 + 2 * 1e-6))
            _rho_ = self.aux_water.rhomolar()

            _dVdT_ = (1 / _rho_ - 1 / rho_) / (tau * 1e-6)
            dVdT_ = (1 / rho_ - 1 / rho) / (tau * 1e-6)

            dV1dT1 = (_dVdT_ + dVdT_) / 2
            d2VdT2 = (_dVdT_ - dVdT_) / (tau * 1e-6)

            return dV1dT1, d2VdT2

        dVdT, dVdTdT = calc_dVdT(tsat)

        Hw0 = self.aux_water.hmolar() - (tsat - t) * dHdT
        Sw0 = self.aux_water.smolar() - (tsat - t) * dSdT
        Gw0 = Hw0 - t * Sw0

        a = dVdT * tsat * self.aux_water.rhomolar()
        Vw0 = 1 / self.aux_water.rhomolar() * (t / tsat) ** a  # I am still not 100% on the best way to exrapolate...

        return Gw0, Hw0, Sw0, Vw0

    def calc_vap_phase(self, p, t, yH2O, yCO2):
        self.water.update(cp.PT_INPUTS, p, t)
        Hw0 = self.water.hmolar()
        Sw0 = self.water.smolar()
        Gw0 = self.water.gibbsmolar()
        Vw0 = 1 / self.water.rhomolar()

        dadTinvw, dadTinvc = self.calc_dadTinv_vap(t, p, yH2O, yCO2)
        dadTw, dadTc = self.calc_dadT_vap(t, p, yH2O, yCO2)
        dadPw, dadPc = self.calc_dadP_vap(t, p, yH2O, yCO2)

        Tsat = 0
        if p < self.aux_water.p_critical():
            self.aux_water.update(cp.PQ_INPUTS, p, 1)
            Tsat = self.aux_water.T()
        # else:
        #     self.aux_water.update(cp.PT_INPUTS, p, self.aux_water.T_critical())
        #     Tsat = self.aux_water.T_critical()

        if t < Tsat:

            Vsat = 1/ self.aux_water.rhomolar()
            Hsat = self.aux_water.hmolar()
            Ssat = self.aux_water.smolar()
            Gsat = self.aux_water.gibbsmolar()

            dHdT = self.aux_water.first_partial_deriv(cp.iHmolar, cp.iT, cp.iP)
            dGdT = self.aux_water.first_partial_deriv(cp.iGmolar, cp.iT, cp.iP)
            dSdT = self.aux_water.first_partial_deriv(cp.iSmolar, cp.iT, cp.iP)
            dVdT = -Vsat*Vsat*self.aux_water.first_partial_deriv(cp.iDmolar, cp.iT, cp.iP)
            a = self.aux_water.rhomolar()*dVdT * Tsat  # needed for the volume

            Hw0 = Hsat - (Tsat - t) * dHdT
            Sw0 = Ssat - (Tsat - t) * dSdT
            Vw0 = 1 / self.aux_water.rhomolar() * (t / Tsat) ** a

            # TODO experiment with just using the saturation properties
            # TODO does it make sense to extrapolate from Psat(T) instead of Tsat(P)
            # Vw0 = 1 / self.aux_water.rhomolar()
            # Hw0 = self.aux_water.hmolar()
            # Sw0 = self.aux_water.smolar()

            # there is no point to extrapolate the gradients... just introduces noise
            dadTinvw, dadTinvc = self.calc_dadTinv_vap(Tsat, p, yH2O, yCO2)
            dadTw, dadTc = self.calc_dadT_vap(Tsat, p, yH2O, yCO2)
            dadPw, dadPc = self.calc_dadP_vap(Tsat, p, yH2O, yCO2)

        Hw = Hw0 + dadTinvw
        Sw = Sw0 + dadTw
        Gw = Hw - t*Sw
        Vw = Vw0 + dadPw

        self.carbondioxide.update(cp.PT_INPUTS, p, t)
        Hc0 = self.carbondioxide.hmolar()
        Sc0 = self.carbondioxide.smolar()
        Gc0 = self.carbondioxide.gibbsmolar()
        Vc0 = 1 / self.carbondioxide.rhomolar()

        Hc = Hc0 + dadTinvc
        Sc = Sc0 + dadTc
        Gc = Hc - t*Sc
        Vc = Vc0 + dadPc

        H = yH2O*Hw + yCO2*Hc
        S = yH2O*Sw + yCO2*Sc
        G = yH2O*Gw + yCO2*Gc
        V = yH2O*Vw + yCO2*Vc
        D = 1 / V

        return D, V, H, S, G

    def calc_activity_liq(self, t, xH2O, xCO2):
        act_CO2_0 = self.sp.activity_coefficients(t, 1, 0)[0]
        act_H2O_0 = self.sp.activity_coefficients(t, 0, 1)[1]
        act_CO2, act_H2O = self.sp.activity_coefficients(t, xCO2, xH2O)

        activity_CO2 = 8.314 * t * math.log(act_CO2 / act_CO2_0)
        activity_H2O = 8.314 * t * math.log(act_H2O / act_H2O_0)

        return activity_H2O, activity_CO2

    def calc_dadTinv_liq(self, t, xH2O, xCO2):
        delta = 1e-8

        activity_est = self.calc_activity_liq(t * (1 + delta), xH2O, xCO2)
        activity = self.calc_activity_liq(t, xH2O, xCO2)

        dadTinv_H2O = (activity_est[0]/(t*(1+delta)) - activity[0]/t)/(1/(t*(1+delta))-1/t)
        dadTinv_CO2 = (activity_est[1]/(t*(1+delta)) - activity[1]/t)/(1/(t*(1+delta))-1/t)

        return dadTinv_H2O, dadTinv_CO2

    def calc_dadP_liq(self, t, xH2O, xCO2):

        return 0, 0

    def calc_dadT_liq(self, t, xH2O, xCO2):
        delta = 1e-8

        activity_est = self.calc_activity_liq(t * (1 + delta), xH2O, xCO2)
        activity = self.calc_activity_liq(t, xH2O, xCO2)

        dadT_H2O = -(activity_est[0] - activity[0])/(delta*t)
        dadT_CO2 = -(activity_est[1] - activity[1])/(delta*t)

        return dadT_H2O, dadT_CO2

    def calc_liq_phase(self, p, t, xH2O, xCO2):

        dadTinvw, dadTinvc = self.calc_dadTinv_liq(t, xH2O, xCO2)
        dadTw, dadTc = self.calc_dadT_liq(t, xH2O, xCO2)
        dadPw, dadPc = self.calc_dadP_liq(t, xH2O, xCO2)

        self.water.update(cp.PT_INPUTS, p, t)
        Hw0 = self.water.hmolar()
        Sw0 = self.water.smolar()
        Gw0 = self.water.gibbsmolar()
        Vw0 = 1 / self.water.rhomolar()

        Hw = Hw0 + dadTinvw
        Sw = Sw0 + dadTw
        Gw = Hw - t*Sw
        Vw = Vw0 + dadPw

        props = self.engine.thermoPropertiesSubstance(t, p, "CO2@")

        Hc0 = props.enthalpy.val - self.co3_h0
        Sc0 = props.entropy.val - self.co3_s0
        Gc0 = props.gibbs_energy.val
        Vc0 = props.volume.val * 1e-5

        Hc = Hc0 + dadTinvc
        Sc = Sc0 + dadTw
        Gc = Hc - t*Sc
        Vc = Vc0 + dadPc

        H = xH2O*Hw + xCO2*Hc
        S = xH2O*Sw + xCO2*Sc
        G = xH2O*Gw + xCO2*Gc
        # G = H - t * S
        V = xH2O*Vw + xCO2*Vc
        D = 1 / V

        return D, V, H, S, G

    def calc(self, p, t, zw, zc):

        # parition the fluid to determine the phase composition
        phase, vap, liq, alpha = self.sp.calc(p, t, zw)

        if phase == "vap":
            D, V, H, S, G = self.calc_vap_phase(p, t, vap[0], vap[1])
            alpha = 1.0
        elif phase == "liq":
            D, V, H, S, G = self.calc_liq_phase(p, t, liq[0], liq[1])
            alpha = 0.0
        elif phase == "two-phase":
            if 0>alpha<1:
                msg = "alpha is unfeasible"
                raise ValueError(msg)

            Dl, Vl, Hl, Sl, Gl = self.calc_liq_phase(p, t, liq[0], liq[1])
            Dg, Vg, Hg, Sg, Gg = self.calc_vap_phase(p, t, vap[0], vap[1])

            H = Hg * alpha + (1 - alpha) * Hl
            S = Sg * alpha + (1 - alpha) * Sl
            G = Gg * alpha + (1 - alpha) * Gl
            V = Vg * alpha + (1 - alpha) * Vl
            # D = Dg / alpha + (1 - alpha) / Dl
            D = 1/V
            # V = 1/D
        else:
            msg ="Phase not recognised"
            raise ValueError(msg)

        return D, V, H, S, G, vap, liq, alpha


class WaterCO2:

    def __init__(self):
        self.state = cp.AbstractState("?", "Water&CarbonDioxide")

    def calc(self, p, t, zw, zc):

        self.state.set_mole_fractions([zw, 1 - zw])

        self.state.update(cp.PT_INPUTS, p, t)

        H = self.state.hmolar()
        S = self.state.smolar()
        G = self.state.gibbsmolar()
        D = self.state.rhomolar()
        V = 1 / D

        vap = self.state.mole_fractions_vapor()
        liq = self.state.mole_fractions_liquid()

        phase = self.state.phase()
        if phase in [cp.iphase_supercritical_gas, cp.iphase_gas, cp.iphase_supercritical]:
            alpha = 1.0
        elif phase in [cp.iphase_liquid, cp.iphase_supercritical_liquid]:
            alpha = 0.0
        else:
            alpha = self.state.Q()

        return D, V, H, S, G, vap, liq, alpha


class Water:

    def __init__(self):
        self.state = cp.AbstractState("?", "Water")
        # self.co2state = cp.AbstractState("?", "CO2")

    def calc(self, p, t):

        # self.state.set_mole_fractions([zw, 1 - zw])
        # self.state.update(cp.PT_INPUTS, Pref, Tref)
        #
        # h0 = self.state.hmolar()
        # s0 = self.state.smolar()

        self.state.update(cp.PT_INPUTS, p, t)
        # self.co2state.update(cp.PT_INPUTS, p, t)

        D = self.state.rhomolar()
        V = 1 / D
        H = self.state.hmolar() #- h0
        S = self.state.smolar() #- s0
        G = self.state.gibbsmolar()
        vap = None
        liq = None

        phase = self.state.phase()
        if phase in [cp.iphase_liquid, cp.iphase_supercritical_liquid]:
            alpha = 0
        elif phase in [cp.iphase_gas, cp.iphase_supercritical_gas, cp.iphase_supercritical]:
            alpha = 1
        elif phase in [cp.iphase_twophase]:
            alpha = self.state.Q
        else: alpha = -1

        return D, V, H, S, G, vap, liq, alpha


class CO2:
    def __init__(self):
        self.state = cp.AbstractState("?", "CO2")

    def calc(self, p, t):

        self.state.update(cp.PT_INPUTS, p, t)

        D = self.state.rhomolar()
        V = 1 / D
        H = self.state.hmolar() #- h0
        S = self.state.smolar() #- s0
        G = self.state.gibbsmolar()
        vap = None
        liq = None

        phase = self.state.phase()
        if phase in [cp.iphase_liquid, cp.iphase_supercritical_liquid]:
            alpha = 0
        elif phase in [cp.iphase_gas, cp.iphase_supercritical_gas, cp.iphase_supercritical]:
            alpha = 1
        elif phase in [cp.iphase_twophase]:
            alpha = self.state.Q
        else:
            alpha = -1

        return D, V, H, S, G, vap, liq, alpha

if __name__ == "__main__":
    model = Model()
    model.calc(300e5, 523, 0.5, 0.5)