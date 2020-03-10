# -*- coding: utf-8 -*-
"""
test_model_pvmodel
~~~~~~~~~~

Test photovoltaic cell parser.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import unittest

from chemdataextractor.model.pv_model import BaseModel, ShortCircuitCurrentDensity, OpenCircuitVoltage, FillFactor,\
    PowerConversionEfficiency, Reference, RedoxCouple, DyeLoading, CounterElectrode, Semiconductor,\
    SemiconductorThickness, SimulatedSolarLightIntensity, ActiveArea, Electrolyte, Substrate, PhotovoltaicCell,\
    ChargeTransferResistance, SeriesResistance, ExposureTime, SentenceDye

from chemdataextractor.doc.text import Sentence, Caption, Paragraph
from chemdataextractor.doc.table import Table

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


class TestPhotovoltaicCellModelTable(unittest.TestCase):

    def do_table_cell(self, cell_list, expected, model):
        logging.basicConfig(level=logging.DEBUG)
        table = Table(caption=Caption(""),
                      table_data=cell_list,
                      models=[model])
        output = []
        for record in table.records:
            output.append(record.serialize())
        self.assertCountEqual(output, expected)

    # Tests for the specfic property extraction
    def test_open_circuit_voltage_table(self):
        input = [['Dye', 'Voc (V)'], ['N719', '0.89']]
        expected = [{'OpenCircuitVoltage': {'raw_units': '(V)',
                         'raw_value': '0.89',
                         'specifier': 'Voc',
                         'units': 'Volt^(1.0)',
                         'value': [0.89]}}]

        self.do_table_cell(input, expected, OpenCircuitVoltage)

    def test_short_circuit_current_density_table(self):
        input = [['Dye', 'Jsc (mAcm-2)'], ['N719', '7.53']]
        expected = [{'ShortCircuitCurrentDensity': {'raw_units': '(mAcm-2)',
                                 'raw_value': '7.53',
                                 'specifier': 'Jsc',
                                 'units': '(10^1.0) * Ampere^(1.0)  '
                                          'Meter^(-2.0)',
                                 'value': [7.53]}}]

        self.do_table_cell(input, expected, ShortCircuitCurrentDensity)

    def test_short_circuit_current_density_table_2(self):
        """Unit extraction with a different hyphen type"""
        input = [['Dye', 'Jsc (mA cm–2)'], ['N719', '4.56']]
        expected = [{'ShortCircuitCurrentDensity': {'raw_units': '(mAcm–2)',
                                 'raw_value': '4.56',
                                 'specifier': 'Jsc',
                                 'units': '(10^1.0) * Ampere^(1.0)  '
                                          'Meter^(-2.0)',
                                 'value': [4.56]}}]

        self.do_table_cell(input, expected, ShortCircuitCurrentDensity)

    def test_power_conversion_efficiency_table(self):
        input = [['Dye', 'PCE (%)'], ['N719', '7.50']]
        expected = [{'PowerConversionEfficiency': {'raw_value': '7.50', 'raw_units': '(%)', 'value': [7.5],
                                                   'units': 'Percent^(1.0)', 'specifier': 'PCE'}}]

        self.do_table_cell(input, expected, PowerConversionEfficiency)

    def test_fill_factor_table(self):
        input = [['Dye', 'FF '], ['N719', '55']]
        expected = [{'FillFactor': {'raw_value': '55', 'value': [55.0], 'specifier': 'FF'}}]

        self.do_table_cell(input, expected, FillFactor)

    def test_redox_couple_table(self):
        input = [['Dye', 'Redox couple'], ['N719', 'I-/I3-']]
        expected = [{'RedoxCouple': {'specifier': 'Redox couple', 'raw_value': 'I- / I3-'}}]

        self.do_table_cell(input, expected, RedoxCouple)

    def test_dye_loading_table(self):
        input = [['Dye', 'Dye loading (mol cm−2)'], ['N719', '13.12×10−8 ']]
        expected = [{'DyeLoading': {'exponent': '− 8',
                 'raw_units': '(molcm−2)',
                 'raw_value': '13.12',
                 'specifier': 'Dye loading',
                 'units': '(10^4.0) * Meter^(-2.0)  Mol^(1.0)',
                 'value': [13.12]}}]

        self.do_table_cell(input, expected, DyeLoading)

    def test_reference_table(self):
        input = [['Dye', 'Ref.'], ['N719', '131']]
        expected = [{'Reference': {'raw_value': '131', 'value': [131.0], 'specifier': 'Ref'}}]

        self.do_table_cell(input, expected, Reference)

    def test_counter_electrodes_table(self):
        input = [['Dye', 'Counter electrodes'], ['N719', 'Pt3Ni']]
        expected = [{'CounterElectrode': {'specifier': 'Counter electrodes', 'raw_value': 'Pt3Ni'}}]

        self.do_table_cell(input, expected, CounterElectrode)

    def test_counter_electrodes_table_2(self):
        input = [['CEs', 'Voc'], ['CBSi3N4-1%', '0.71 ± 0.02'], ['CBSi3N4-3%', '0.74 ± 0.01']]
        expected =  [{'CounterElectrode': {'raw_value': 'CBSi3N4-1 %', 'specifier': 'CEs'}},
                     {'CounterElectrode': {'raw_value': 'CBSi3N4-3 %', 'specifier': 'CEs'}},
                     {'OpenCircuitVoltage': {'error': 0.02,
                                             'raw_value': '0.71 ± 0.02',
                                             'specifier': 'Voc',
                                             'value': [0.71]}},
                     {'OpenCircuitVoltage': {'error': 0.01,
                                             'raw_value': '0.74 ± 0.01',
                                             'specifier': 'Voc',
                                             'value': [0.74]}},
                     {'PhotovoltaicCell': {'counter_electrode': {'CounterElectrode': {'raw_value': 'CBSi3N4-1 %',
                                                                                      'specifier': 'CEs'}},
                                           'voc': {'OpenCircuitVoltage': {'error': 0.02,
                                                                          'raw_value': '0.71 ± 0.02',
                                                                          'specifier': 'Voc',
                                                                          'value': [0.71]}}}},
                     {'PhotovoltaicCell': {'counter_electrode': {'CounterElectrode': {'raw_value': 'CBSi3N4-3 %',
                                                                                      'specifier': 'CEs'}},
                                           'voc': {'OpenCircuitVoltage': {'error': 0.01,
                                                                          'raw_value': '0.74 ± 0.01',
                                                                          'specifier': 'Voc',
                                                                          'value': [0.74]}}}}]

        self.do_table_cell(input, expected, PhotovoltaicCell)

    def test_semiconductor_table(self):
        input = [['Dye', 'Semiconductor'], ['N719', 'TiO2 film, 12µm']]
        expected = [{'Semiconductor': {'specifier': 'Semiconductor', 'raw_value': 'TiO2 film , 12 µm',
                                       'thickness': {'SemiconductorThickness': {'raw_value': '12', 'raw_units': 'µm', 'value': [12.0], 'units': '(10^-6.0) * Meter^(1.0)', 'specifier': 'Semiconductor'}}}},
                    {'SemiconductorThickness': {'raw_value': '12', 'raw_units': 'µm', 'value': [12.0], 'units': '(10^-6.0) * Meter^(1.0)', 'specifier': 'Semiconductor'}}]

        self.do_table_cell(input, expected, Semiconductor)

    def test_semiconductor_table_2(self):
        input = [['Photoanode', 'Voc (V)'], ['T2/8/5 + T9/1/9', '12.3']]
        expected = [{'Semiconductor': {'specifier': 'Photoanode', 'raw_value': 'T2 / 8 / 5 + T9 / 1 / 9', 'thickness': {'SemiconductorThickness': {'raw_value': '8', 'value': [8.0], 'specifier': 'Photoanode'}}}}, {'SemiconductorThickness': {'raw_value': '8', 'value': [8.0], 'specifier': 'Photoanode'}}]

        self.do_table_cell(input, expected, Semiconductor)

    def test_semiconductor_thickness_table(self):
        input = [['Dye', 'Semiconductor'], ['N719', 'TiO2 film, 12µm']]
        expected = [{'SemiconductorThickness': {'raw_value': '12', 'raw_units': 'µm', 'value': [12.0], 'units': '(10^-6.0) * Meter^(1.0)', 'specifier': 'Semiconductor'}}]

        self.do_table_cell(input, expected, SemiconductorThickness)

    def test_solar_irradiance_table(self):
        input = [['Dye', 'Solar irradiance'], ['N719', 'AM1.5G']]
        expected = [{'SimulatedSolarLightIntensity': {'specifier': 'irradiance',
                                   'spectra': 'AM1.5G'}}]

        self.do_table_cell(input, expected, SimulatedSolarLightIntensity)

    def test_active_area_table(self):
        input = [['Dye', 'Active area (cm2)'], ['N719', '25.0']]
        expected = [{'ActiveArea': {'raw_value': '25.0', 'raw_units': '(cm2)', 'value': [25.0], 'units': '(10^-4.0) * Meter^(2.0)', 'specifier': 'Active area'}}]

        self.do_table_cell(input, expected, ActiveArea)

    def test_electrolyte_table(self):
        input = [['Dye', 'Electrolyte'], ['N719', 'example_electrolyte']]
        expected = [{'Electrolyte': {'raw_value': 'example_electrolyte', 'specifier': 'Electrolyte'}}]
        self.do_table_cell(input, expected, Electrolyte)

    def test_substrate_table(self):
        input = [['Dye', 'Substrate'], ['N719', 'FTO']]
        expected = [{'Substrate': {'raw_value': 'FTO', 'specifier': 'Substrate'}}]

        self.do_table_cell(input, expected, Substrate)

    def test_charge_transfer_resistance(self):
        input = [['Dye', 'Rct2 (Ω)'], ['N719', '5.28']]
        expected = [{'ChargeTransferResistance': {'raw_value': '5.28', 'raw_units': '(Ω)', 'value': [5.28], 'units': 'Ohm^(1.0)', 'specifier': 'Rct2'}}]

        self.do_table_cell(input, expected, ChargeTransferResistance)

    def test_series_resistance(self):
        input = [['Dye', 'Rs (Ω)'], ['N719', '27.43']]
        expected = [{'SeriesResistance': {'raw_value': '27.43', 'raw_units': '(Ω)', 'value': [27.43], 'units': 'Ohm^(1.0)', 'specifier': 'Rs'}}]

        self.do_table_cell(input, expected, SeriesResistance)

    def test_exposure_time(self):
        input = [['Dye', 'Time (h)'], ['N719', '24']]
        expected = [{'ExposureTime': {'raw_units': '(h)',
                   'raw_value': '24',
                   'specifier': 'Time',
                   'units': 'Hour^(1.0)',
                   'value': [24.0]}}]

        self.do_table_cell(input, expected, ExposureTime)

    def test_errors_table(self):
        input = [['Dye', 'JSC mAcm−2'], ['T-1', '7.47 ±0.14']]
        expected = [{'ShortCircuitCurrentDensity': {'error': 0.14,
                                 'raw_units': 'mAcm−2',
                                 'raw_value': '7.47 ± 0.14',
                                 'specifier': 'JSC',
                                 'units': '(10^1.0) * Ampere^(1.0)  '
                                          'Meter^(-2.0)',
                                 'value': [7.47]}}]

        self.do_table_cell(input, expected, ShortCircuitCurrentDensity)


class TestPhotovoltaicCellText(unittest.TestCase):
    """ Tests to check that the PV parsers work on sentences when required.
        This is geared towards properties that are likely to be contextual.
    """

    def do_sentence(self, input, expected, model):
        sentence = Sentence(input)
        sentence.models = [model]
        output = []
        for record in sentence.records:
            output.append(record.serialize())
        self.assertEqual(output, expected)

    def do_paragraph(self, input, expected, model):
        paragraph = Paragraph(input)
        paragraph.models = [model]
        output = []
        for record in paragraph.records:
            output.append(record.serialize())
        self.assertEqual(output, expected)


    def test_solar_irradiance_sentence(self):
        input = 'The measurements were conducted at a simulated solar light intensity of 100 mW cm−2 (AM 1.5G) unless specified'
        expected = [{'SimulatedSolarLightIntensity': {'raw_value': '100', 'raw_units': 'mWcm−2(', 'value': [100.0],
                                                      'units': '(10^1.0) * Meter^(-2.0)  Watt^(1.0)',
                                                      'specifier': 'light intensity of', 'spectra': 'AM 1.5G'}}]

        self.do_sentence(input, expected, SimulatedSolarLightIntensity)

    def test_solar_irradiance_sentence_2(self):
        input = 'Photovoltaic parameters of various SD/ERD systems measured under simulated AM 1.5G irradiance (100 mW cm−2)'
        expected = [{'SimulatedSolarLightIntensity': {'raw_value': '100', 'raw_units': 'mWcm−2)', 'value': [100.0],
                                                      'units': '(10^1.0) * Meter^(-2.0)  Watt^(1.0)',
                                                      'specifier': 'irradiance', 'spectra': 'AM 1.5G'}}]

        self.do_sentence(input, expected, SimulatedSolarLightIntensity)

    def test_solar_irradiance_sentence_3(self):
        input = ' an irradiance of 100 mW cm−2 simulated AM1.5G sunlight'
        expected = [{'SimulatedSolarLightIntensity': {'raw_units': 'mWcm−2',
                                   'raw_value': '100',
                                   'specifier': 'irradiance',
                                   'spectra': 'AM1.5G',
                                   'units': '(10^1.0) * Meter^(-2.0)  '
                                            'Watt^(1.0)',
                                   'value': [100.0]}}]

        self.do_sentence(input, expected, SimulatedSolarLightIntensity)

    def test_semiconductor_thickness_sentence(self):
        input = '8 μm thick ZnO anodes'
        expected = [{'SemiconductorThickness': {'raw_value': '8', 'raw_units': 'μm', 'value': [8.0], 'units': '(10^-6.0) * Meter^(1.0)', 'specifier': 'anodes'}}]

        self.do_sentence(input, expected, SemiconductorThickness)

    def test_semiconductor_sentence(self):
        input = 'Photovoltaic properties of D149-sensitized, YD2-o-C8-TBA-sensitized and co-sensitized ZnO DSSCs fabricated using 8 μm thick ZnO anodes with light-scattering layers.'
        expected = [{'Semiconductor': {'specifier': 'anodes', 'raw_value': 'ZnO',
                    'thickness': {'SemiconductorThickness': {'raw_value': '8', 'raw_units': 'μm', 'value': [8.0], 'units': '(10^-6.0) * Meter^(1.0)', 'specifier': 'anodes'}}}},
                    {'SemiconductorThickness': {'raw_value': '8', 'raw_units': 'μm', 'value': [8.0], 'units': '(10^-6.0) * Meter^(1.0)', 'specifier': 'anodes'}}]

        self.do_sentence(input, expected, Semiconductor)

    def test_sentence_dye_sentence(self):
        input = "Organic sensitizer of 3-{6-{4-[bis(2′,4′-dihexyloxybiphenyl-4-yl)amino-]phenyl}-4,4-dihexyl-cyclopenta-[2,1-b:3,4-b']dithiophene-2-yl}-2-cyanoacrylic acid (Y123) was purchased from Dyenamo and used without purification."
        expected = [{'SentenceDye': {'raw_value': 'Y123', 'specifier': 'sensitizer'}}]

        self.do_sentence(input, expected, SentenceDye)

    def test_sentence_dye_sentence_2(self):
        input = "The experiment used a dye that we are not mentioning here, and used a TiO2 substrate."
        expected = [{'SentenceDye': {'specifier': 'dye'}}]

        self.do_sentence(input, expected, SentenceDye)

