
########### Genetic algorithm settings #################

N_var = 3
# reduced pressure, dT superheat, Tmin
Variables_low_bound  = [0.3, 3, 303]
Variables_up_bound   = [0.8, 15, 400]

N_obj = 1
N_constr = 0

N_species = N_var * 10

N_individuals_0 = 3*N_species  ## size of the initial generation
N_individuals = N_species  # size of all the subsequent generations
N_gen = N_var * 10

Seed_init = 1 # change this number to change the distribution of the initial population
cross_over_prob = 0.8
cross_over_eta  = 15
mut_prob = 0.2
mut_eta  = 0.3

SensitivityParams = {
"Hot fluid input2"         : [0.025, 0.05, 0.075, 0.125, 0.15, 0.175, 0.225, 0.25, 0.275, 0.325, 0.35, 0.375],
"Hot fluid input1"         : [150+273.15, 175+273.15, 200+273.15, 225+273.15, 250+273.15, 275+273.15],
"Working fluid comp"       : [["n-Propane", 1], ["CycloPropane", 1], ["IsoButane", 1], ["n-Butane", 1], ["Isopentane", 1], ["Isohexane", 1], ["Cyclopentane", 1], ["n-Heptane", 1],],
}

Parameters = {
"is Cycle regenerated"     : False,
# "Hot fluid comp"           : ["water", 0.95, "carbondioxide", 0.05],
# "Hot fluid engine"         : "geoprop",
# "Hot fluid table path"     : "../propertyengine_plugins/LookUpTables/SuperDuperTable",
"Hot fluid tables"         : False,
"Hot fluid comp"           : ["water", 1],
"Hot fluid engine"         : "default",
"Hot fluid input spec"     : 'TQ',
"Hot fluid input1"         : 450,
"Hot fluid input2"         : 0.15,
"Hot fluid mass flow"      : 50,
"Cold fluid comp"          : ["air", 1],
"Cold fluid engine"        : "default",
"Condenser dP"             : 120,
"Cooling Pump IsenEff"     : 0.6,
"Working fluid comp"       : ["nButane", 1],
"Working fluid engine"     : "default",
"MaxSuperheat"             : 15,
"MinSuperheat"     : 2,
"TestMassRates"            : [1, 2.5, 5, 10, 25, 50, 100, 150, 200]
}






