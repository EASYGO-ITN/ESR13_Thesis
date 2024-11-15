import matplotlib.pyplot as plt
import tikzplotlib

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

years = [i for i in EUR_to_USD]
exchange_rate = [EUR_to_USD[i] for i in EUR_to_USD]

fig, ax = plt.subplots()

ax.plot(years, exchange_rate)
ax.set_xlabel("Year")
ax.set_ylabel("Exchange Rate/\\unit{\\USD\\per\\EUR}")

tikzplotlib.save("CurrencyCorrection.tex")
