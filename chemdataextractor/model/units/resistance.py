# -*- coding: utf-8 -*-
"""
Units and models for resistance
.. codeauthor:: Ed Beard <ejb207@cam.ac.uk>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from . import Dimension, ElectricPotential, Unit, ElectricalCurrent
from .quantity_model import QuantityModel
from ...parse.elements import R
import logging

log = logging.getLogger(__name__)


class Resisitance(Dimension):
    """ Defining the resistance."""
    constituent_dimensions = ElectricPotential() / ElectricalCurrent()


class ResisitanceModel(QuantityModel):
    """Irradiance model"""
    dimensions = Resisitance()


class ResisitanceUnit(Unit):

    def __init__(self, magnitude=0.0, powers=None):
        super(ResisitanceUnit, self).__init__(Resisitance(), magnitude, powers)


class Ohm(ResisitanceUnit):
    """
    Class defining the ohm
    """

    def convert_value_to_standard(self, value):
        return value

    def convert_value_from_standard(self, value):
        return value

    def convert_error_to_standard(self, error):
        return error

    def convert_error_from_standard(self, error):
        return error


units_dict = {R('(Ω)|(ohm(s)?)', group=0): Ohm}
Resisitance.units_dict.update(units_dict)
Resisitance.standard_units = Ohm()
