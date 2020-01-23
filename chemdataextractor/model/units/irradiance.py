# -*- coding: utf-8 -*-
"""
Units and models for irradiance (radiant flux or power per unit area)
.. codeauthor:: Ed Beard <ejb207@cam.ac.uk>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from . import Dimension, Length, Unit, Power
from .quantity_model import QuantityModel
from ...parse.elements import R
import logging

log = logging.getLogger(__name__)


# Creating the irradiance unit
class Irradiance(Dimension):
    """ Defining the irradiance unit (W/m^2)"""
    constituent_dimensions = Power() * Length()**(-2)


class IrradianceModel(QuantityModel):
    """Irradiance model"""
    dimensions = Irradiance()


class IrradianceUnit(Unit):

    def __init__(self, magnitude=0.0, powers=None):
        super(IrradianceUnit, self).__init__(Irradiance(), magnitude, powers)


class WattPerMeterSquared(IrradianceUnit):
    """
    Class watt per meter squared
    """

    def convert_value_to_standard(self, value):
        return value

    def convert_value_from_standard(self, value):
        return value

    def convert_error_to_standard(self, error):
        return error

    def convert_error_from_standard(self, error):
        return error


units_dict = {R('m?W( )?cm[−−-]2', group=0): WattPerMeterSquared}
Irradiance.units_dict.update(units_dict)
Irradiance.standard_units = WattPerMeterSquared()
