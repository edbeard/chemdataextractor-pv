# -*- coding: utf-8 -*-
"""
Test the Table Document element and complex Table autoparsers.

"""

from chemdataextractor.doc import Caption, Document
from chemdataextractor.doc.table import Table, Cell
from chemdataextractor.model import TemperatureModel, StringType, Compound, ModelType, DimensionlessModel
from chemdataextractor.parse.cem import CompoundParser, CompoundHeadingParser, ChemicalLabelParser, CompoundTableParser
from chemdataextractor.model.units.energy import EnergyModel
from chemdataextractor.model.pv_model import OpenCircuitVoltage, ShortCircuitCurrentDensity, FillFactor, PowerConversionEfficiency, Dye
from chemdataextractor.model.model import BaseModel
from chemdataextractor.parse import W, R, Any
from chemdataextractor.parse.auto import AutoTableParser, AutoTableParserOptionalCompound, AutoSentenceParserOptionalCompound

import logging
import unittest

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


# 1.MODEL CLASSES USED FOR TESTING OF THE TABLE
class AbsentModel(TemperatureModel):
    specifier = StringType(parse_expression=W('Nothing'), required=True, contextual=False, updatable=False)
    compound = ModelType(Compound, required=True, contextual=True, updatable=False, binding=True)
    parser = [AutoTableParser()]


class Enthalpy(EnergyModel):
    compound = ModelType(Compound, required=False, binding=True)
    specifier = StringType(parse_expression=R('^Enthalpy$'), required=True, contextual=False, updatable=True)
    absent = ModelType(AbsentModel, required=True, contextual=True, updatable=False)
    parsers = [AutoTableParser()]


class Reference(DimensionlessModel):
    specifier = StringType(parse_expression=R('Ref'), required=True, contextual=False, updatable=False)
    compound = ModelType(Compound, required=True, contextual=True, updatable=False, binding=True)
    enthalpy = ModelType(Enthalpy, required=True, contextual=True, updatable=False)
    parsers = [AutoTableParser()]


class CurieTemperature(TemperatureModel):
    specifier = StringType(parse_expression=R(r'^\[?T(C|c)(urie)?[1-2]?\]?$'), required=True, contextual=False, updatable=True)
    compound = ModelType(Compound, required=True, contextual=True, updatable=False, binding=True)
    reference = ModelType(Reference, required=True, contextual=True, updatable=False)
    parsers = [AutoTableParser()]


def _get_serialised_records(records, models=None):
    serialized_list = []
    for record in records:
        if models is None or type(record) in models:
            serialized_list.append(record.serialize())
    return serialized_list


# 2. TESTS
class TestNestedTable(unittest.TestCase):
    """
    Tests for automated parsing of tables with complex structure, which involves parsing of the table
    row header region, as well as a complex nested model hierarchy with different combinations of `required`
    submodels.
    """

    maxDiff = None

    def do_table(self, expected):
        Compound.parsers = [CompoundParser(), CompoundHeadingParser(), ChemicalLabelParser()]
        table = Table(caption=Caption(""),
                      table_data="tests/data/tables/table_example_3.csv",
                      models=[CurieTemperature])
        result = _get_serialised_records(table.records, models=[CurieTemperature])
        self.assertCountEqual(expected, result)
        Compound.parsers = [CompoundParser(), CompoundHeadingParser(), ChemicalLabelParser(), CompoundTableParser()]
        Enthalpy.absent.required = True
        Enthalpy.absent.contextual = True
        Reference.enthalpy.required = True
        Reference.enthalpy.contextual = True
        CurieTemperature.reference.required = True
        CurieTemperature.reference.contextual = True

    def test_required_submodels_1(self):
        """
        Tests a combination of `required` parameters for submodels.
        """
        Enthalpy.absent.required = True
        Enthalpy.absent.contextual = False
        Reference.enthalpy.required = True
        Reference.enthalpy.contextual = False
        CurieTemperature.reference.required = True
        CurieTemperature.reference.contextual = False
        expected = []
        self.do_table(expected)

    def test_required_submodels_2(self):
        """
        Tests a combination of `required` parameters for submodels.
        """
        Enthalpy.absent.required = False
        Reference.enthalpy.required = True
        CurieTemperature.reference.required = True
        expected = [
            {'CurieTemperature': {'raw_value': '293', 'raw_units': '(K)', 'value': [293.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['MnO2']}}, 'reference': {'Reference': {'raw_value': '52–55', 'value': [52.0, 55.0], 'specifier': 'Ref', 'compound': {'Compound': {'names': ['MnO2']}}, 'enthalpy': {'Enthalpy': {'raw_value': '5', 'raw_units': '(kJ)', 'value': [5.0], 'units': '(10^3.0) * Joule^(1.0)', 'specifier': 'Enthalpy', 'compound': {'Compound': {'names': ['MnO2']}}}}}}}},
            {'CurieTemperature': {'raw_value': '293', 'raw_units': '(K)', 'value': [293.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['MnO2']}}, 'reference': {'Reference': {'raw_value': '56', 'value': [56.0], 'specifier': 'Ref', 'compound': {'Compound': {'names': ['MnO2']}}, 'enthalpy': {'Enthalpy': {'raw_value': '1', 'raw_units': '(kJ)', 'value': [1.0], 'units': '(10^3.0) * Joule^(1.0)', 'specifier': 'Enthalpy', 'compound': {'Compound': {'names': ['MnO2']}}}}}}}},
            {'CurieTemperature': {'raw_value': '337', 'raw_units': '(K)', 'value': [337.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['La2']}}, 'reference': {'Reference': {'raw_value': '57', 'value': [57.0], 'specifier': 'Ref', 'compound': {'Compound': {'names': ['La2']}}, 'enthalpy': {'Enthalpy': {'raw_value': '1', 'raw_units': '(kJ)', 'value': [1.0], 'units': '(10^3.0) * Joule^(1.0)', 'specifier': 'Enthalpy', 'compound': {'Compound': {'names': ['La2']}}}}}}}},
            {'CurieTemperature': {'raw_value': '292', 'raw_units': '(K)', 'value': [292.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['La0.67Ba0.33']}}, 'reference': {'Reference': {'raw_value': '26', 'value': [26.0], 'specifier': 'Ref', 'compound': {'Compound': {'names': ['La0.67Ba0.33']}}, 'enthalpy': {'Enthalpy': {'raw_value': '5', 'raw_units': '(kJ)', 'value': [5.0], 'units': '(10^3.0) * Joule^(1.0)', 'specifier': 'Enthalpy', 'compound': {'Compound': {'names': ['La0.67Ba0.33']}}}}}}}},
            {'CurieTemperature': {'raw_value': '252', 'raw_units': '(K)', 'value': [252.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['La0.67Ca0.33']}}, 'reference': {'Reference': {'raw_value': '26', 'value': [26.0], 'specifier': 'Ref', 'compound': {'Compound': {'names': ['La0.67Ca0.33']}}, 'enthalpy': {'Enthalpy': {'raw_value': '5', 'raw_units': '(kJ)', 'value': [5.0], 'units': '(10^3.0) * Joule^(1.0)', 'specifier': 'Enthalpy', 'compound': {'Compound': {'names': ['La0.67Ca0.33']}}}}}}}},
            {'CurieTemperature': {'raw_value': '312', 'raw_units': '(K)', 'value': [312.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['La0.67Sr0.33MnO3']}}, 'reference': {'Reference': {'raw_value': '58', 'value': [58.0], 'specifier': 'Ref', 'compound': {'Compound': {'names': ['La0.67Sr0.33MnO3']}}, 'enthalpy': {'Enthalpy': {'raw_value': '1.5', 'raw_units': '(kJ)', 'value': [1.5], 'units': '(10^3.0) * Joule^(1.0)', 'specifier': 'Enthalpy', 'compound': {'Compound': {'names': ['La0.67Sr0.33MnO3']}}}}}}}},
            {'CurieTemperature': {'raw_value': '321', 'raw_units': '(K)', 'value': [321.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['La0.67Sr0.33MnO3']}}, 'reference': {'Reference': {'raw_value': '58', 'value': [58.0], 'specifier': 'Ref', 'compound': {'Compound': {'names': ['La0.67Sr0.33MnO3']}}, 'enthalpy': {'Enthalpy': {'raw_value': '1.5', 'raw_units': '(kJ)', 'value': [1.5], 'units': '(10^3.0) * Joule^(1.0)', 'specifier': 'Enthalpy', 'compound': {'Compound': {'names': ['La0.67Sr0.33MnO3']}}}}}}}},
            {'CurieTemperature': {'raw_value': '309', 'raw_units': '(K)', 'value': [309.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['Ba0.33Mn0.98Ti0.02O3']}}, 'reference': {'Reference': {'raw_value': '39', 'value': [39.0], 'specifier': 'Ref', 'compound': {'Compound': {'names': ['Ba0.33Mn0.98Ti0.02O3']}}, 'enthalpy': {'Enthalpy': {'raw_value': '1', 'raw_units': '(kJ)', 'value': [1.0], 'units': '(10^3.0) * Joule^(1.0)', 'specifier': 'Enthalpy', 'compound': {'Compound': {'names': ['Ba0.33Mn0.98Ti0.02O3']}}}}}}}},
            {'CurieTemperature': {'raw_value': '309', 'raw_units': '(K)', 'value': [309.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['Ba0.33Mn0.98Ti0.02O3']}}, 'reference': {'Reference': {'raw_value': '39', 'value': [39.0], 'specifier': 'Ref', 'compound': {'Compound': {'names': ['Ba0.33Mn0.98Ti0.02O3']}}, 'enthalpy': {'Enthalpy': {'raw_value': '5', 'raw_units': '(kJ)', 'value': [5.0], 'units': '(10^3.0) * Joule^(1.0)', 'specifier': 'Enthalpy', 'compound': {'Compound': {'names': ['Ba0.33Mn0.98Ti0.02O3']}}}}}}}},
            {'CurieTemperature': {'raw_value': '286', 'raw_units': '(K)', 'value': [286.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['Ba0.33Mn0.98Ti0.02O3']}}, 'reference': {'Reference': {'raw_value': '286', 'value': [286.0], 'specifier': 'Ref', 'compound': {'Compound': {'names': ['Ba0.33Mn0.98Ti0.02O3']}}, 'enthalpy': {'Enthalpy': {'raw_value': '5', 'raw_units': '(kJ)', 'value': [5.0], 'units': '(10^3.0) * Joule^(1.0)', 'specifier': 'Enthalpy', 'compound': {'Compound': {'names': ['Ba0.33Mn0.98Ti0.02O3']}}}}}}}},
            {'CurieTemperature': {'raw_value': '286', 'raw_units': '(K)', 'value': [286.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['Ba0.33Mn0.98Ti0.02O3']}}, 'reference': {'Reference': {'raw_value': '286', 'value': [286.0], 'specifier': 'Ref', 'compound': {'Compound': {'names': ['Ba0.33Mn0.98Ti0.02O3']}}, 'enthalpy': {'Enthalpy': {'raw_value': '1', 'raw_units': '(kJ)', 'value': [1.0], 'units': '(10^3.0) * Joule^(1.0)', 'specifier': 'Enthalpy', 'compound': {'Compound': {'names': ['Ba0.33Mn0.98Ti0.02O3']}}}}}}}}
        ]
        self.do_table(expected)

    def test_required_submodels_3(self):
        """
        Tests a combination of `required` parameters for submodels.
        """
        Enthalpy.absent.required = True
        Enthalpy.absent.contextual = False
        Reference.enthalpy.required = False
        CurieTemperature.reference.required = True
        expected = [
            {'CurieTemperature': {'raw_value': '293', 'raw_units': '(K)', 'value': [293.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['MnO2']}}, 'reference': {'Reference': {'raw_value': '52–55', 'value': [52.0, 55.0], 'specifier': 'Ref', 'compound': {'Compound': {'names': ['MnO2']}}}}}},
            {'CurieTemperature': {'raw_value': '293', 'raw_units': '(K)', 'value': [293.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['MnO2']}}, 'reference': {'Reference': {'raw_value': '56', 'value': [56.0], 'specifier': 'Ref', 'compound': {'Compound': {'names': ['MnO2']}}}}}},
            {'CurieTemperature': {'raw_value': '337', 'raw_units': '(K)', 'value': [337.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['La2']}}, 'reference': {'Reference': {'raw_value': '57', 'value': [57.0], 'specifier': 'Ref', 'compound': {'Compound': {'names': ['La2']}}}}}},
            {'CurieTemperature': {'raw_value': '292', 'raw_units': '(K)', 'value': [292.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['La0.67Ba0.33']}}, 'reference': {'Reference': {'raw_value': '26', 'value': [26.0], 'specifier': 'Ref', 'compound': {'Compound': {'names': ['La0.67Ba0.33']}}}}}},
            {'CurieTemperature': {'raw_value': '252', 'raw_units': '(K)', 'value': [252.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['La0.67Ca0.33']}}, 'reference': {'Reference': {'raw_value': '26', 'value': [26.0], 'specifier': 'Ref', 'compound': {'Compound': {'names': ['La0.67Ca0.33']}}}}}},
            {'CurieTemperature': {'raw_value': '312', 'raw_units': '(K)', 'value': [312.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['La0.67Sr0.33MnO3']}}, 'reference': {'Reference': {'raw_value': '58', 'value': [58.0], 'specifier': 'Ref', 'compound': {'Compound': {'names': ['La0.67Sr0.33MnO3']}}}}}},
            {'CurieTemperature': {'raw_value': '321', 'raw_units': '(K)', 'value': [321.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['La0.67Sr0.33MnO3']}}, 'reference': {'Reference': {'raw_value': '58', 'value': [58.0], 'specifier': 'Ref', 'compound': {'Compound': {'names': ['La0.67Sr0.33MnO3']}}}}}},
            {'CurieTemperature': {'raw_value': '309', 'raw_units': '(K)', 'value': [309.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['Ba0.33Mn0.98Ti0.02O3']}}, 'reference': {'Reference': {'raw_value': '39', 'value': [39.0], 'specifier': 'Ref', 'compound': {'Compound': {'names': ['Ba0.33Mn0.98Ti0.02O3']}}}}}},
            {'CurieTemperature': {'raw_value': '286', 'raw_units': '(K)', 'value': [286.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['Ba0.33Mn0.98Ti0.02O3']}}, 'reference': {'Reference': {'raw_value': '286', 'value': [286.0], 'specifier': 'Ref', 'compound': {'Compound': {'names': ['Ba0.33Mn0.98Ti0.02O3']}}}}}}
        ]
        self.do_table(expected)

    def test_required_submodels_4(self):
        """
        Tests a combination of `required` parameters for submodels.
        """
        Enthalpy.absent.required = False
        Reference.enthalpy.required = False
        CurieTemperature.reference.required = True
        expected = [
            {'CurieTemperature': {'raw_value': '293', 'raw_units': '(K)', 'value': [293.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['MnO2']}}, 'reference': {'Reference': {'raw_value': '52–55', 'value': [52.0, 55.0], 'specifier': 'Ref', 'compound': {'Compound': {'names': ['MnO2']}}, 'enthalpy': {'Enthalpy': {'raw_value': '5', 'raw_units': '(kJ)', 'value': [5.0], 'units': '(10^3.0) * Joule^(1.0)', 'specifier': 'Enthalpy', 'compound': {'Compound': {'names': ['MnO2']}}}}}}}},
            {'CurieTemperature': {'raw_value': '293', 'raw_units': '(K)', 'value': [293.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['MnO2']}}, 'reference': {'Reference': {'raw_value': '56', 'value': [56.0], 'specifier': 'Ref', 'compound': {'Compound': {'names': ['MnO2']}}, 'enthalpy': {'Enthalpy': {'raw_value': '1', 'raw_units': '(kJ)', 'value': [1.0], 'units': '(10^3.0) * Joule^(1.0)', 'specifier': 'Enthalpy', 'compound': {'Compound': {'names': ['MnO2']}}}}}}}},
            {'CurieTemperature': {'raw_value': '337', 'raw_units': '(K)', 'value': [337.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['La2']}}, 'reference': {'Reference': {'raw_value': '57', 'value': [57.0], 'specifier': 'Ref', 'compound': {'Compound': {'names': ['La2']}}, 'enthalpy': {'Enthalpy': {'raw_value': '1', 'raw_units': '(kJ)', 'value': [1.0], 'units': '(10^3.0) * Joule^(1.0)', 'specifier': 'Enthalpy', 'compound': {'Compound': {'names': ['La2']}}}}}}}},
            {'CurieTemperature': {'raw_value': '292', 'raw_units': '(K)', 'value': [292.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['La0.67Ba0.33']}}, 'reference': {'Reference': {'raw_value': '26', 'value': [26.0], 'specifier': 'Ref', 'compound': {'Compound': {'names': ['La0.67Ba0.33']}}, 'enthalpy': {'Enthalpy': {'raw_value': '5', 'raw_units': '(kJ)', 'value': [5.0], 'units': '(10^3.0) * Joule^(1.0)', 'specifier': 'Enthalpy', 'compound': {'Compound': {'names': ['La0.67Ba0.33']}}}}}}}},
            {'CurieTemperature': {'raw_value': '252', 'raw_units': '(K)', 'value': [252.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['La0.67Ca0.33']}}, 'reference': {'Reference': {'raw_value': '26', 'value': [26.0], 'specifier': 'Ref', 'compound': {'Compound': {'names': ['La0.67Ca0.33']}}, 'enthalpy': {'Enthalpy': {'raw_value': '5', 'raw_units': '(kJ)', 'value': [5.0], 'units': '(10^3.0) * Joule^(1.0)', 'specifier': 'Enthalpy', 'compound': {'Compound': {'names': ['La0.67Ca0.33']}}}}}}}},
            {'CurieTemperature': {'raw_value': '312', 'raw_units': '(K)', 'value': [312.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['La0.67Sr0.33MnO3']}}, 'reference': {'Reference': {'raw_value': '58', 'value': [58.0], 'specifier': 'Ref', 'compound': {'Compound': {'names': ['La0.67Sr0.33MnO3']}}, 'enthalpy': {'Enthalpy': {'raw_value': '1.5', 'raw_units': '(kJ)', 'value': [1.5], 'units': '(10^3.0) * Joule^(1.0)', 'specifier': 'Enthalpy', 'compound': {'Compound': {'names': ['La0.67Sr0.33MnO3']}}}}}}}},
            {'CurieTemperature': {'raw_value': '321', 'raw_units': '(K)', 'value': [321.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['La0.67Sr0.33MnO3']}}, 'reference': {'Reference': {'raw_value': '58', 'value': [58.0], 'specifier': 'Ref', 'compound': {'Compound': {'names': ['La0.67Sr0.33MnO3']}}, 'enthalpy': {'Enthalpy': {'raw_value': '1.5', 'raw_units': '(kJ)', 'value': [1.5], 'units': '(10^3.0) * Joule^(1.0)', 'specifier': 'Enthalpy', 'compound': {'Compound': {'names': ['La0.67Sr0.33MnO3']}}}}}}}},
            {'CurieTemperature': {'raw_value': '309', 'raw_units': '(K)', 'value': [309.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['Ba0.33Mn0.98Ti0.02O3']}}, 'reference': {'Reference': {'raw_value': '39', 'value': [39.0], 'specifier': 'Ref', 'compound': {'Compound': {'names': ['Ba0.33Mn0.98Ti0.02O3']}}, 'enthalpy': {'Enthalpy': {'raw_value': '1', 'raw_units': '(kJ)', 'value': [1.0], 'units': '(10^3.0) * Joule^(1.0)', 'specifier': 'Enthalpy', 'compound': {'Compound': {'names': ['Ba0.33Mn0.98Ti0.02O3']}}}}}}}},
            {'CurieTemperature': {'raw_value': '309', 'raw_units': '(K)', 'value': [309.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['Ba0.33Mn0.98Ti0.02O3']}}, 'reference': {'Reference': {'raw_value': '39', 'value': [39.0], 'specifier': 'Ref', 'compound': {'Compound': {'names': ['Ba0.33Mn0.98Ti0.02O3']}}, 'enthalpy': {'Enthalpy': {'raw_value': '5', 'raw_units': '(kJ)', 'value': [5.0], 'units': '(10^3.0) * Joule^(1.0)', 'specifier': 'Enthalpy', 'compound': {'Compound': {'names': ['Ba0.33Mn0.98Ti0.02O3']}}}}}}}},
            {'CurieTemperature': {'raw_value': '286', 'raw_units': '(K)', 'value': [286.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['Ba0.33Mn0.98Ti0.02O3']}}, 'reference': {'Reference': {'raw_value': '286', 'value': [286.0], 'specifier': 'Ref', 'compound': {'Compound': {'names': ['Ba0.33Mn0.98Ti0.02O3']}}, 'enthalpy': {'Enthalpy': {'raw_value': '5', 'raw_units': '(kJ)', 'value': [5.0], 'units': '(10^3.0) * Joule^(1.0)', 'specifier': 'Enthalpy', 'compound': {'Compound': {'names': ['Ba0.33Mn0.98Ti0.02O3']}}}}}}}},
            {'CurieTemperature': {'raw_value': '286', 'raw_units': '(K)', 'value': [286.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['Ba0.33Mn0.98Ti0.02O3']}}, 'reference': {'Reference': {'raw_value': '286', 'value': [286.0], 'specifier': 'Ref', 'compound': {'Compound': {'names': ['Ba0.33Mn0.98Ti0.02O3']}}, 'enthalpy': {'Enthalpy': {'raw_value': '1', 'raw_units': '(kJ)', 'value': [1.0], 'units': '(10^3.0) * Joule^(1.0)', 'specifier': 'Enthalpy', 'compound': {'Compound': {'names': ['Ba0.33Mn0.98Ti0.02O3']}}}}}}}}
        ]
        self.do_table(expected)

    def test_required_submodels_5(self):
        """
        Tests a combination of `required` parameters for submodels.
        """
        Enthalpy.absent.required = True
        Enthalpy.absent.contextual = False
        Reference.enthalpy.required = True
        Reference.enthalpy.contextual = False
        CurieTemperature.reference.required = False
        expected = [
            {'CurieTemperature': {'raw_value': '293', 'raw_units': '(K)', 'value': [293.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['MnO2']}}}},
            {'CurieTemperature': {'raw_value': '337', 'raw_units': '(K)', 'value': [337.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['La2']}}}},
            {'CurieTemperature': {'raw_value': '292', 'raw_units': '(K)', 'value': [292.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['La0.67Ba0.33']}}}},
            {'CurieTemperature': {'raw_value': '252', 'raw_units': '(K)', 'value': [252.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['La0.67Ca0.33']}}}},
            {'CurieTemperature': {'raw_value': '312', 'raw_units': '(K)', 'value': [312.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['La0.67Sr0.33MnO3']}}}},
            {'CurieTemperature': {'raw_value': '321', 'raw_units': '(K)', 'value': [321.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['La0.67Sr0.33MnO3']}}}},
            {'CurieTemperature': {'raw_value': '309', 'raw_units': '(K)', 'value': [309.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['Ba0.33Mn0.98Ti0.02O3']}}}},
            {'CurieTemperature': {'raw_value': '286', 'raw_units': '(K)', 'value': [286.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['Ba0.33Mn0.98Ti0.02O3']}}}}
        ]
        self.do_table(expected)

    def test_required_submodels_6(self):
        """
        Tests a combination of `required` parameters for submodels.
        """
        Enthalpy.absent.required = False
        Reference.enthalpy.required = True
        CurieTemperature.reference.required = False
        expected = [
            {'CurieTemperature': {'raw_value': '293', 'raw_units': '(K)', 'value': [293.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['MnO2']}}, 'reference': {'Reference': {'raw_value': '52–55', 'value': [52.0, 55.0], 'specifier': 'Ref', 'compound': {'Compound': {'names': ['MnO2']}}, 'enthalpy': {'Enthalpy': {'raw_value': '5', 'raw_units': '(kJ)', 'value': [5.0], 'units': '(10^3.0) * Joule^(1.0)', 'specifier': 'Enthalpy', 'compound': {'Compound': {'names': ['MnO2']}}}}}}}},
            {'CurieTemperature': {'raw_value': '293', 'raw_units': '(K)', 'value': [293.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['MnO2']}}, 'reference': {'Reference': {'raw_value': '56', 'value': [56.0], 'specifier': 'Ref', 'compound': {'Compound': {'names': ['MnO2']}}, 'enthalpy': {'Enthalpy': {'raw_value': '1', 'raw_units': '(kJ)', 'value': [1.0], 'units': '(10^3.0) * Joule^(1.0)', 'specifier': 'Enthalpy', 'compound': {'Compound': {'names': ['MnO2']}}}}}}}},
            {'CurieTemperature': {'raw_value': '337', 'raw_units': '(K)', 'value': [337.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['La2']}}, 'reference': {'Reference': {'raw_value': '57', 'value': [57.0], 'specifier': 'Ref', 'compound': {'Compound': {'names': ['La2']}}, 'enthalpy': {'Enthalpy': {'raw_value': '1', 'raw_units': '(kJ)', 'value': [1.0], 'units': '(10^3.0) * Joule^(1.0)', 'specifier': 'Enthalpy', 'compound': {'Compound': {'names': ['La2']}}}}}}}},
            {'CurieTemperature': {'raw_value': '292', 'raw_units': '(K)', 'value': [292.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['La0.67Ba0.33']}}, 'reference': {'Reference': {'raw_value': '26', 'value': [26.0], 'specifier': 'Ref', 'compound': {'Compound': {'names': ['La0.67Ba0.33']}}, 'enthalpy': {'Enthalpy': {'raw_value': '5', 'raw_units': '(kJ)', 'value': [5.0], 'units': '(10^3.0) * Joule^(1.0)', 'specifier': 'Enthalpy', 'compound': {'Compound': {'names': ['La0.67Ba0.33']}}}}}}}},
            {'CurieTemperature': {'raw_value': '252', 'raw_units': '(K)', 'value': [252.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['La0.67Ca0.33']}}, 'reference': {'Reference': {'raw_value': '26', 'value': [26.0], 'specifier': 'Ref', 'compound': {'Compound': {'names': ['La0.67Ca0.33']}}, 'enthalpy': {'Enthalpy': {'raw_value': '5', 'raw_units': '(kJ)', 'value': [5.0], 'units': '(10^3.0) * Joule^(1.0)', 'specifier': 'Enthalpy', 'compound': {'Compound': {'names': ['La0.67Ca0.33']}}}}}}}},
            {'CurieTemperature': {'raw_value': '312', 'raw_units': '(K)', 'value': [312.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['La0.67Sr0.33MnO3']}}, 'reference': {'Reference': {'raw_value': '58', 'value': [58.0], 'specifier': 'Ref', 'compound': {'Compound': {'names': ['La0.67Sr0.33MnO3']}}, 'enthalpy': {'Enthalpy': {'raw_value': '1.5', 'raw_units': '(kJ)', 'value': [1.5], 'units': '(10^3.0) * Joule^(1.0)', 'specifier': 'Enthalpy', 'compound': {'Compound': {'names': ['La0.67Sr0.33MnO3']}}}}}}}},
            {'CurieTemperature': {'raw_value': '321', 'raw_units': '(K)', 'value': [321.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['La0.67Sr0.33MnO3']}}, 'reference': {'Reference': {'raw_value': '58', 'value': [58.0], 'specifier': 'Ref', 'compound': {'Compound': {'names': ['La0.67Sr0.33MnO3']}}, 'enthalpy': {'Enthalpy': {'raw_value': '1.5', 'raw_units': '(kJ)', 'value': [1.5], 'units': '(10^3.0) * Joule^(1.0)', 'specifier': 'Enthalpy', 'compound': {'Compound': {'names': ['La0.67Sr0.33MnO3']}}}}}}}},
            {'CurieTemperature': {'raw_value': '309', 'raw_units': '(K)', 'value': [309.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['Ba0.33Mn0.98Ti0.02O3']}}, 'reference': {'Reference': {'raw_value': '39', 'value': [39.0], 'specifier': 'Ref', 'compound': {'Compound': {'names': ['Ba0.33Mn0.98Ti0.02O3']}}, 'enthalpy': {'Enthalpy': {'raw_value': '1', 'raw_units': '(kJ)', 'value': [1.0], 'units': '(10^3.0) * Joule^(1.0)', 'specifier': 'Enthalpy', 'compound': {'Compound': {'names': ['Ba0.33Mn0.98Ti0.02O3']}}}}}}}},
            {'CurieTemperature': {'raw_value': '309', 'raw_units': '(K)', 'value': [309.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['Ba0.33Mn0.98Ti0.02O3']}}, 'reference': {'Reference': {'raw_value': '39', 'value': [39.0], 'specifier': 'Ref', 'compound': {'Compound': {'names': ['Ba0.33Mn0.98Ti0.02O3']}}, 'enthalpy': {'Enthalpy': {'raw_value': '5', 'raw_units': '(kJ)', 'value': [5.0], 'units': '(10^3.0) * Joule^(1.0)', 'specifier': 'Enthalpy', 'compound': {'Compound': {'names': ['Ba0.33Mn0.98Ti0.02O3']}}}}}}}},
            {'CurieTemperature': {'raw_value': '286', 'raw_units': '(K)', 'value': [286.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['Ba0.33Mn0.98Ti0.02O3']}}, 'reference': {'Reference': {'raw_value': '286', 'value': [286.0], 'specifier': 'Ref', 'compound': {'Compound': {'names': ['Ba0.33Mn0.98Ti0.02O3']}}, 'enthalpy': {'Enthalpy': {'raw_value': '5', 'raw_units': '(kJ)', 'value': [5.0], 'units': '(10^3.0) * Joule^(1.0)', 'specifier': 'Enthalpy', 'compound': {'Compound': {'names': ['Ba0.33Mn0.98Ti0.02O3']}}}}}}}},
            {'CurieTemperature': {'raw_value': '286', 'raw_units': '(K)', 'value': [286.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['Ba0.33Mn0.98Ti0.02O3']}}, 'reference': {'Reference': {'raw_value': '286', 'value': [286.0], 'specifier': 'Ref', 'compound': {'Compound': {'names': ['Ba0.33Mn0.98Ti0.02O3']}}, 'enthalpy': {'Enthalpy': {'raw_value': '1', 'raw_units': '(kJ)', 'value': [1.0], 'units': '(10^3.0) * Joule^(1.0)', 'specifier': 'Enthalpy', 'compound': {'Compound': {'names': ['Ba0.33Mn0.98Ti0.02O3']}}}}}}}}
        ]
        self.do_table(expected)

    def test_required_submodels_7(self):
        """
        Tests a combination of `required` parameters for submodels.
        """
        Enthalpy.absent.required = True
        Enthalpy.absent.contextual = False
        Reference.enthalpy.required = False
        CurieTemperature.reference.required = False
        expected = [
            {'CurieTemperature': {'raw_value': '293', 'raw_units': '(K)', 'value': [293.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['MnO2']}}, 'reference': {'Reference': {'raw_value': '52–55', 'value': [52.0, 55.0], 'specifier': 'Ref', 'compound': {'Compound': {'names': ['MnO2']}}}}}},
            {'CurieTemperature': {'raw_value': '293', 'raw_units': '(K)', 'value': [293.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['MnO2']}}, 'reference': {'Reference': {'raw_value': '56', 'value': [56.0], 'specifier': 'Ref', 'compound': {'Compound': {'names': ['MnO2']}}}}}},
            {'CurieTemperature': {'raw_value': '337', 'raw_units': '(K)', 'value': [337.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['La2']}}, 'reference': {'Reference': {'raw_value': '57', 'value': [57.0], 'specifier': 'Ref', 'compound': {'Compound': {'names': ['La2']}}}}}},
            {'CurieTemperature': {'raw_value': '292', 'raw_units': '(K)', 'value': [292.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['La0.67Ba0.33']}}, 'reference': {'Reference': {'raw_value': '26', 'value': [26.0], 'specifier': 'Ref', 'compound': {'Compound': {'names': ['La0.67Ba0.33']}}}}}},
            {'CurieTemperature': {'raw_value': '252', 'raw_units': '(K)', 'value': [252.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['La0.67Ca0.33']}}, 'reference': {'Reference': {'raw_value': '26', 'value': [26.0], 'specifier': 'Ref', 'compound': {'Compound': {'names': ['La0.67Ca0.33']}}}}}},
            {'CurieTemperature': {'raw_value': '312', 'raw_units': '(K)', 'value': [312.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['La0.67Sr0.33MnO3']}}, 'reference': {'Reference': {'raw_value': '58', 'value': [58.0], 'specifier': 'Ref', 'compound': {'Compound': {'names': ['La0.67Sr0.33MnO3']}}}}}},
            {'CurieTemperature': {'raw_value': '321', 'raw_units': '(K)', 'value': [321.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['La0.67Sr0.33MnO3']}}, 'reference': {'Reference': {'raw_value': '58', 'value': [58.0], 'specifier': 'Ref', 'compound': {'Compound': {'names': ['La0.67Sr0.33MnO3']}}}}}},
            {'CurieTemperature': {'raw_value': '309', 'raw_units': '(K)', 'value': [309.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['Ba0.33Mn0.98Ti0.02O3']}}, 'reference': {'Reference': {'raw_value': '39', 'value': [39.0], 'specifier': 'Ref', 'compound': {'Compound': {'names': ['Ba0.33Mn0.98Ti0.02O3']}}}}}},
            {'CurieTemperature': {'raw_value': '286', 'raw_units': '(K)', 'value': [286.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['Ba0.33Mn0.98Ti0.02O3']}}, 'reference': {'Reference': {'raw_value': '286', 'value': [286.0], 'specifier': 'Ref', 'compound': {'Compound': {'names': ['Ba0.33Mn0.98Ti0.02O3']}}}}}}
        ]
        self.do_table(expected)

    def test_required_submodels_8(self):
        """
        Tests a combination of `required` parameters for submodels.
        """
        Enthalpy.absent.required = False
        Reference.enthalpy.required = False
        CurieTemperature.reference.required = False
        expected = [
            {'CurieTemperature': {'raw_value': '293', 'raw_units': '(K)', 'value': [293.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['MnO2']}}, 'reference': {'Reference': {'raw_value': '52–55', 'value': [52.0, 55.0], 'specifier': 'Ref', 'compound': {'Compound': {'names': ['MnO2']}}, 'enthalpy': {'Enthalpy': {'raw_value': '5', 'raw_units': '(kJ)', 'value': [5.0], 'units': '(10^3.0) * Joule^(1.0)', 'specifier': 'Enthalpy', 'compound': {'Compound': {'names': ['MnO2']}}}}}}}},
            {'CurieTemperature': {'raw_value': '293', 'raw_units': '(K)', 'value': [293.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['MnO2']}}, 'reference': {'Reference': {'raw_value': '56', 'value': [56.0], 'specifier': 'Ref', 'compound': {'Compound': {'names': ['MnO2']}}, 'enthalpy': {'Enthalpy': {'raw_value': '1', 'raw_units': '(kJ)', 'value': [1.0], 'units': '(10^3.0) * Joule^(1.0)', 'specifier': 'Enthalpy', 'compound': {'Compound': {'names': ['MnO2']}}}}}}}},
            {'CurieTemperature': {'raw_value': '337', 'raw_units': '(K)', 'value': [337.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['La2']}}, 'reference': {'Reference': {'raw_value': '57', 'value': [57.0], 'specifier': 'Ref', 'compound': {'Compound': {'names': ['La2']}}, 'enthalpy': {'Enthalpy': {'raw_value': '1', 'raw_units': '(kJ)', 'value': [1.0], 'units': '(10^3.0) * Joule^(1.0)', 'specifier': 'Enthalpy', 'compound': {'Compound': {'names': ['La2']}}}}}}}},
            {'CurieTemperature': {'raw_value': '292', 'raw_units': '(K)', 'value': [292.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['La0.67Ba0.33']}}, 'reference': {'Reference': {'raw_value': '26', 'value': [26.0], 'specifier': 'Ref', 'compound': {'Compound': {'names': ['La0.67Ba0.33']}}, 'enthalpy': {'Enthalpy': {'raw_value': '5', 'raw_units': '(kJ)', 'value': [5.0], 'units': '(10^3.0) * Joule^(1.0)', 'specifier': 'Enthalpy', 'compound': {'Compound': {'names': ['La0.67Ba0.33']}}}}}}}},
            {'CurieTemperature': {'raw_value': '252', 'raw_units': '(K)', 'value': [252.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['La0.67Ca0.33']}}, 'reference': {'Reference': {'raw_value': '26', 'value': [26.0], 'specifier': 'Ref', 'compound': {'Compound': {'names': ['La0.67Ca0.33']}}, 'enthalpy': {'Enthalpy': {'raw_value': '5', 'raw_units': '(kJ)', 'value': [5.0], 'units': '(10^3.0) * Joule^(1.0)', 'specifier': 'Enthalpy', 'compound': {'Compound': {'names': ['La0.67Ca0.33']}}}}}}}},
            {'CurieTemperature': {'raw_value': '312', 'raw_units': '(K)', 'value': [312.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['La0.67Sr0.33MnO3']}}, 'reference': {'Reference': {'raw_value': '58', 'value': [58.0], 'specifier': 'Ref', 'compound': {'Compound': {'names': ['La0.67Sr0.33MnO3']}}, 'enthalpy': {'Enthalpy': {'raw_value': '1.5', 'raw_units': '(kJ)', 'value': [1.5], 'units': '(10^3.0) * Joule^(1.0)', 'specifier': 'Enthalpy', 'compound': {'Compound': {'names': ['La0.67Sr0.33MnO3']}}}}}}}},
            {'CurieTemperature': {'raw_value': '321', 'raw_units': '(K)', 'value': [321.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['La0.67Sr0.33MnO3']}}, 'reference': {'Reference': {'raw_value': '58', 'value': [58.0], 'specifier': 'Ref', 'compound': {'Compound': {'names': ['La0.67Sr0.33MnO3']}}, 'enthalpy': {'Enthalpy': {'raw_value': '1.5', 'raw_units': '(kJ)', 'value': [1.5], 'units': '(10^3.0) * Joule^(1.0)', 'specifier': 'Enthalpy', 'compound': {'Compound': {'names': ['La0.67Sr0.33MnO3']}}}}}}}},
            {'CurieTemperature': {'raw_value': '309', 'raw_units': '(K)', 'value': [309.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['Ba0.33Mn0.98Ti0.02O3']}}, 'reference': {'Reference': {'raw_value': '39', 'value': [39.0], 'specifier': 'Ref', 'compound': {'Compound': {'names': ['Ba0.33Mn0.98Ti0.02O3']}}, 'enthalpy': {'Enthalpy': {'raw_value': '1', 'raw_units': '(kJ)', 'value': [1.0], 'units': '(10^3.0) * Joule^(1.0)', 'specifier': 'Enthalpy', 'compound': {'Compound': {'names': ['Ba0.33Mn0.98Ti0.02O3']}}}}}}}},
            {'CurieTemperature': {'raw_value': '309', 'raw_units': '(K)', 'value': [309.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['Ba0.33Mn0.98Ti0.02O3']}}, 'reference': {'Reference': {'raw_value': '39', 'value': [39.0], 'specifier': 'Ref', 'compound': {'Compound': {'names': ['Ba0.33Mn0.98Ti0.02O3']}}, 'enthalpy': {'Enthalpy': {'raw_value': '5', 'raw_units': '(kJ)', 'value': [5.0], 'units': '(10^3.0) * Joule^(1.0)', 'specifier': 'Enthalpy', 'compound': {'Compound': {'names': ['Ba0.33Mn0.98Ti0.02O3']}}}}}}}},
            {'CurieTemperature': {'raw_value': '286', 'raw_units': '(K)', 'value': [286.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['Ba0.33Mn0.98Ti0.02O3']}}, 'reference': {'Reference': {'raw_value': '286', 'value': [286.0], 'specifier': 'Ref', 'compound': {'Compound': {'names': ['Ba0.33Mn0.98Ti0.02O3']}}, 'enthalpy': {'Enthalpy': {'raw_value': '5', 'raw_units': '(kJ)', 'value': [5.0], 'units': '(10^3.0) * Joule^(1.0)', 'specifier': 'Enthalpy', 'compound': {'Compound': {'names': ['Ba0.33Mn0.98Ti0.02O3']}}}}}}}},
            {'CurieTemperature': {'raw_value': '286', 'raw_units': '(K)', 'value': [286.0], 'units': 'Kelvin^(1.0)', 'specifier': 'TC', 'compound': {'Compound': {'names': ['Ba0.33Mn0.98Ti0.02O3']}}, 'reference': {'Reference': {'raw_value': '286', 'value': [286.0], 'specifier': 'Ref', 'compound': {'Compound': {'names': ['Ba0.33Mn0.98Ti0.02O3']}}, 'enthalpy': {'Enthalpy': {'raw_value': '1', 'raw_units': '(kJ)', 'value': [1.0], 'units': '(10^3.0) * Joule^(1.0)', 'specifier': 'Enthalpy', 'compound': {'Compound': {'names': ['Ba0.33Mn0.98Ti0.02O3']}}}}}}}}
        ]
        self.do_table(expected)


# DEFINE A SIMPLE PV PARSER
class SimplePhotovoltaicDevice(BaseModel):
    specifier = StringType(parse_expression=Any().hide(), required=False, contextual=False)

    voc = ModelType(OpenCircuitVoltage, required=False, contextual=False)
    ff = ModelType(FillFactor, required=False, contextual=False)
    pce = ModelType(PowerConversionEfficiency, required=False, contextual=False)
    jsc = ModelType(ShortCircuitCurrentDensity, required=False, contextual=False)
    dye = ModelType(Dye, required=False, contextual=False)

    parsers = [AutoTableParserOptionalCompound(), AutoSentenceParserOptionalCompound()]

class TestTablePVCell(unittest.TestCase):
    """ Testing complex nested tables for photovoltaic tables"""

    def test_LH_column_merging(self):
        """This test ensures that the LH column in a table gets merges when appropriate"""

        table_input = [['Dye',	'Jsc (mA cm−2)', 'Voc (V)', 'FF', 'PCE'], ['DPTP', '11.11', '22.22', '33.33', '44.44'], ['N719','55.55','66.66', '77.77', '88.88']]
        table = Table(caption=Caption(''), table_data=table_input, models=[SimplePhotovoltaicDevice])

        expected_1 = {'SimplePhotovoltaicDevice': {'voc': {'OpenCircuitVoltage': {'raw_value': '22.22', 'raw_units': '(V)', 'value': [22.22], 'units': 'Volt^(1.0)', 'specifier': 'Voc'}}, 'ff': {'FillFactor': {'raw_value': '33.33', 'value': [33.33], 'specifier': 'FF'}}, 'pce': {'PowerConversionEfficiency': {'raw_value': '44.44', 'value': [44.44], 'specifier': 'PCE'}}, 'jsc': {'ShortCircuitCurrentDensity': {'raw_value': '11.11', 'raw_units': '(mAcm−2)', 'value': [11.11], 'units': '(10^1.0) * Ampere^(1.0)  Meter^(-2.0)', 'specifier': 'Jsc'}}, 'dye': {'Dye': {'specifier': 'Dye', 'raw_value': 'DPTP'}}}}
        expected_2 = {'SimplePhotovoltaicDevice': {'voc': {'OpenCircuitVoltage': {'raw_value': '66.66', 'raw_units': '(V)', 'value': [66.66], 'units': 'Volt^(1.0)', 'specifier': 'Voc'}}, 'ff': {'FillFactor': {'raw_value': '77.77', 'value': [77.77], 'specifier': 'FF'}}, 'pce': {'PowerConversionEfficiency': {'raw_value': '88.88', 'value': [88.88], 'specifier': 'PCE'}}, 'jsc': {'ShortCircuitCurrentDensity': {'raw_value': '55.55', 'raw_units': '(mAcm−2)', 'value': [55.55], 'units': '(10^1.0) * Ampere^(1.0)  Meter^(-2.0)', 'specifier': 'Jsc'}}, 'dye': {'Dye': {'specifier': 'Dye', 'raw_value': 'N719'}}}}

        self.assertEqual(expected_1, table.records[-2].serialize())
        self.assertEqual(expected_2, table.records[-1].serialize())
        
    def test_unusual_hyphen_included(self):
        
        cell_string = '7.53 sdfkljlk N719 sdfkljlk Jsc mAcm–2'
        cell = Cell(cell_string)
        parser = AutoTableParserOptionalCompound()
        parser.model = ShortCircuitCurrentDensity
        results = list(parser.parse_cell(cell))

        self.assertEqual(results[0].serialize(), {'ShortCircuitCurrentDensity': {'raw_value': '7.53', 'raw_units': 'mAcm–2', 'value': [7.53], 'units': '(10^1.0) * Ampere^(1.0)  Meter^(-2.0)', 'specifier': 'Jsc'}})

if __name__ == '__main__':
    unittest.main()
