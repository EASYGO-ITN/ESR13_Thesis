from SP2009 import SpycherPruss2009
import CoolProp as cp

sp = SpycherPruss2009()

xCO2 = sp.calc_xCO2(6e5, 293)  # %
print(xCO2)

print(xCO2*0.044/(xCO2*0.044 + (100-xCO2)*0.018))  # mass frac


xCO2 = sp.calc_xCO2(5005000, 293)  # %
print(xCO2)
xCO2 = sp.calc_xCO2(10005000, 304)  # %
print(xCO2)
xCO2 = sp.calc_xCO2(30005000, 333)  # %
print(xCO2)

print(xCO2*0.044/(xCO2*0.044 + (100-xCO2)*0.018))  # mass frac

xCO2 = sp.calc_xCO2(40e5, 273 + 20)  # %
print(xCO2)

xCO2 = sp.calc_xCO2(150e5, 273 + 60)  # %
print(xCO2)

xCO2 = sp.calc_xCO2(20e5, 273 + 70)  # %
print(xCO2)
xCO2 = sp.calc_xCO2(20e5, 273 + 200)  # %
print(xCO2)

xCO2 = sp.calc_xCO2(16e5, 273 + 200)  # %
print(xCO2)


from CoolProp.CoolProp import PropsSI

print(PropsSI("P", "T", 200+273, "Q", 0.5, "water"))