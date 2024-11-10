
########### Genetic algorithm settings #################

N_var = 2
Variables_low_bound  = [0.1, 0.1e5]
Variables_up_bound   = [0.99, 5e5]

N_obj = 1
N_constr = 0

N_species = N_var * 10

N_individuals_0 = 3*N_species  ## size of the initial generation
N_individuals = N_species  # size of all the subsequent generations
N_gen = N_var * 10

Seed_init = 1# change this number to change the distribution of the initial population
cross_over_prob = 0.8
cross_over_eta  = 15
mut_prob = 0.2
mut_eta  = 0.3

SensitivityParams = {
"Hot fluid input2"         : [0.25],
"Hot fluid input1"         : [200+273.15],
}

Parameters = {
"is Cycle regenerated"     : True,
"Hot fluid comp"           : ["water", 1.00, "carbondioxide", 0.00],
"Hot fluid engine"         : "geoprop",
# "Hot fluid table path"     : "../propertyengine_plugins/LookUpTables/SuperDuperTable",
"Hot fluid tables"         : False,
# "Hot fluid comp"           : ["water", 1],
# "Hot fluid engine"         : "default",
"Hot fluid input spec"     : 'TQ',
"Hot fluid input1"         : 175+273.15,
"Hot fluid input2"         : 0.0,
"Hot fluid mass flow"      : 50,
"Cold fluid comp"          : ["air", 1],
"Cold fluid engine"        : "default",
"Condenser dP"             : 120,
"Cooling Pump IsenEff"     : 0.6,
"TestMassRates"            : [1, 2.5, 5, 10, 25, 50, 100, 150, 200]
}




