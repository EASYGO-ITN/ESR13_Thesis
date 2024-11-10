import json
import os.path

# TODO implement viscosity & thermal conductivity

Pref = 101325  # set reference pressure
Tref = 298  # set reference temperature

from . import factory
from . import loader
from propertyengine_plugins.coolprop_engine import CoolPropEngine

factory.register("default", CoolPropEngine)

with open(os.path.dirname(__file__)+"\\engines.json") as file:
    data = json.load(file)

     # load the plugins
    loader.load_plugins(data["plugins"])

     # create the characters
    # engines = [factory.create(item) for item in data["engines"]]  # i prefer to return the engines as a dictionary
    engines = {item["type"]: factory.create(item) for item in data["engines"]}


