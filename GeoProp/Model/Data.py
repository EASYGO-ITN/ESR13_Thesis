from enum import Enum


class Data:

    def __init__(self, value, unit="", tag="", description="", reference=""):

        value = value
        units = unit
        SIunits = ""
        SIvalue = ""
        tag = tag
        description = ""
        reference = reference


class Unit:

    def __init__(self, name, dimensions, U2SI):

        self.name = name
        self.dimensions = dimensions
        self.shift = U2SI[0]
        self.mult = U2SI[1]


class BaseDimensions(Enum):
    t = "time"
    L = "length"
    M = "mass"
    m = "moles"
    T = "temperature"


class SIUnits(Enum):
    s = Unit("s", {BaseDimensions.t: 1}, (0, 1))
    m = Unit("m", {BaseDimensions.L: 1}, (0, 1))
    kg = Unit("kg", {BaseDimensions.M: 1}, (0, 1))
    mol = Unit("mol", {BaseDimensions.m: 1}, (0, 1))
    K = Unit("K", {BaseDimensions.T: 1}, (0, 1))


class Area(Unit):

    def __init__(self, name, U2SI=(0, 1)):

        dimensions = {BaseDimensions.L: 2}
        super().__init__(name, dimensions, U2SI)


class Mass(Unit):

    def __init__(self, name, U2SI=(0, 1)):
        dimensions = {BaseDimensions.M: 1}
        super().__init__(name, dimensions, U2SI)


class Pressure(Unit):

    def __init__(self, name, U2SI=(0, 1)):
        dimensions = {BaseDimensions.M: 1, BaseDimensions.L: -1, BaseDimensions.t: -2}
        super().__init__(name, dimensions, U2SI)


class Temperature(Unit):

    def __init__(self, name, U2SI=(0, 1)):
        dimensions = {BaseDimensions.T:1}
        super().__init__(name, dimensions, U2SI)


class dTemperature(Unit):

    def __init__(self, name, U2SI=(0, 1)):

        dimensions = {BaseDimensions.T:1}
        super().__init__(name, dimensions, U2SI)


Pa = Pressure("Pa")
BARa = Pressure("Bar", U2SI=(0, 1e5))

