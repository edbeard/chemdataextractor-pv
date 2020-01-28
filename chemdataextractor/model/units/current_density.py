# -*- coding: utf-8 -*-
"""
Units and models for current density.
.. codeauthor:: Ed Beard <ejb207@cam.ac.uk>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from . import Dimension, ElectricalCurrent, Length, Unit
from .quantity_model import QuantityModel
from ...parse.elements import R
import logging

log = logging.getLogger(__name__)


# Creating the current density unit
class CurrentDensity(Dimension):
    """ Defining the current density unit"""
    constituent_dimensions = ElectricalCurrent() * Length()**(-2)


class CurrentDensityModel(QuantityModel):
    """Current Density model"""
    dimensions = CurrentDensity()


class CurrentDensityUnit(Unit):

    def __init__(self, magnitude=0.0, powers=None):
        super(CurrentDensityUnit, self).__init__(CurrentDensity(), magnitude, powers)


class AmpPerMeterSquared(CurrentDensityUnit):
    """
    Class for amp per meter squared.
    """

    def convert_value_to_standard(self, value):
        return value

    def convert_value_from_standard(self, value):
        return value

    def convert_error_to_standard(self, error):
        return error

    def convert_error_from_standard(self, error):
        return error

# CurrentDensity.units_dict = {}


# units_dict = {R('(m)?A( )?cm[–\−−-]2', group=0): AmpPerMeterSquared}
# CurrentDensity.units_dict.update(units_dict)
# CurrentDensity.standard_units = AmpPerMeterSquared()
