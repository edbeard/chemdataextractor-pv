# -*- coding: utf-8 -*-
"""
Units and models for resistance
.. codeauthor:: Ed Beard <ejb207@cam.ac.uk>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from . import Dimension, Unit
from .resistance import Resistance
from .area import Area
from .quantity_model import QuantityModel
from ...parse.elements import R
import logging

log = logging.getLogger(__name__)


class SpecificResistance(Dimension):
    """ Defining the resistance."""
    constituent_dimensions = Resistance() * Area()


class SpecificResistanceModel(QuantityModel):
    """Irradiance model"""
    dimensions = SpecificResistance()


class SpecificResistanceUnit(Unit):

    def __init__(self, magnitude=0.0, powers=None):
        super(SpecificResistanceUnit, self).__init__(Resistance(), magnitude, powers)
