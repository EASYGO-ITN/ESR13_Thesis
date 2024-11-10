import CoolProp as cp
import math
import numpy as np

Pref = 101325
Tref = 298


class SpycherPruss2009:
    Tmin_low = 12 + 273.15  # degK
    Tmax_low = 99 + 273.15  # degK
    Tmin_high = 109 + 273.15  # degK
    Tmax_high = 300 + 273.15  # degK

    Pmin = 1e5
    Pmax = 600e5

    R = 83.144598  # bar.cm3/(mol.K)

    @staticmethod
    def interpolate(func, low, high, val, *args, **kwargs):
        if low <= val <= high:
            val_low = func(low, *args, **kwargs)
            val_high = func(high, *args, **kwargs)
            ratio = (high - val) / (high - low)

            if type(val_low) in (int, float):
                return val_low * ratio + (1 - ratio) * val_high
            elif type(val_low) in (tuple, list, set):
                return (val_low[i] * ratio + (1 - ratio) * val_high[i] for i in range(len(val_low)))
            else:
                raise ValueError("The type of the function output is not supported ")
        else:
            raise ValueError("The value ({}) is outside the specified range (min: {} to max: {}".format(val, low, high))

    def a_CO2(self, T):
        if self.Tmin_low <= T <= self.Tmax_low:
            # low temperature model
            return 7.54e7 - 4.13e4 * T
        elif T < self.Tmin_high:
            return self.interpolate(self.a_CO2, self.Tmax_low, self.Tmin_high, T)
        else:
            # high temperature model
            return 8.008e7 - 4.984e4 * T

    def a_H2O(self, T):
        if self.Tmin_low <= T <= self.Tmax_low:
            # low temperature model
            return 128475900.0  # my addition
        elif T < self.Tmin_high:
            return self.interpolate(self.a_H2O, self.Tmax_low, self.Tmin_high, T)
        else:
            # high temperature model
            return 1.337e8 - 1.4e4 * T

    def a_CO2_H2O(self, T, aCO2_aH2O, yCO2, yH2O):
        if self.Tmin_low <= T <= self.Tmax_low:
            # low temperature model
            return 7.89e7, 7.89e7
        elif T < self.Tmin_high:
            return self.interpolate(self.a_CO2_H2O, self.Tmax_low, self.Tmin_high, T, aCO2_aH2O, yCO2, yH2O)
        else:
            # high temperature model
            KCO2_H2O = self.K_CO2_H2O(T)
            KH2O_CO2 = self.K_H2O_CO2(T)

            kCO2_H2O = KCO2_H2O * yCO2 + KH2O_CO2 * yH2O
            kH2O_CO2 = KH2O_CO2 * yH2O + KCO2_H2O * yCO2

            aCO2_H2O = math.sqrt(aCO2_aH2O) * (1 - kCO2_H2O)
            aH2O_CO2 = math.sqrt(aCO2_aH2O) * (1 - kH2O_CO2)

            return aCO2_H2O, aH2O_CO2

    def K_CO2_H2O(self, T):
        if self.Tmin_low <= T <= self.Tmax_low:
            # low temperature model
            return 0.0
        elif T < self.Tmin_high:
            return self.interpolate(self.K_CO2_H2O, self.Tmax_low, self.Tmin_high, T)
        else:
            # high temperature model
            return 0.4228 - 7.422e-4 * T

    def K_H2O_CO2(self, T):
        if self.Tmin_low <= T <= self.Tmax_low:
            # low temperature model
            return 0.0
        elif T < self.Tmin_high:
            return self.interpolate(self.K_H2O_CO2, self.Tmax_low, self.Tmin_high, T)
        else:
            # high temperature model
            return 1.427e-2 - 4.037e-4 * T

    def a_mix(self, aCO2, aH2O, aCO2_H2O, aH2O_CO2, yCO2, yH2O):

        return aCO2 * yCO2 * yCO2 + aH2O * yH2O * yH2O + (aCO2_H2O + aH2O_CO2) * yCO2 * yH2O

    def a(self, T, yCO2, yH2O):
        aCO2 = self.a_CO2(T)
        aH2O = self.a_H2O(T)
        aCO2_H2O, aH2O_CO2 = self.a_CO2_H2O(T, aCO2 * aH2O, yCO2, yH2O)
        amix = self.a_mix(aCO2, aH2O, aCO2_H2O, aH2O_CO2, yCO2, yH2O)

        return amix, aCO2, aH2O, aCO2_H2O, aH2O_CO2

    def b_CO2(self, T):
        if self.Tmin_low <= T <= self.Tmax_low:
            # low temperature
            return 27.8
        elif T < self.Tmin_high:
            return self.interpolate(self.b_CO2, self.Tmax_low, self.Tmin_high, T)
        else:
            # high temperature model
            return 28.25

    def b_H2O(self, T):
        if self.Tmin_low <= T <= self.Tmax_low:
            # low temperature model
            return 18.18
        elif T < self.Tmin_high:
            return self.interpolate(self.b_H2O, self.Tmax_low, self.Tmin_high, T)
        else:
            # high temperature model
            return 15.70

    def b_mix(self, bCO2, bH2O, yCO2, yH2O):
        return bCO2 * yCO2 + bH2O * yH2O

    def b(self, T, yCO2, yH2O):
        bCO2 = self.b_CO2(T)
        bH2O = self.b_H2O(T)

        bmix = self.b_mix(bCO2, bH2O, yCO2, yH2O)

        return bmix, bCO2, bH2O

    def fugacity_coefficients(self, T, P, yCO2, yH2O):
        Pbar = P * 1e-5

        amix, aCO2, aH2O, aCO2_H2O, aH2O_CO2 = self.a(T, yCO2, yH2O)
        bmix, bCO2, bH2O = self.b(T, yCO2, yH2O)
        KCO2_H2O = self.K_CO2_H2O(T)
        KH2O_CO2 = self.K_H2O_CO2(T)

        a2 = -self.R * T / Pbar
        a1 = -(self.R * T * bmix/Pbar - amix/(Pbar * math.sqrt(T)) + bmix * bmix)
        a0 = -amix * bmix / (Pbar * math.sqrt(T))

        Vs = CubicSolver(a2, a1, a0)

        V = max(Vs)

        T05 = math.sqrt(T)
        T15 = T05 * T

        aux1 = (Pbar*V/(self.R*T)-1)/bmix
        aux2 = -math.log(Pbar*(V-bmix)/(self.R*T))
        aux3 = -(yH2O*yH2O*yCO2*(KH2O_CO2-KCO2_H2O) + yCO2*yCO2*yH2O*(KCO2_H2O-KH2O_CO2))*math.sqrt(aH2O*aCO2)
        aux4 = (amix/(bmix*self.R*T15))*math.log(V/(V+bmix))

        test = V/(V+bmix)

        c1 = (yH2O*(aH2O_CO2+aCO2_H2O)+2*yCO2*aCO2)
        c2 = yCO2*yH2O*(KCO2_H2O-KH2O_CO2)*math.sqrt(aCO2*aH2O)
        c3 = ((c1 + aux3 + c2)/amix - bCO2/bmix)

        ln_phi_CO2 = bCO2*aux1 + aux2 + c3*aux4

        h1 = (yCO2*(aCO2_H2O+aH2O_CO2)+2*yH2O*aH2O)
        h2 = yH2O*yCO2*(KH2O_CO2 - KCO2_H2O)*math.sqrt(aH2O*aCO2)
        h3 = ((h1 + aux3 + h2)/amix - bH2O/bmix)

        ln_phi_H2O = bH2O*aux1 + aux2 + h3*aux4

        return math.exp(ln_phi_CO2), math.exp(ln_phi_H2O)

    def log_K0_H2O(self, T):
        Tc = T - 273.15

        if self.Tmin_low <= T <= self.Tmax_low:
            # low temperature model
            return -2.209 + 3.097e-2 * Tc - 1.098e-4 * Tc * Tc + 2.048e-7 * Tc * Tc * Tc
        elif T < self.Tmin_high:
            return self.interpolate(self.log_K0_H2O, self.Tmax_low, self.Tmin_high, T)
        else:
            # high temperature model
            return -2.1077 + 2.8127e-2 * Tc - 8.4298e-5 * Tc * Tc + 1.4969e-7 * Tc * Tc * Tc - 1.1812e-10 * Tc * Tc * Tc * Tc

    def K0_H2O(self, T):
        # return math.exp(log_K0_H2O(T))
        return math.pow(10, self.log_K0_H2O(T))

    def log_K0_CO2(self, T):
        Tc = T - 273.15

        if self.Tmin_low <= T <= self.Tmax_low:
            # low temperature model
            return 1.189 + 1.304e-2 * Tc - 5.446e-5 * Tc * Tc
        elif T < self.Tmin_high:
            return self.interpolate(self.log_K0_CO2, self.Tmax_low, self.Tmin_high, T)
        else:
            # high temperature model
            return 1.668 + 3.992e-3 * Tc - 1.156e-5 * Tc * Tc + 1.593e-9 * Tc * Tc * Tc

    def K0_CO2(self, T):
        # return math.exp(log_K0_CO2(T))
        return math.pow(10, self.log_K0_CO2(T))

    def V_CO2(self, T):
        dT = T - 373.15
        if self.Tmin_low <= T <= self.Tmax_low:
            # low temperature
            return 32.6
        elif T < self.Tmin_high:
            return self.interpolate(self.V_CO2, self.Tmax_low, self.Tmin_high, T)
        else:
            return 32.6 + 3.413e-2 * dT

    def V_H2O(self, T):
        dT = T - 373.15
        if self.Tmin_low <= T <= self.Tmax_low:
            # low temperature model
            return 18.1
        elif T < self.Tmin_high:
            return self.interpolate(self.V_H2O, self.Tmax_low, self.Tmin_high, T)
        else:
            # high temperature model
            return 18.1 + 3.137e-2 * dT

    def A_m(self, T):
        dT = (T - 373.15)
        if self.Tmin_low <= T <= self.Tmax_low:
            # low temperature model
            return 0
        elif T < self.Tmin_high:
            return self.interpolate(self.A_m, self.Tmax_low, self.Tmin_high, T)
        else:
            # high temperature model

            return -3.084e-2 * dT + 1.927e-5 * dT * dT

    def Pref_CO2(self, T):
        Tcutoff = 100 + 273.15
        Tc = T - 273.15

        if self.Tmin_low <= T <= Tcutoff:
            # low temperature model
            return 1
        elif T < self.Tmin_high:
            return self.interpolate(self.Pref_CO2, self.Tmax_low, self.Tmin_high, T)
        else:
            # high temperature model
            return -1.9906e-1 + 2.0471e-3 * Tc + 1.0152e-4 * Tc * Tc - 1.4234e-6 * Tc * Tc * Tc + 1.4168e-8 * Tc * Tc * Tc * Tc

    def Pref_H2O(self, T):
        Tcutoff = 100 + 273.15

        if self.Tmin_low <= T <= Tcutoff:
            return 1.0
        elif T < self.Tmin_high:
            return self.interpolate(self.Pref_H2O, self.Tmax_low, self.Tmin_high, T)

        else:
            water = cp.AbstractState("?", "Water")
            water.update(cp.QT_INPUTS, 0.5, T)
            return water.p() * 1e-5

    def K_CO2(self, T, P):
        Pbar = P * 1e-5
        return self.K0_CO2(T) * math.exp((Pbar - self.Pref_CO2(T)) * self.V_CO2(T) / (self.R * T))

    def K_H2O(self, T, P):
        Pbar = P * 1e-5
        return self.K0_H2O(T) * math.exp((Pbar - self.Pref_H2O(T)) * self.V_H2O(T) / (self.R * T))

    def activity_coefficients(self, T, xCO2, xH2O):
        Am = self.A_m(T)

        ln_gammaCO2 = 2 * Am * xCO2 * xH2O * xH2O
        ln_gammeH2O = (Am - 2 * Am * xH2O) * xCO2 * xCO2

        return math.exp(ln_gammaCO2), math.exp(ln_gammeH2O)

    def lambda_(self, T):
        InvT = 1 / T

        return 2.217e-4 * T + 1.074 * InvT + 2648 * InvT * InvT

    def xi_(self, T):
        InvT = 1 / T

        return 1.3e-5 * T - 20.12 * InvT + 5259 * InvT * InvT

    def gamma_CO2_correction(self, T, mNa, mK, mCa, mMg, mCl, mSO4):

        lamb = self.lambda_(T)
        xi = self.xi_(T)

        aux1 = 1 + (mNa + mK + mCa + mMg + mCl + mSO4) / 55.508
        aux2 = 2 * lamb * (mNa + mK + 2 * mCa + 2 * mMg)
        aux3 = xi * mCl * (mNa + mK + mCa + mMg)

        gamma_correction = aux1 * math.exp(aux2 + aux3 - 0.07 * mSO4)

        return gamma_correction

    def calcSP2009(self, P, T, mNa, mK, mCa, mMg, mCl, mSO4):

        if T < self.Tmin_low:
            raise ValueError("The temperature ({} K)is below the minimum temperature ({} K)".format(T, self.Tmin_low))
        if T > self.Tmax_high:
            raise ValueError("The temperature ({} K)is above the maximum temperature ({} K)".format(T, self.Tmax_high))
        if P < self.Pmin:
            raise ValueError("The pressure ({} Pa)is below the minimum pressure ({} Pa)".format(P, self.Pmin))
        if P > self.Pmax:
            raise ValueError("The pressure ({} Pa)is above the maximum pressure ({} Pa)".format(P, self.Pmax))

        Pbar = P * 1e-5

        KCO2 = self.K_CO2(T, P)
        KH2O = self.K_H2O(T, P)

        gammaCO2corr = self.gamma_CO2_correction(T, mNa, mK, mCa, mMg, mCl, mSO4)

        yH2O = 0
        xCO2 = 0
        xSalt = 0
        mSalt = mNa + mK + mCa + mMg + mCl + mSO4

        max_iter = 1

        if T > self.Tmin_high:
            yH2O = self.Pref_H2O(T) / Pbar
            xCO2 = 0.009
            max_iter = 10

        xH2O = 1 - xCO2 - xSalt
        for i in range(max_iter):
            mCO2 = xCO2 * 55.508 / xH2O
            xSalt = mSalt / (55.508 + mSalt + mCO2)

            yCO2 = 1 - yH2O
            xH2O = 1 - xCO2 - xSalt

            phiCO2, phiH2O = self.fugacity_coefficients(T, P, yCO2, yH2O)
            gammaCO2, gammaH2O = self.activity_coefficients(T, xCO2, xH2O)

            A = KH2O * gammaH2O / (phiH2O * Pbar)
            B = phiCO2 * Pbar / (55.508 * gammaCO2 * gammaCO2corr * KCO2)

            yH2O = (1 - B) * 55.508 / ((1 / A - B) * (mSalt + 55.508) + mSalt * B)
            xCO2 = B * (1 - yH2O)

        return yH2O, xCO2, xSalt

    def calc(self, P, T, zH2O):

        zCO2 = 1 - zH2O

        water = cp.AbstractState("?", "Water")
        water.update(cp.QT_INPUTS, 0.5, T)
        Psat = water.p()

        if P > Psat:
            yH2O, xCO2, xsalts = self.calcSP2009(P, T, 0, 0, 0, 0, 0, 0)

            yCO2 = 1 - yH2O
            xH2O = 1 - xCO2 - xsalts

            if yH2O <= 1:
                alpha = (zH2O - xH2O) / (yH2O - xH2O)
            else:
                alpha = None
        else:
            alpha = 1.1  # all the water has boiled off

        if alpha is None:
            # water boiled off - lets see how this works out
            vapour = [zH2O, zCO2]
            liquid = [zH2O, zCO2]
            type = "vap"
        elif alpha < 0:
            # the fluid is totally liquid
            vapour = [zH2O, zCO2]
            liquid = [zH2O, zCO2]
            type = "liq"
        elif alpha > 1:
            # the fluid is totally vapour
            vapour = [zH2O, zCO2]
            liquid = [zH2O, zCO2]
            type = "vap"
        else:
            # two phase mixtures
            vapour = [yH2O, 1 - yH2O]
            liquid = [1 - xCO2, xCO2]
            type = "two-phase"

        return type, vapour, liquid, alpha

    # helper function
    def calc_xCO2(self, P, T):
        yH2O, xCO2, xsalts = self.calcSP2009(P, T, 0, 0, 0, 0, 0, 0)

        return xCO2*100

    def calc_yH2O(self, P, T):
        yH2O, xCO2, xsalts = self.calcSP2009(P, T, 0, 0, 0, 0, 0, 0)

        return yH2O * 100


class CubicSolver:

    def __new__(cls, a2, a1, a0):

        return cls.__call__(cls, a2, a1, a0)

    def __call__(self, a2, a1, a0):

        p = (3 * a1 - a2 * a2) / 3
        q = (2 * a2 * a2 * a2 - 9 * a2 * a1 + 27 * a0) / 27

        R = q * q / 4 + p * p * p / 27

        if R <= 0:
            # taken from https://en.wikipedia.org/wiki/Cubic_equation#Cardano's_formula:~:text=Trigonometric%20and%20hyperbolic%20solutions
            m = 2 * math.sqrt(-p / 3)
            theta = math.acos(3 * q / (p * m)) / 3

            x1 = m * math.cos(theta) - a2 / 3
            x2 = m * math.cos(theta - 2 * math.pi / 3) - a2 / 3
            x3 = m * math.cos(theta - 4 * math.pi / 3) - a2 / 3
        else:
            # taken from https://mathworld.wolfram.com/CubicFormula.html#:~:text=(48)-,Defining,-(49)
            P = np.cbrt(-q / 2 + math.sqrt(R))
            Q = np.cbrt(-q / 2 - math.sqrt(R))

            x1 = P + Q - a2 / 3
            x2 = x1
            x3 = x1

        return x1, x2, x3
