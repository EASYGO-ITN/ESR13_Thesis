import json
import os.path

# TODO First Law Efficiency
# TODO Second Law Efficiency
# TODO Rescale power plant to mass rate
# TODO \Exergy balance

Pref = 101325  # set reference pressure
Tref = 298  # set reference temperature

Yref = 2023  # set reference year

EUR_to_USD = {2023:	1.08,
              2022:	1.05,
              2021:	1.18,
              2020:	1.14,
              2019:	1.12,
              2018:	1.18,
              2017:	1.13,
              2016:	1.11,
              2015:	1.11,
              2014:	1.33,
              2013:	1.33,
              2012:	1.29,
              2011:	1.39,
              2010:	1.33,
              2009:	1.39,
              2008:	1.47,
              2007:	1.37,
              2006:	1.26,
              2005:	1.24,
              2004:	1.24,
              2003:	1.13,
              2002:	0.95,
              2001:	0.9,
              2000:	0.92,
              }


def convert_EUR_to_USD(euro, year=2010):

    exchange_rate = EUR_to_USD[year]

    dollar = euro * exchange_rate

    return dollar


def convert_USD_to_EUR(dollar, year=2010):

    exchange_rate = 1 / EUR_to_USD[year]

    euro = dollar * exchange_rate

    return euro


PPIs = {"pipe": {2002: 153.69,
                2003: 155.93,
                2004: 187.48,
                2005: 206.08,
                2006: 217.29,
                2007: 214.36,
                2008: 230.56,
                2009: 242.53,
                2010: 268.66,
                2011: 286.11,
                2012: 297.23,
                2013: 300.49,
                2014: 305.36,
                2015: 305.56,
                2016: 302.67,
                2017: 305.08,
                2018: 317.34,
                2019: 321.61,
                2020: 320.72,
                2021: 377.42,
                2022: 434.09,
                2023: 446.72,},
       "turbine": {2002: 165.6,
                   2003: 167.8,
                   2004: 168.72,
                   2005: 168.51,
                   2006: 173.92,
                   2007: 183.27,
                   2008: 206.19,
                   2009: 223.63,
                   2010: 221.96,
                   2011: 225.18,
                   2012: 223.54,
                   2013: 227.98,
                   2014: 233.78,
                   2015: 231.68,
                   2016: 232.34,
                   2017: 223.05,
                   2018: 220.63,
                   2019: 233.13,
                   2020: 240.5,
                   2021: 246.89,
                   2022: 255.18,
                   2023: 266.33,},
       "heat_exchanger": {2002: 174.75,
                          2003: 174.48,
                          2004: 186.33,
                          2005: 214.33,
                          2006: 232.92,
                          2007: 240.75,
                          2008: 251.32,
                          2009: 247.23,
                          2010: 248.73,
                          2011: 255.83,
                          2012: 264.39,
                          2013: 268.2,
                          2014: 271.66,
                          2015: 280.33,
                          2016: 287.18,
                          2017: 289.62,
                          2018: 304.47,
                          2019: 313.91,
                          2020: 320.12,
                          2021: 349.08,
                          2022: 397.02,
                          2023: 421.6,},
       "pump": {2002: 100,
                2003: 100,
                2004: 102.22,
                2005: 108.41,
                2006: 112.63,
                2007: 117.89,
                2008: 123.65,
                2009: 127.46,
                2010: 128.96,
                2011: 133.39,
                2012: 137.22,
                2013: 140.17,
                2014: 143.48,
                2015: 145.98,
                2016: 147.46,
                2017: 150.13,
                2018: 155.15,
                2019: 158.88,
                2020: 161.53,
                2021: 168.08,
                2022: 192.57,
                2023: 210.51,}}


def calc_PPI(type, year):

    return PPIs[type][year]


from . import factory
from . import loader

with open(os.path.dirname(__file__)+"\\components.json") as file:
    data = json.load(file)

    # load the plugins
    loader.load_plugins(data["plugins"])

    # create the characters
    # we actually want to add the components to the Simulator module
    for item in data["components"]:
        globals()[item["type"]] = factory.create(item)