# -*- coding: utf-8 -*-
"""
Units and models for area.
.. codeauthor:: Ed Beard <ejb207@cam.ac.uk>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from . import Dimension, Length, Unit
from .quantity_model import QuantityModel
from ...parse.elements import R
import logging

log = logging.getLogger(__name__)


# Creating the area unit
class Area(Dimension):
    """ Defining the area unit (W/m^2)"""
    constituent_dimensions = Length()**(2)


class AreaModel(QuantityModel):
    """Irradiance model"""
    dimensions = Area()


class AreaUnit(Unit):

    def __init__(self, magnitude=0.0, powers=None):
        super(AreaUnit, self).__init__(Area(), magnitude, powers)


class MetersSquaredAreaUnit:
    """
    Class meter squared
    """

    def convert_value_to_standard(self, value):
        return value

    def convert_value_from_standard(self, value):
        return value

    def convert_error_to_standard(self, error):
        return error

    def convert_error_from_standard(self, error):
        return error


units_dict = {R('m2', group=0): MetersSquaredAreaUnit}
Area.units_dict.update(units_dict)
Area.standard_units = MetersSquaredAreaUnit()
