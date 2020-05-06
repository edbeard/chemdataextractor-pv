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
    ChargeTransferResistance, SeriesResistance, ExposureTime, SentenceDye, SentenceDyeLoading, Dye, Perovskite, \
    PerovskiteSolarCell, HoleTransportLayer, ElectronTransportLayer

from chemdataextractor.doc.text import Sentence, Caption, Paragraph
from chemdataextractor.doc.table import Table

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


class TestPhotovoltaicCellModelTable(unittest.TestCase):

    def do_table_cell(self, cell_list, expected, model):
        self.maxDiff = None
        logging.basicConfig(level=logging.DEBUG)
        table = Table(caption=Caption(""),
                      table_data=cell_list,
                      models=[model])
        output = []
        for record in table.records:
            output.append(record.serialize())
        self.assertCountEqual(output, expected)

    def test_adsorbed_dye_not_identified_table(self):
        """ Check that cases containing the units for dye loading in the heading are ignored."""
        input = [['Dye', 'Adsorbed dye (10−7 mol cm−2)'], ['N719', '2.601']]
        expected = [{'Dye': {'specifier': 'Dye', 'raw_value': 'N719'}}]
        self.do_table_cell(input, expected, Dye)

    def test_sensitizers_specifier_dye(self):
        """ Check that cases containing the units for dye loading in the heading are ignored."""
        input = [['Sensitizers', 'Adsorbed dye (10−7 mol cm−2)'], ['N719', '2.601']]
        expected = [{'Dye': {'specifier': 'Sensitizers', 'raw_value': 'N719'}}]
        self.do_table_cell(input, expected, Dye)

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
        expected = [{'RedoxCouple': {'specifier': 'Redox couple', 'raw_value': 'I-/I3-'}}]

        self.do_table_cell(input, expected, RedoxCouple)

    def test_dye_loading_table(self):
        input = [['Dye', 'Dye loading (mol cm−2)'], ['N719', '13.12×10−8 ']]
        expected = [{'DyeLoading': {'exponent': [-8.0],
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
        expected = [{'Semiconductor': {'specifier': 'Photoanode', 'raw_value': 'T2 / 8 / 5 + T9 / 1 / 9'}}]

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

    def test_solar_irradiance_sol(self):
        input = [['Dye', 'Illumination (Sun)'], ['N719', '1']]
        expected = [{'SimulatedSolarLightIntensity': {'raw_value': '1', 'raw_units': '(Sun)', 'value': [1.0], 'units': 'Sun^(1.0)', 'specifier': 'Illumination'}}]

        self.do_table_cell(input, expected, SimulatedSolarLightIntensity)

    def test_solar_irradiance_sol_2(self):
        input = [['Dye', 'Illumination (Sol)'], ['N719', '1/8']]
        expected = [{'SimulatedSolarLightIntensity': {'raw_value': '1/8', 'raw_units': '(Sol)', 'value': [0.125], 'units': 'Sun^(1.0)', 'specifier': 'Illumination'}}]

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

    def test_dye_omitted_by_units(self):
        input = [['Counter Electrode', 'Adsorbed dye (108 /cm2)'], ['Pt', '0.86']]
        expected = []
        self.do_table_cell(input, expected, Dye)


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
        print(output)
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

    def test_solar_irradiance_sentence_4(self):
        input = 'Detailed photovoltaic parameters of solar cells based on different TiO2 photoelectrodes under AM 1.5 illumination (100 mW cm−2).'
        expected = [{'SimulatedSolarLightIntensity': {'raw_units': 'mWcm−2)',
                                   'raw_value': '100',
                                   'specifier': 'illumination',
                                   'spectra': 'AM 1.5',
                                   'units': '(10^1.0) * Meter^(-2.0)  '
                                            'Watt^(1.0)',
                                   'value': [100.0]}}]

        self.do_sentence(input, expected, SimulatedSolarLightIntensity)

    def test_solar_irradiance_sentence_5(self):
        input = ' The efficiency of the solar cells fabricated is determined from the photocurrent versus voltage (I–V) characteristics measured by using solar simulator under 1:5 AM (ORIEL Sol1A). '
        expected = [{'SimulatedSolarLightIntensity': {'specifier': 'solar',
                                   'spectra': '1 : 5 AM'}}]
        self.do_sentence(input, expected, SimulatedSolarLightIntensity)

    def test_semiconductor_thickness_sentence(self):
        input = '8 μm thick ZnO anodes'
        expected = [{'SemiconductorThickness': {'raw_value': '8', 'raw_units': 'μm', 'value': [8.0], 'units': '(10^-6.0) * Meter^(1.0)', 'specifier': 'thick'}}]

        self.do_sentence(input, expected, SemiconductorThickness)

    def test_semiconductor_sentence(self):
        input = 'Photovoltaic properties of D149-sensitized, YD2-o-C8-TBA-sensitized and co-sensitized ZnO DSSCs fabricated using 8 μm thick ZnO anodes with light-scattering layers.'
        expected = [{'Semiconductor': {'specifier': 'anodes', 'raw_value': 'ZnO',
                    'thickness': {'SemiconductorThickness': {'raw_value': '8', 'raw_units': 'μm', 'value': [8.0], 'units': '(10^-6.0) * Meter^(1.0)', 'specifier': 'thick'}}}},
                    {'SemiconductorThickness': {'raw_value': '8', 'raw_units': 'μm', 'value': [8.0], 'units': '(10^-6.0) * Meter^(1.0)', 'specifier': 'thick'}}]

        self.do_sentence(input, expected, Semiconductor)

    def test_sentence_dye_sentence(self):
        input = "Organic sensitizer of 3-{6-{4-[bis(2′,4′-dihexyloxybiphenyl-4-yl)amino-]phenyl}-4,4-dihexyl-cyclopenta-[2,1-b:3,4-b']dithiophene-2-yl}-2-cyanoacrylic acid (Y123) was purchased from Dyenamo and used without purification."
        expected = [{'SentenceDye': {'raw_value': 'Y123', 'specifier': 'sensitizer'}}]

        self.do_sentence(input, expected, SentenceDye)

    def test_sentence_dye_sentence_2(self):
        input = "The experiment used a dye that we are not mentioning here, and used a TiO2 substrate."
        expected = [{'SentenceDye': {'specifier': 'dye'}}]

        self.do_sentence(input, expected, SentenceDye)

    def test_dye_loading_sentence(self):
        input = 'with a dye-loading capacity of two working electrodes: 2.601×10−7 mol cm−2.'
        expected = [{'SentenceDyeLoading': {'exponent': [-7.0],
                         'raw_units': 'molcm−2',
                         'raw_value': '2.601',
                         'specifier': 'loading',
                         'units': '(10^4.0) * Meter^(-2.0)  Mol^(1.0)',
                         'value': [2.601]}}]

        self.do_sentence(input, expected, SentenceDyeLoading)

    def test_redox_couple_sentence(self):
        input = ' Obviously, the Epp for two electrodes is almost identical, while the peak current density of the NGF electrode is a bit higher than that of the Pt electrode, indicating that NGFs possess superior electrocatalytic activity for the regeneration of the I−/I3− redox couple.'
        expected = [{'RedoxCouple': {'raw_value': 'I−/I3−', 'specifier': 'redox couple'}}]

        self.do_sentence(input, expected, RedoxCouple)

    def test_redox_couple_sentence2(self):
        input = 'The peak to peak voltage separation (Epp) of reaction (1) corresponds to the electrocatalytic activity of the CEs for I−/I3− redox reactions, with the standard electrochemical rate constant inversely correlated.'
        expected = [{'RedoxCouple': {'raw_value': 'I−/I3−', 'specifier': 'redox reactions'}}]

        self.do_sentence(input, expected, RedoxCouple)

    def test_redox_couple_sentence2(self):
        input = 'Cyclic voltammetry (CV) for I3−/I− redox couple was carried out in a three-electrode system in an argon-purged acetonitrile solution which contained 0.1 M LiClO4, 10 mM LiI, and 1 mM I2 at a scan rate of 10 mV s−1 using a electrochemical analyzer (CHI630, Chenhua, Shanghai)'
        expected = [{'RedoxCouple': {'raw_value': 'I3−/I−', 'specifier': 'redox couple'}}]

        self.do_sentence(input, expected, RedoxCouple)


class TestPerovskiteCellTable(unittest.TestCase):

    def do_table_cell(self, cell_list, expected, model):
        self.maxDiff = None
        logging.basicConfig(level=logging.DEBUG)
        table = Table(caption=Caption(""),
                      table_data=cell_list,
                      models=[model])
        output = []
        for record in table.records:
            output.append(record.serialize())
        self.assertCountEqual(output, expected)

    # Tests for the specfic property extraction
    def test_simple_perovskite_sc_table(self):
        input = [['counter electrode', 'Voc (V)'], ['Ag', '0.89']]
        expected = [{'OpenCircuitVoltage': {'raw_units': '(V)',
                         'raw_value': '0.89',
                         'specifier': 'Voc',
                         'units': 'Volt^(1.0)',
                         'value': [0.89]}},
                    {'CounterElectrode': {'specifier': 'counter electrode', 'raw_value': 'Ag'}},
                    {'PerovskiteSolarCell': {'voc': {'OpenCircuitVoltage': {'raw_value': '0.89', 'raw_units': '(V)', 'value': [0.89], 'units': 'Volt^(1.0)', 'specifier': 'Voc'}}, 'counter_electrode': {'CounterElectrode': {'specifier': 'counter electrode', 'raw_value': 'Ag'}}}}]

        self.do_table_cell(input, expected, PerovskiteSolarCell)

    def test_simple_perovskite_table(self):
        input = [['perovskite', 'Voc (V)'], ['CH3NH3PbI3', '0.89']]
        expected = [{'Perovskite': {'specifier': 'perovskite', 'raw_value': 'CH3NH3PbI3'}}]
        self.do_table_cell(input, expected, Perovskite)

    def test_hole_transport_material_table(self):
        input = [['HTM', 'Voc (V)'], ['Spiro-OMeTAD', '0.89']]
        expected = [{'HoleTransportLayer': {'specifier': 'HTM', 'raw_value': 'Spiro - OMeTAD'}}]
        self.do_table_cell(input, expected, HoleTransportLayer)

    def test_electron_transporting_material_table(self):
        input = [['HTM', 'Voc (V)'], ['Spiro-OMeTAD', '0.89']]
        expected = [{'HoleTransportLayer': {'specifier': 'HTM', 'raw_value': 'Spiro - OMeTAD'}}]
        self.do_table_cell(input, expected, HoleTransportLayer)


class TestPerovskiteCellSentence(unittest.TestCase):

    def do_sentence(self, input, expected, model):
        sentence = Sentence(input)
        sentence.models = [model]
        output = []
        for record in sentence.records:
            output.append(record.serialize())
        self.assertEqual(expected, output)

    def test_hole_transport_layer_sentence_1(self):
        text = 'A HTM of spiro-OMeTAD was used.'
        expected = [{'HoleTransportLayer': {'raw_value': 'spiro - OMeTAD', 'specifier': 'HTM'}}]
        self.do_sentence(text, expected, HoleTransportLayer)

    def test_hole_transport_layer_sentence_2(self):
        text = 'A HTL of spiro-OMeTAD was used.'
        expected = [{'HoleTransportLayer': {'raw_value': 'spiro - OMeTAD', 'specifier': 'HTL'}}]
        self.do_sentence(text, expected, HoleTransportLayer)

    def test_hole_transport_layer_sentence_3(self):
        text = 'Summary of photovoltaic parameters of the fully-vacuum-processed perovskite solar cells using 5.5 nm thick C60 ESLs, 370 nm thick CH3NH3PbI3 films and CuPc HSLs with different thicknesses measured under the reverse voltage scanning'
        expected = [{'HoleTransportLayer': {'raw_value': 'CuPc', 'specifier': 'HSLs'}}]
        self.do_sentence(text, expected, HoleTransportLayer)

    def test_electron_transport_layer_sentence(self):
        text = 'Device parameters for MAPbI3 solar cells prepared on an identical TiO2 ETL and capped with a spiro-MeOTAD HTL.'
        expected = [{'ElectronTransportLayer': {'raw_value': 'TiO2', 'specifier': 'ETL'}}]
        self.do_sentence(text, expected, ElectronTransportLayer)


    def test_active_area_and_counter_electrode(self):
        text = 'The active area of the cells defined by the Au electrodes were 0.08 cm2. '
        expected = [{'ActiveArea': {'raw_units': 'cm2',
                 'raw_value': '0.08',
                 'specifier': 'active area',
                 'units': '(10^-4.0) * Meter^(2.0)',
                 'value': [0.08]}},
        {'CounterElectrode': {'raw_value': 'Au', 'specifier': 'electrodes'}}]
        sentence = Sentence(text)
        sentence.models = [ActiveArea, CounterElectrode]
        output = []
        for record in sentence.records:
            output.append(record.serialize())
        self.assertEqual(output, expected)


