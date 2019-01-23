# -*- coding: utf-8 -*-
"""
chemdataextractor.units.temperatures.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Units and models for temperatures.

Taketomo Isazawa (ti250@cam.ac.uk)

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from .quantity_model import QuantityModel
from .unit import Unit
from .dimension import Dimension
from ...parse.elements import W, I, R, Optional, Any, OneOrMore, Not, ZeroOrMore
from ...parse.actions import merge, join

log = logging.getLogger(__name__)


class TemperatureUnit(Unit):

    def __init__(self, magnitude=0.0, powers=None):
        super(TemperatureUnit, self).__init__(Temperature(), magnitude, powers)

class Kelvin(TemperatureUnit):

    def convert_value_to_standard(self, value):
        return value

    def convert_value_from_standard(self, value):
        return value

    def convert_error_to_standard(self, error):
        return error

    def convert_error_from_standard(self, error):
        return error

class Celsius(TemperatureUnit):

    def convert_value_to_standard(self, value):
        return value + 273.15

    def convert_value_from_standard(self, value):
        return value - 273.15

    def convert_error_to_standard(self, error):
        return error

    def convert_error_from_standard(self, error):
        return error


class Fahrenheit(TemperatureUnit):

    def convert_value_to_standard(self, value):
        return (value + 459.67) * (5. / 9.)

    def convert_value_from_standard(self, value):
        return value * (9. / 5.) - 459.67

    def convert_error_to_standard(self, error):
        return error * (5. / 9.)

    def convert_error_from_standard(self, error):
        return error * (9. / 5.)


class Temperature(Dimension):
    pass


class TemperatureModel(QuantityModel):

    dimensions = Temperature()


units_dict = {R('°?(((K|k)elvin(s)?)|K)\.?', group=0): Kelvin,
              R('(°|((C|c)elsius|°?C))\.?', group=0): Celsius,
              R('°?((F|f)ahrenheit|F)\.?', group=0): Fahrenheit}
Temperature.units_dict = units_dict
