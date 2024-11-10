from .base_component import Component
from Simulator import factory


class compressor(Component):

    def __init__(self):
        super().__init__()


def register():
    factory.register("compressor", compressor)