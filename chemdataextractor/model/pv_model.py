"""
Model classes for properties related to a photovoltaic device

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import re

from .base import BaseModel, StringType, ModelType
from .units.substance_amount_density import AmounOfSubstanceDensityModel
from .units.area import AreaModel
from .units.current_density import CurrentDensityModel
from .units.electric_potential import ElectricPotentialModel
from .units.irradiance import IrradianceModel
from .units.length import LengthModel
from .units.ratio import RatioModel
from .units.resistance import ResisitanceModel
from .units.time import TimeModel
from ..parse.elements import R, I, Optional, W, Group, NoMatch, Any, Start, SkipTo, Not
from ..parse.actions import merge, join
from ..parse.cem import strict_chemical_label

from ..model.units.quantity_model import DimensionlessModel
from ..parse.auto import AutoTableParserOptionalCompound, AutoSentenceParserOptionalCompound

log = logging.getLogger(__name__)

# Models for Photovoltaic Properties
common_substrates = (
    W('FTO') | (I('flourine') + Optional(I('doped')) + I('tin') + I('oxide')) |
    W('ITO') | (I('indium') + Optional(I('doped')) + I('tin') + I('oxide')) |
    I('glass') |
    W('NiO') | (I('nickel') + I('oxide'))
).add_action(join)

common_spectra = (
    I('AM') + (
        I('1.5G') |
        I('1.5')
    ) |
    I('AM1.5G')
).add_action(join)

common_semiconductors = (
    (W('TiO2') | (I('titanium') + I('dioxide')) | I('titania') |
     W('ZnO') | (I('zinc') + I('oxide')) |
     W('NiO') | (I('nickel') + I('oxide')) |
     W('Zn2SnO4') | (I('zinc') + I('stannate')) |
     W('SnO2') | (I('tin') + I('oxide'))
     ) + Optional(I('film')) + Optional(I('anode'))
).add_action(join)

common_redox_couples = (
    R('I[−−-]\/( )?I3[−−-]') |
    R('T2\/( )?T[−−-]') |
    I('I-') + W('/') + I('I3-')
).add_action(join)


common_dyes = (
    I('N719')
)


# Common properties for photovoltaic cells:
class OpenCircuitVoltage(ElectricPotentialModel):
    """Testing out a model"""
    specifier = StringType(parse_expression=I('Voc'), required=True, contextual=False, updatable=True)
    parsers = [AutoTableParserOptionalCompound()]


class ShortCircuitCurrentDensity(CurrentDensityModel):
    specifier = StringType(parse_expression=I('Jsc'), required=True, contextual=False, updatable=True)
    parsers = [AutoTableParserOptionalCompound()]


class FillFactor(DimensionlessModel):
    specifier = StringType(parse_expression=(I('FF') | (I('fill') + I('factor')).add_action(join)), required=True, contextual=False, updatable=True)
    parsers = [AutoTableParserOptionalCompound()]


class PowerConversionEfficiency(RatioModel):
    specifier = StringType(parse_expression=(I('PCE') | I('η') | I('eff')), required=True, contextual=False, updatable=True)
    parsers = [AutoTableParserOptionalCompound()]


class Dye(BaseModel):
    """Dye Model that identifies from alphanumerics"""
    specifier = StringType(parse_expression=((I('dye') | I('sample') | R('sensiti[zs]er')) + Not(I('loading'))).add_action(join), required=True, contextual=False)
    raw_value = StringType(parse_expression=((Start() + SkipTo(W('sdfkljlk'))).add_action(join)) | R('[a-zA-Z0-9_/]*'), required=True)
    parsers = [AutoTableParserOptionalCompound()]


class Reference(DimensionlessModel):
    specifier = StringType(parse_expression=I('Ref'), required=True)
    parsers = [AutoTableParserOptionalCompound()]


class RedoxCouple(BaseModel):
    specifier = StringType(parse_expression=(I('redox') + R('[Cc]ouple(s)?')).add_action(join), required=True)
    raw_value = StringType(parse_expression=common_redox_couples, required=True)
    parsers = [AutoTableParserOptionalCompound(), AutoSentenceParserOptionalCompound()]


class DyeLoading(AmounOfSubstanceDensityModel):
    specifier = StringType(parse_expression=((Optional(I('dye')) + (I('loading') | I('amount'))).add_action(join) | W('Γ') | W('Cm')), required=True)
    exponent = StringType(parse_expression=(W('10').hide() + Optional(R('[−-−‒‐‑]')) + R('\d')).add_action(join))
    parsers = [AutoTableParserOptionalCompound()]


class CounterElectrode(BaseModel):
    specifier = StringType(parse_expression=((Optional(I('counter')) + R('[Ee]lectrode(s)?')).add_action(join) | Not(I('PCE')) + R('CE(s)?')), required=True)
    raw_value = StringType(parse_expression=(Start() + SkipTo(W('sdfkljlk'))).add_action(join), required=True)
    parsers = [AutoTableParserOptionalCompound()]


class SemiconductorThickness(LengthModel):
    specifier = StringType(parse_expression=(R('[Ss]emiconductor(s)?') | R('[Aa]node(s)?')), required=True)
    raw_value = StringType(required=True, contextual=False)
    parsers = [AutoTableParserOptionalCompound(), AutoSentenceParserOptionalCompound()]


class Semiconductor(BaseModel):
    specifier = StringType(parse_expression=(R('[Ss]emiconductor(s)?') | R('[Aa]node(s)?')), required=True)
    raw_value = StringType(parse_expression=(Start() + SkipTo(W('sdfkljlk'))).add_action(join) | common_semiconductors)
    thickness = ModelType(SemiconductorThickness, required=False)
    parsers = [AutoTableParserOptionalCompound(), AutoSentenceParserOptionalCompound()]


class ActiveArea(AreaModel):
    specifier = StringType(parse_expression=((I('active') + I('area')).add_action(join)), required=True)
    parsers = [AutoTableParserOptionalCompound()]


class SimulatedSolarLightIntensity(IrradianceModel):
    specifier = StringType(parse_expression=(I('irradiance') | (I('light') + I('intensity') + Optional(I('of'))).add_action(join)), required=True)
    spectra = StringType(parse_expression=common_spectra)
    parsers = [AutoTableParserOptionalCompound(), AutoSentenceParserOptionalCompound()]


class Electrolyte(BaseModel):
    specifier = StringType(parse_expression=(I('electrolyte') | I('liquid')), required=True)
    raw_value = StringType(parse_expression=(Start() + SkipTo(W('sdfkljlk'))).add_action(join), required=True)
    parsers = [AutoTableParserOptionalCompound()]


class Substrate(BaseModel):
    specifier = StringType(parse_expression=I('substrate'), required=True, contextual=False)
    raw_value = StringType(parse_expression=((Start() + SkipTo(W('sdfkljlk'))).add_action(join) | common_substrates), required=True, contextual=False)
    parsers = [AutoTableParserOptionalCompound(), AutoSentenceParserOptionalCompound()]


class ChargeTransferResistance(ResisitanceModel):
    specifier = StringType(parse_expression=(R('Rct\d?') | R('Rk')), required=True)
    parsers = [AutoTableParserOptionalCompound()]


class SeriesResistance(ResisitanceModel):
    specifier = StringType(parse_expression=W('Rs'), required=True)
    parsers = [AutoTableParserOptionalCompound()]


class ExposureTime(TimeModel):
    specifier = StringType(parse_expression=(I('exposure') | (Optional(I('exposure')) + I('time'))).add_action(join), required=True)
    parsers = [AutoTableParserOptionalCompound()]


class PhotovoltaicCell(BaseModel):
    """ Class for photovoltaic devices. Uses a number of automatic parsers."""

    specifier = StringType(parse_expression=Any().hide(), required=False, contextual=False)

    voc = ModelType(OpenCircuitVoltage, required=False, contextual=False)
    ff = ModelType(FillFactor, required=False, contextual=False)
    pce = ModelType(PowerConversionEfficiency, required=False, contextual=False)
    jsc = ModelType(ShortCircuitCurrentDensity, required=False, contextual=False)
    dye = ModelType(Dye, required=False, contextual=False)
    ref = ModelType(Reference, required=False, contextual=False)
    redox_couple = ModelType(RedoxCouple, required=False, contextual=False)
    dye_loading = ModelType(DyeLoading, required=False, contextual=False)
    counter_electrode = ModelType(CounterElectrode, required=False, contextual=False)
    semiconductor = ModelType(Semiconductor, required=False, contextual=False)
    active_area = ModelType(ActiveArea, required=False, contextual=False)
    solar_simulator = ModelType(SimulatedSolarLightIntensity, required=False, contextual=True)
    electrolyte = ModelType(Electrolyte, required=False, contextual=False)
    substrate = ModelType(Substrate, required=False, contextual=False)
    charge_transfer_resisitance = ModelType(ChargeTransferResistance, required=False, contextual=False)
    series_resisitance = ModelType(SeriesResistance, required=False, contextual=False)
    exposure_time = ModelType(ExposureTime, required=False, contextual=True)

    parsers = [AutoTableParserOptionalCompound()]#, AutoSentenceParserOptionalCompound()]

# Sentence parsers for separately  sentence information


class SentenceDye(BaseModel):
    """ Dye mentioned in a sentence. Identifies def"""

    alphanumeric_label= R('^(([A-Z][\--–−]?)+\d{1,3})$')('labels')
    lenient_label = alphanumeric_label | strict_chemical_label

    specifier = StringType(parse_expression=((I('dye') | R('sensiti[zs]er')) + Not(I('loading'))).add_action(join), required=True, contextual=False)
    raw_value = StringType(parse_expression=(common_dyes | lenient_label), required=True)
    parsers = [AutoSentenceParserOptionalCompound()]
