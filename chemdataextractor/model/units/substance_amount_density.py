# -*- coding: utf-8 -*-
"""
Units and models for the substance amount density.
.. codeauthor:: Ed Beard <ejb207@cam.ac.uk>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from . import Dimension, AmountOfSubstance, Length, Unit
from .quantity_model import QuantityModel
from ...parse.elements import R
import logging

log = logging.getLogger(__name__)


# Creating the current density unit
class AmountOfSubstanceDensity(Dimension):
    """ Defining the current density unit"""
    constituent_dimensions = AmountOfSubstance() * Length()**(-2)


class AmountOfSubstanceDensityModel(QuantityModel):
    """Current Density model"""
    dimensions = AmountOfSubstanceDensity()


class AmountOfSubstanceDensityUnit(Unit):

    def __init__(self, magnitude=0.0, powers=None):
        super(AmountOfSubstanceDensityUnit, self).__init__(AmountOfSubstanceDensity(), magnitude, powers)


class MolPerMeterSquared(AmountOfSubstanceDensityUnit):
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


units_dict = {R('[Mm](ol)(e(s)?)?( )?cm[−−-]2', group=0): MolPerMeterSquared}
AmountOfSubstanceDensity.units_dict.update(units_dict)
AmountOfSubstanceDensity.standard_units = MolPerMeterSquared()
