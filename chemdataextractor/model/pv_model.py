"""
Model classes for properties related to a photovoltaic device

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import six
import copy

import logging
import re

from .base import BaseModel, StringType, ModelType, ListType
from .units.substance_amount_density import AmountOfSubstanceDensityModel
from .units.area import AreaModel
from .units.current import ElectricalCurrentModel
from .units.current_density import CurrentDensityModel
from .units.electric_potential import ElectricPotentialModel
from .units.irradiance import IrradianceModel
from .units.length import LengthModel
from .units.power import PowerModel
from .units.ratio import RatioModel
from .units.resistance import ResistanceModel
from .units.specific_resistance import SpecificResistanceModel
from .units.time import TimeModel
from ..parse.elements import R, I, Optional, W, Any, Start, SkipTo, Not
from ..parse.actions import join, merge
from ..parse.cem import strict_chemical_label

from ..model.units.quantity_model import DimensionlessModel
from ..parse.auto import AutoTableParserOptionalCompound, AutoSentenceParserOptionalCompound

log = logging.getLogger(__name__)

hyphens = R('[-‐‑⁃‒–—―]')

# Models for Photovoltaic Properties
common_substrates = (
    W('FTO') | (I('flourine') + Optional(I('doped')) + I('tin') + I('oxide')) |
    W('ITO') | (I('indium') + Optional(I('doped')) + I('tin') + I('oxide')) |
    I('glass') |
    W('NiO') | (I('nickel') + I('oxide'))
).add_action(join)

common_spectra = (
     (Optional(I('AM')) + (
        I('1.5G') |
        I('1.5') |
        (W('1') + W(':') + W('5') + Optional(W('G')) )
     )  + Optional(I('AM')) ) |
    I('AM1.5G') |
    I('AM1.5')
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
    I('I-') + W('/') + I('I3-') |
    R('I[−−-]') + W('/') + R('I3[−−-]') |
    W('T2') + W('/') + R('T[−−-]') |
    R('I3[−−-]') + W('/') + R('I[−−-]') |
    R('T[−−-]') + W('/') + W('T2') |
    I('disulfide') + W('/') + I('thiolate') |
    I('thiolate') + W('/') + I('disulfide')  |
    I('triiodide') + W('/') + I('iodide') |
    I('iodide') + W('/') + I('triiodide')
).add_action(merge)

common_counter_electrodes = (
    I('gold') | W('Ag') |  # gold
    I('silver') | W('Au') | # silver
    I('platinum') | W('Pt') # platinum
)

not_dyes = common_substrates | common_spectra | common_semiconductors | common_redox_couples

common_dyes = (
    I("Squarylium dye III") |
    I("1,3-Bis[4-(dimethylamino)phenyl]-2,4-dihydroxycyclobutenediylium dihydroxide, bis(inner salt)") |
    I("149063") |
    I("D358") |
    I("5-[3-(Carboxymethyl)-5-[[4-[4-(2,2-diphenylethenyl)phenyl]-1,2,3,3a,4,8b-hexahydrocyclopent[b]indol-7-yl]methylene]-4-oxo-2-thiazoli dinylidene]-4-oxo-2-thioxo-3-thiazolidinedodecanoic acid") |
    I("YD2") |
    I("DN-F12") |
    I("YD-2") |
    I("Zinc(II) 5,15-Bis(3,5-di-tert-butylphenyl)-10-(bis(4-hexylphenyl)amino)-20-(4-carboxyphenylethynyl)porphyrin") |
    I("DN-FP02") |
    I("PB6") |
    I("4,4'-((4-(5-(2-(2,6-diisopropylphenyl)-1,3-dioxo-2,3-dihydro-1H-benzo[10,5]anthra[2,1,9-def]isoquinolin-8-yl)thiophen-2-yl)phenyl)azanediyl)dibenzoic acid") |
    I("DN-FP01") |
    I("P1") |
    I("4-(Bis-{4-[5-(2,2-dicyano-vinyl)-thiophene-2-yl]-phenyl}-amino)-benzoic acid") |
    I("Ruthenizer 520-DN") |
    I("Z907") |
    I("Z-907") |
    I("520-DN") |
    I("cis-diisothiocyanato-(2,2’-bipyridyl-4,4’-dicarboxylic acid)-(2,2’-bipyridyl-4,4’-dinonyl) ruthenium(II)") |
    I("Sensidizer BA504") |
    I("BA504") |
    I("2-(9-(4-(bis(9,9-dimethyl-9H-fluoren-2-yl)amino)phe nyl)-1,3-dioxo-1H-benzo[5,10]anthra[2,1,9-def]isoqui nolin-2(3H,9H,13aH)-yl)acetic acid") |
    I("DN-F04") |
    I("dyenamo orange") |
    I("D35") |
    I("(E)-3-(5-(4-(bis(2',4'-dibutoxy-[1,1'-biphenyl]-4-yl)amino)phenyl)thiophen-2-yl)-2-cyanoacrylic acid") |
    I("D131") |
    I("2-Cyano-3-[4-[4-(2,2-diphenylethenyl)phenyl]-1,2,3,3a,4,8b-hexahydrocyclopent[b]indol-7-yl]-2-propenoic acid") |
    I("DN-F17") |
    I("R6") |
    I("4-(7-((15-(Bis(4-(hexyloxy)phenyl)amino)-9,9,19,19-tetrakis(4-hexylphenyl)-9,19-dihydrobenzo[1',10']phenanthro[3',4':4,5]thieno[3,2-b]benzo[1,10]phenanthro[3,4-d]thiophen-5-yl)ethynyl)benzo[c][1,2,5]thiadiazol-4-yl)benzoic acid") |
    I("DN-F01") |
    I("dyenamo yellow") |
    I("L0") |
    I("4-(diphenylamino)phenylcyanoacrylic acid") |
    I("D149") |
    I("5-[[4-[4-(2,2-Diphenylethenyl)phenyl]-1,2,3-3a,4,8b-hexahydrocyclopent[b]indol-7-yl]methylene]-2-(3-ethyl-4-oxo-2-thioxo-5-thiazolidinylidene)-4-oxo-3-thiazolidineacetic acidindoline dye D149") |
    I("purple dye") |
    I("DN-F03") |
    I("D5") |
    I("L2") |
    I("3-(5-(4-(diphenylamino)styryl)thiophen-2-yl)-2-cyanoacrylic acid") |
    I("DN-FR02") |
    I("B11") |
    I("CYC-B11") |
    I("Ruthenate(2-), [[2,2´-bipyridine]-4,4´-dicarboxylato(2-)-κN1,κN1´][4,4´-bis[5´-(hexylthio)[2,2´-bithiophen]-5-yl]-2,2´-bipyridine-κN1,κN1´]bis(thiocyanato-κN)-, hydrogen (1:2), (OC-6-32)-") |
    I("Merocyanine 540") |
    I("3(2H)-Benzoxazolepropanesulfonic acid, 2-[4-(1,3-dibutyltetrahydro-4,6-dioxo-2-thioxo-5(2H)-pyrimidinylidene)-2-butenylidene]-, sodium salt") |
    I("coumarin 6") |
    I("coumarin-6") |
    I("3-(2-Benzothiazolyl)-N,N-diethylumbelliferylamine") |
    I("3-(2-Benzothiazolyl)-7-(diethylamino)coumarin") |
    I("DN-F18") |
    I("WS-72") |
    I("(E)-3-(6-(8-(4-(bis(2',4'-bis(hexyloxy)-[1,1'-biphenyl]-4-yl)amino)phenyl)-2,3-bis(4-(hexyloxy)phenyl)quinoxalin-5-yl)-4,4-dihexyl-4H-cyclopenta[2,1-b:3,4-b']dithiophen-2-yl)-2-cyanoacrylic acid") |
    I("DN-F21") |
    I("SC-4") |
    I("4-(7-(5'-(4-(bis(4-(hexyloxy)phenyl)amino)phenyl)-3,3'-dihexyl-[2,2'-bithiophen]-5-yl)benzo[c][1,2,5]thiadiazol-4-yl)benzoic acid") |
    I("D205") |
    I("5-[[4-[4-(2,2-Diphenylethenyl)phenyl]-1,2,3,3a,4,8b-hexahydrocyclopent[b]indol-7-yl]methylene]-2-(3-octyl-4-oxo-2-thioxo-5-thiazolidinylidene)-4-oxo-3-thiazolidineacetic acid") |
    I("indoline dye D205") |
    I("purple dye") |
    I("DN-F05M") |
    I("D51") |
    I("(E)-3-(6-(4-(bis(2',4'-dimethoxy-[1,1'-biphenyl]-4-yl)amino)phenyl)-4,4-dihexyl-4H-cyclopenta[2,1-b:3,4-b']dithiophen-2-yl)-2-cyanoacrylic acid") |
    I("Ruthenizer 620-1H3TBA") |
    I("620-1H3TBA") |
    I("N749") |
    I("triisothiocyanato-(2,2’:6’,6”-terpyridyl-4,4’,4”-tricarboxylato) ruthenium(II) tris(tetra-butylammonium)Ruthenium 620") |
    I("Greatcell Solar") |
    I("DPP13") |
    I("DN-F11") |
    I("(E)-3-(5-(4-(4-(5-(4-(bis(4-(hexyloxy)phenyl)amino)phenyl)thiophen-2-yl)-2,5-bis(2-ethylhexyl)-3,6-dioxo-2,3,5,6-tetrahydropyrrolo[3,4-c]pyrrol-1-yl)phenyl)furan-2-yl)-2-cyanoacrylic acid") |
    I("D102") |
    I("(5-{4-[4-(2,2-diphenyl-vinyl)phenyl]-1,2,3,3a,4,8b-hexahydrocyclopenta[b]indol-7-ylmethylene}-4-oxo-2-thioxo-thiazolidin-3-yl)acetic acid") |
    I("DN-F19") |
    I("C218") |
    I("(E)-3-(6-(4-(bis(4-(hexyloxy)phenyl)amino)phenyl)-4,4-dihexyl-4H-cyclopenta[2,1-b:3,4-b']dithiophen-2-yl)-2-cyanoacrylic acid") |
    I("K19") |
    I("Ru(4,4-dicarboxylic acid-2,2′-bipyridine)(4,4′-bis(p-hexyloxystyryl)-2,2-bipyridine)(NCS)2") |
    I("DN-F16") |
    I("XY1") |
    I("(E)-3-(4-(6-(7-(4-(bis(2',4'-bis((2-ethylhexyl)oxy)-[1,1'-biphenyl]-4-yl)amino)phenyl)benzo[c][1,2,5]thiadiazol-4-yl)-4,4-bis(2-ethylhexyl)-4H-cyclopenta[2,1-b:3,4-b']dithiophen-2-yl)phenyl)-2-cyanoacrylic acid") |
    I("DN-FR03") |
    I("N719") |
    I("N-719") |
    I("black dye") |
    I("N719 black dye") |
    I("1-Butanaminium, N,N,N-tributyl-, hydrogen (OC-6-32)-[[2,2´:6´,2´´-terpyridine]-4,4´,4´´-tricarboxylato(3-)-κN1,κN1´,κN1´´]tris(thiocyanato-κN)ruthenate(4-) (2:2:1)") |
    I("Di-tetrabutylammonium cis-bis(isothiocyanato)bis(2,2′-bipyridyl-4,4′-dicarboxylato)ruthenium(II)") |
    I("Ruthenium(2+) N,N,N-tributyl-1-butanaminium 4'-carboxy-2,2'-bipyridine-4-carboxylate (thioxomethylene)azanide (1:2:2:2)") |
    I("Ruthenium(2+)-N,N,N-tributyl-1-butanaminium-4'-carboxy-2,2'-bipyridin-4-carboxylat-(thioxomethylen)azanid (1:2:2:2)") |
    I("Ruthenizer 535-bisTBA") |
    I("cis-diisothiocyanato-bis(2,2’-bipyridyl-4,4’-dicarboxylato) ruthenium(II) bis(tetrabutylammonium)") |
    I("coumarin 102") |
    I("coumarin-102") |
    I("coumarin 480") |
    I("2,3,6,7-Tetrahydro-9-methyl-1H,5H-quinolizino(9,1-gh)coumarin") |
    I("8-Methyl-2,3,5,6-tetrahydro-1H,4H-11-oxa-3a-aza-benzo(de)anthracen-10-one") |
    I("DN-F05") |
    I("dyenamo red") |
    I("D35CPDT") |
    I("LEG4") |
    I("3-{6-{4-[bis(2',4'-dibutyloxybiphenyl-4-yl)amino-]phenyl}-4,4-dihexyl-cyclopenta-[2,1-b:3,4-b']dithiophene-2-yl}-2-cyanoacrylic acid") |
    I("DN-FR01") |
    I("K77") |
    I("Ru(2,2´–bipyridine-4,4´-dicarboxylic acid)(4,4´-bis(2-(4-tert-butyloxyphenyl)ethenyl)-2,2´–bipyridine) (NCS)2") |
    I("Ruthenizer 505") |
    I("cis-dicyano-bis(2,2’-bipyridyl-4,4’-dicarboxylic acid) ruthenium(II)") |
    I("DN-FR04") |
    I("C101") |
    I("C-101Ruthenate(2-), [[2,2´-bipyridine]-4,4´-dicarboxylato(2-)-κN1,κN1´][4,4´-bis(5-hexyl-2-thienyl)-2,2´-bipyridine-κN1,κN1´]bis(thiocyanato-κN)-, hydrogen (1:2), (OC-6-32)-") |
    I("coumarin 30") |
    I("coumarin-30") |
    I("coumarin 515") |
    I("3-(2-N-Methylbenzimidazolyl)-7-N,N-diethylaminocoumarin") |
    I("Ruthenizer 535-4TBA") |
    I("N712") |
    I("535-4TBA") |
    I("cis-diisothiocyanato-bis(2,2’-bipyridyl-4,4’-dicarboxylato) ruthenium(II) tetrakis(tetrabutylammonium)") |
    I("DN-F10M") |
    I("Dyenamo Blue 2016") |
    I("(E)-3-(5-(4-(4-(5-(4-(bis(2',4'-dibutoxy-[1,1'-biphenyl]-4-yl)amino)phenyl)thiophen-2-yl)-2,5-dioctyl-3,6-dioxo-2,3,5,6-tetrahydropyrrolo[3,4-c]pyrrol-1-yl)phenyl)furan-2-yl)-2-cyanoacrylic acid") |
    I("DN-F16B") |
    I("XY1b") |
    I("(E)-3-(4-(6-(7-(4-(bis(2',4'-dibutoxy-[1,1'-biphenyl]-4-yl)amino)phenyl)benzo[c][1,2,5]thiadiazol-4-yl)-4,4-bis(2-ethylhexyl)-4H-cyclopenta[2,1-b:3,4-b']dithiophen-2-yl)phenyl)-2-cyanoacrylic acid") |
    I("dyenamo blue") |
    I("DN-F10") |
    I("(E)-3-(5-(4-(4-(5-(4-(bis(2',4'-dibutoxy-[1,1'-biphenyl]-4-yl)amino)phenyl)thiophen-2-yl)-2,5-bis(2-ethylhexyl)-3,6-dioxo-2,3,5,6-tetrahydropyrrolo[3,4-c]pyrrol-1-yl)phenyl)furan-2-yl)-2-cyanoacrylic acid") |
    I("dyenamo mareel blue") |
    I("DN-F14") |
    I("VG1-C8") |
    I("(E)-4-((5-carboxy-3,3-dimethyl-1-octyl-3H-indol-1-ium-2-yl)methylene)-2-(((E)-5-carboxy-3,3-dimethyl-1-octylindolin-2-ylidene)methyl)-3-oxocyclobut-1-en-1-olate") |
    I("DN-F05Y") |
    I("Y123") |
    I("3-{6-{4-[bis(2',4'-dihexyloxybiphenyl-4-yl)amino-]phenyl}-4,4-dihexyl-cyclopenta-[2,1-b:3,4-b']dithiphene-2-yl}-2-cyanoacrylic acid") |
    I("DN-F13") |
    I("dyenamo cloudberry orange") |
    I("(E)-3-(4-(bis(2',4'-dibutoxy-[1,1'-biphenyl]-4-yl)amino)phenyl)-2-cyanoacrylic acid") |
    I("DN-F08") |
    I("JF419") |
    I("(E)-3-(6-(4-(bis(5,7-bis(hexyloxy)-9,9-dimethyl-9H-fluoren-2-yl)amino)phenyl)-4,4-dihexyl-4H-cyclopenta[2,1-b:3,4-b']dithiophen-2-yl)-2-cyanoacrylic acid") |
    I("DN-F15") |
    I("dyenamo transparent green") |
    I("HSQ4") |
    I("(3Z,4Z)-4-((5-carboxy-3,3-dimethyl-1-octyl-3H-indol-1-ium-2-yl)methylene)-2-(((E)-5-carboxy-3,3-dimethyl-1-octylindolin-2-ylidene)methyl)-3-(1-cyano-2-ethoxy-2-oxoethylidene)cyclobut-1-en-1-olate") |
    I("DN-F20") |
    I("C268") |
    I("4-((7-(6-(4-(bis(4-(hexyloxy)phenyl)amino)phenyl)-4,4-dihexyl-4H-cyclopenta[2,1-b:3,4-b']dithiophen-2-yl)benzo[c][1,2,5]thiadiazol-4-yl)ethynyl)benzoic acid") |
    I("Sensidizer RK1") |
    I("RK1") |
    I("2-cyano-3-(4-(7-(5-(4- (diphenylamino)phenyl)-4- octylthiophen-2-yl)benzo[c][1,2,5] thiadiazol-4-yl)phenyl) acrylic acid") |
    I("C106") |
    I("2-(4-Carboxypyridin-2-yl)pyridine-4-carboxylic acid;4-(5-hexylsulfanylthiophen-2-yl)-2-[4-(5-hexylsulfanylthiophen-2-yl)pyridin-2-yl]pyridine;ruthenium(2+);diisothiocyanate") |
    I("DN-F04M") |
    I("D45") |
    I("(E)-3-(5-(4-(bis(2',4'-dimethoxy-[1,1'-biphenyl]-4-yl)amino)phenyl)thiophen-2-yl)-2-cyanoacrylic acid") |
    I("Sensidizer BA741") |
    I("BA741") |
    I("2-(6-(5'-(4-(bis(9,9-dimethyl-9H-fluoren-2-yl)amino) phenyl)-[2,2'-bithiophen]-5-yl)-1,3-dioxo-1H-benzo[d e]isoquinolin-2(3H)-yl)acetic acid ") |
    I("Sensidizer SQ2") |
    I("SQ2") |
    I("5-carboxy-2-[[3-[(2,3-dihydro-1,1-dimethyl-3-ethyl-1H-benzo[e]indol-2-ylidene)methyl]-2-hydroxy-4-oxo-2-cyclobuten-1-ylidene]methyl]-3,3-dimethyl-1-octyl-3H-indolium") |
    I("DN-FI07") |
    I("MK245") |
    I("3-(2-((E)-2-((E)-3-((Z)-2-(3-(2-carboxyethyl)-1,1-dimethyl-1,3-dihydro-2H-benzo[e]indol-2-ylidene)ethylidene)-2-chlorocyclohex-1-en-1-yl)vinyl)-1,1-dimethyl-1H-benzo[e]indol-3-ium-3-yl)propanoate") |
    I("Ruthenizer 535") |
    I("N3") |
    I("N-3cis-diisothiocyanato-bis(2,2’-bipyridyl-4,4’-dicarboxylic acid) ruthenium(II)") |
    I("coumarin 153") |
    I("coumarin-153") |
    I("2,3,6,7-Tetrahydro-9-(trifluoromethyl)-1H,5H,11H-[1]benzopyrano(6,7,8-ij)quinolizin-11-one") |
    I("2,3,6,7-Tetrahydro-9-trifluoromethyl-1H,5H-quinolizino(9,1-gh)coumarin") |
    I("8-Trifluoromethyl-2,3,5,6-4H-1,H-11-oxa-3a-aza-benzo[de]anthracen-10-one") |
    I("coumarin 540A") |
    I("DN-F02") |
    I("L1") |
    I("5-[4-(diphenylamino)phenyl]thiophene-2-cyanoacrylic acid") |
    I("DN-F09") |
    I("MKA253") |
    I("(E)-3-(6-(4-(bis(5,7-dibutoxy-9,9-dimethyl-9H-fluoren-2-yl)amino)phenyl)-4,4-dihexyl-4H-cyclopenta[2,1-b:3,4-b']dithiophen-2-yl)-2-cyanoacrylic acid")
).add_action(join)

common_perovskites = (
    W('CH3NH3PbI3') |
    W('CH6I3NPb')
).add_action(join)

common_htls = (
    (I('spiro') + R('[−−-]') + (W('OMeTAD') | W('MeOTAD'))) |
    W('PEDOT:PSS') |
    (W('Li') + R('[−−-]') + I('TFSI') ) |
     W('TBP') |
    W('CuPc') |
    I("Spiro-OMeTAD") |
    I("2,2',7,7'-Tetrakis-(N,N-di-4-methoxyphenylamino)-9,9'-spirobifluorene") |
    I("C81H68N4O8") |
    I("Spiro-MeOTAD") |
    I("N7′-octakis(4-methoxyphenyl)-9,9′-spirobi[9H-fluorene]-2,2′,7,7′-tetramine") |
    I("Cuprous thiocyanate") |
    I("Copper(I) thiocyanate") |
    I("2,2',7,7'-Tetrakis-(N,N-di-4-methoxyphenylamino)-9,9'-spirobifluorene") |
    I("CCuNS") |
    I("EH44") |
    I("9-(2-Ethylhexyl)-N,N,N,N-tetrakis(4-methoxyphenyl)- 9H-carbazole-2,7-diamine)") |
    I("C48H51N3O4") |
    I("Poly-TPD") |
    I("4-butyl-N,N-diphenylaniline") |
    I("C22H23N") |
    I("X59") |
    I("Spiro[9H-fluorene-9,9′-[9H]xanthene]-2,7-diamine") |
    I("N,N,N′,N′-tetrakis(4-methoxyphenyl)spiro[fluorene-9,9′-xanthene]-2,7-diamine") |
    I("2-N,2-N,7-N,7-N-tetrakis(4-methoxyphenyl)spiro[fluorene-9,9'-xanthene]-2,7-diamineC53H42N2O5") |
    I("TFB") |
    I("N-(4-Butan-2-ylphenyl)-4-methyl-N-[4-(7-methyl-9,9-dioctylfluoren-2-yl)phenyl]aniline") |
    I("C53H67N")
).add_action(join)

etl_rules = (
        I("titanium dioxide") |
        I("TiO2") |
        I("zinc oxide") |
        I("ZnO") |
        I("tin dioxide") |
        I("stannic oxide") |
        I("SnO2") |
        I("silicon dioxide") |
        I("SiO2") |
        I("nickel oxide") |
        I("NiO") |
        I("zirconium dioxide") |
        I("ZrO2") |
        I("poly(triarylamine)") |
        I("PTAA") |
        I("phenyl-C61-butyric acid methyl ester") |
        I("PCBM") |
        I("m-TiO2") |
        I("mesoporous titanium dioxide") |
        I("c-TiO2") |
        I("compact titanium dioxide") |
        I("MgO/TiO2") |
        I("Al2O3/TiO2") |
        I("ZnO/TiO2") |
        I("TiO2/MgO") |
        I("WO3/TiO2") |
        I("np-TiO2") |
        I("titanium dioxide nanoparticles") |
        I("TiO2 nanoparticles") |
        I("Al2O3/ZnO") |
        I("ITO/ZnO") |
        I("ITO/Al2O3") |
        I("ITO/V2O5") |
        I("ITO/TiO2") |
        I("aluminum doped zinc oxide") |
        I("AZO") |
        I("hafnium(IV) oxide") |
        I("HfO2") |
        I("polyethyleneimine / titanium dioxide") |
        I("PEI/TiO2") |
        I("polyethyleneimine / zinc oxide") |
        I("PEI/ZnO")
).add_action(join)

common_etls = common_semiconductors | etl_rules

exponent = (Optional(W('×') | W('×')).hide() + W('10').hide() + Optional(R('[−-−‒‐‑-]')) + R('\d'))
dye_loading_unit = (Optional(W('(')) + exponent + I('mol') + ( (W('/') + R('[cnmk]m2')) | R('[cnmk]m[−-−‒‐‑-]2')) + Optional(W(')')))
dye_loading_unit_simple = (Optional(W('(')) + R('[cnmk]m[−-−‒‐‑-]2') | ( (W('/') + R('[cnmk]m2'))) + Optional(W(')')))


# Common properties for photovoltaic cells:
class OpenCircuitVoltage(ElectricPotentialModel):
    """Testing out a model"""
    specifier = StringType(parse_expression=I('Voc'), required=True, contextual=False, updatable=True)
    parsers = [AutoTableParserOptionalCompound()]


class ShortCircuitCurrentDensity(CurrentDensityModel):
    specifier = StringType(parse_expression=I('Jsc'), required=True, contextual=False, updatable=True)
    parsers = [AutoTableParserOptionalCompound()]


class ShortCircuitCurrent(ElectricalCurrentModel):
    specifier = StringType(parse_expression=I('Isc'), required=True, contextual=False, updatable=True)
    parsers = [AutoTableParserOptionalCompound()]


class FillFactor(RatioModel):
    specifier = StringType(parse_expression=(I('FF') | (I('fill') + I('factor')).add_action(join)), required=True, contextual=False, updatable=True)
    parsers = [AutoTableParserOptionalCompound()]


class PowerConversionEfficiency(RatioModel):
    specifier = StringType(parse_expression=(I('PCE') | I('η') | I('eff') | I('efficiency')), required=True, contextual=False, updatable=True)
    parsers = [AutoTableParserOptionalCompound()]


class Dye(BaseModel):
    """Dye Model that identifies from alphanumerics"""
    specifier = StringType(parse_expression=((R('[Dd]ye(s)?') | R('[Ss]ensiti[zs]e[rd](s)?') | R('[Cc]ompound')) + Not(I('loading') | I('adsorbed') | I('adsorption') |
                                                dye_loading_unit | SkipTo(dye_loading_unit_simple))).add_action(join), required=True, contextual=False)
    raw_value = StringType(parse_expression=((Start() + SkipTo(W('sdfkljlk'))).add_action(join)) | R('[a-zA-Z0-9_/]*'), required=True)
    parsers = [AutoTableParserOptionalCompound()]


class Reference(DimensionlessModel):
    specifier = StringType(parse_expression=I('Ref'), required=True)
    parsers = [AutoTableParserOptionalCompound()]


class RedoxCouple(BaseModel):
    specifier = StringType(parse_expression=(I('redox') + (R('[Cc]ouple(s)?') | R('[Rr]eaction(s)?'))).add_action(join), required=True)
    raw_value = StringType(parse_expression=common_redox_couples, required=True)
    parsers = [AutoTableParserOptionalCompound(), AutoSentenceParserOptionalCompound()]


class DyeLoading(AmountOfSubstanceDensityModel):
    specifier = StringType(parse_expression=(( (I('adsorbed') + I('dye')) | Optional(I('dye')) + (I('loading') | I('amount'))).add_action(join) | W('Γ') | W('Cm')), required=True)
    parsers = [AutoTableParserOptionalCompound(), AutoSentenceParserOptionalCompound()]


class CounterElectrode(BaseModel):
    specifier = StringType(parse_expression=((Optional(I('counter')) + R('[Ee]lectrode(s)?')).add_action(join) | Not(I('PCE')) + R('CE(s)?')), required=True)
    raw_value = StringType(parse_expression=(Start() + SkipTo(W('sdfkljlk')) | common_counter_electrodes).add_action(join), required=True)
    parsers = [AutoTableParserOptionalCompound(), AutoSentenceParserOptionalCompound()]


class SemiconductorThickness(LengthModel):
    specifier = StringType(parse_expression=(R('[Ss]emiconductor(s)?') | R('[Aa]node(s)?') | R('[Pp]hotoanode(s)?') | R('[Tt]hick(ness)?')), required=True)
    raw_value = StringType(required=True, contextual=False)
    parsers = [AutoTableParserOptionalCompound(lenient=False), AutoSentenceParserOptionalCompound()]


class Semiconductor(BaseModel):
    specifier = StringType(parse_expression=(R('[Ss]emiconductor(s)?') | R('[Aa]node(s)?') | R('[Pp]hotoanode(s)?')), required=True)
    raw_value = StringType(parse_expression=(Start() + SkipTo(W('sdfkljlk'))).add_action(join) | common_semiconductors)
    thickness = ModelType(SemiconductorThickness, required=False)
    parsers = [AutoTableParserOptionalCompound(), AutoSentenceParserOptionalCompound()]


class ActiveArea(AreaModel):
    specifier = StringType(parse_expression=((I('active') + I('area')).add_action(join)), required=True)
    parsers = [AutoTableParserOptionalCompound(), AutoSentenceParserOptionalCompound()]


class SimulatedSolarLightIntensity(IrradianceModel):
    specifier = StringType(parse_expression=(I('irradiance') | I('illumination') | I('solar') + I('simulator')  | (I('light') + I('intensity') + Optional(I('of'))).add_action(join)), required=True)
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


class ChargeTransferResistance(ResistanceModel):
    specifier = StringType(parse_expression=(R('Rct\d?') | R('Rk')), required=True)
    parsers = [AutoTableParserOptionalCompound()]


class SeriesResistance(ResistanceModel):
    specifier = StringType(parse_expression=W('Rs'), required=True)
    parsers = [AutoTableParserOptionalCompound()]


class SpecificChargeTransferResistance(SpecificResistanceModel):
    specifier = StringType(parse_expression=(R('Rct\d?') | R('Rk')), required=True)
    parsers = [AutoTableParserOptionalCompound()]


class SpecificSeriesResistance(SpecificResistanceModel):
    specifier = StringType(parse_expression=W('Rs'), required=True)
    parsers = [AutoTableParserOptionalCompound()]


class ExposureTime(TimeModel):
    specifier = StringType(parse_expression=(I('exposure') | (Optional(I('exposure')) + I('time'))).add_action(join), required=True)
    parsers = [AutoTableParserOptionalCompound()]


class PowerIn(PowerModel):
    specifier = StringType(parse_expression=(I('Pin') | I('power') + I('in') ).add_action(join), required=True)
    parsers = [AutoTableParserOptionalCompound()]


class PowerMax(PowerModel):
    specifier = StringType(parse_expression=(I('Pmax') | (R('[mM]ax(imum)?') + I('power')) ).add_action(join), required=True)
    parsers = [AutoTableParserOptionalCompound()]


class PhotovoltaicCell(BaseModel):
    """ Class for photovoltaic devices. Uses a number of automatic parsers."""

    def __init__(self, **raw_data):
        """"""
        self._values = {}
        for key, value in six.iteritems(raw_data):
            setattr(self, key, value)
        # Set defaults
        for key, field in six.iteritems(self.fields):
            if key not in raw_data:
                setattr(self, key, copy.copy(field.default))
        self._record_method = None
        self.was_updated = self._updated
        self.calculated_properties = {}

    def set_calculated_properties(self, prop_key, property):
        self.calculated_properties[prop_key] = property


    specifier = StringType(parse_expression=Any().hide(), required=False, contextual=False)

    voc = ModelType(OpenCircuitVoltage, required=False, contextual=False)
    ff = ModelType(FillFactor, required=False, contextual=False)
    pce = ModelType(PowerConversionEfficiency, required=False, contextual=False)
    jsc = ModelType(ShortCircuitCurrentDensity, required=False, contextual=False)
    isc = ModelType(ShortCircuitCurrent, required=False, contextual=False)
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
    charge_transfer_resistance = ModelType(ChargeTransferResistance, required=False, contextual=False)
    series_resistance = ModelType(SeriesResistance, required=False, contextual=False)
    specific_charge_transfer_resistance = ModelType(SpecificChargeTransferResistance, required=False, contextual=False)
    specific_series_resistance = ModelType(SpecificSeriesResistance, required=False, contextual=False)
    exposure_time = ModelType(ExposureTime, required=False, contextual=True)
    pin = ModelType(PowerIn, required=False, contextual=True)
    pmax = ModelType(PowerMax, required=False, contextual=True)

    parsers = [AutoTableParserOptionalCompound()]#, AutoSentenceParserOptionalCompound()]

# Sentence parsers for separately  sentence information


class SentenceDye(BaseModel):
    """ Permissive parser for Dyes mentioned in a sentence. Finds the word 'dye', and accepts any alphanumeric label."""

    alphanumeric_label= R('^(([A-Z][\--–−]?)+\d{1,3})$')('labels')
    lenient_label = Not(not_dyes) + (alphanumeric_label | strict_chemical_label)

    specifier = StringType(parse_expression=((I('dye') + Not(Optional(hyphens) + I('sensitized'))| R('sensiti[zs]er(s)?') | R('dsc(s)?', re.I)) + Not(I('loading'))).add_action(join), required=True, contextual=False)
    raw_value = StringType(parse_expression=(common_dyes | lenient_label), required=True)
    parsers = [AutoSentenceParserOptionalCompound()]


class CommonSentenceDye(BaseModel):
    """ Restricted parsers for Dyes mentioned in a sentence. Finds the word 'dye', and accepts only common dyes from a list."""

    specifier = StringType(parse_expression=((I('dye') | R('sensiti[zs]er') | R('dsc(s)?', re.I)) + Not(I('loading'))).add_action(join),
                           required=True, contextual=False)
    raw_value = StringType(parse_expression=common_dyes, required=True)
    parsers = [AutoSentenceParserOptionalCompound()]


class SentenceSemiconductor(BaseModel):
    specifier = StringType(parse_expression=(R('[Ss]emiconductor(s)?') | R('[Aa]node(s)?')), required=True)
    raw_value = StringType(parse_expression=common_semiconductors, required=True)
    thickness = ModelType(SemiconductorThickness, required=False)
    parsers = [ AutoSentenceParserOptionalCompound()]


class SentenceDyeLoading(AmountOfSubstanceDensityModel):
    specifier = StringType(parse_expression=((Optional(I('dye')) + (I('loading') | I('amount'))).add_action(join) | W('Γ') | W('Cm')), required=True)
    exponent = None
    parsers = [AutoSentenceParserOptionalCompound(lenient=True)]


# Separate classes for perovskites


class Perovskite(BaseModel):
    """Dye Model that identifies from alphanumerics"""
    specifier = StringType(parse_expression=((I('perovskite') | (I('light') + I('harvester')) + Optional('material') )).add_action(join), required=True, contextual=False)
    raw_value = StringType(parse_expression=(((Start() + SkipTo(W('sdfkljlk')) )| common_perovskites).add_action(join)), required=True)
    parsers = [AutoTableParserOptionalCompound(), AutoSentenceParserOptionalCompound()]


class HoleTransportLayer(BaseModel):
    """ Hole transporting layer of solar cell (replaces electrolyte)"""
    specifier = StringType(parse_expression=( R('HTLs?') | R('HCLs?') | R('HCMs?') | R('HTMs?') | R('HSLs?') |
        ( I('hole') + Optional(I('[−−-]')) + (I('conducting') | I('transport') | I('transporting') | I('selective') | I('selection')) + (I('material') | I('layer')))
         ).add_action(join), required=True, contextual=False)
    raw_value = StringType(parse_expression=(((Start() + SkipTo(W('sdfkljlk'))) | common_htls).add_action(join)), required=True)
    parsers = [AutoTableParserOptionalCompound(), AutoSentenceParserOptionalCompound()]


class ElectronTransportLayer(BaseModel):
    """ Electron transporting layer of solar cell (usual term for semiconductor here.)"""
    specifier = StringType(parse_expression=( R('ETLs?') | W('ECLs?') | W('ECMs?') | W('ETMs?') | W('ESLs?') |
        ( I('electron') + Optional(I('[−−-]'))
          + (I('conducting') | I('transport') | I('transporting') | I('selective') | I('selection') | I('extraction') | I('collection'))
          + (I('material') | I('layer')))
         ).add_action(join), required=True, contextual=False)
    raw_value = StringType(parse_expression=(((Start() + SkipTo(W('sdfkljlk')))| common_etls).add_action(join)), required=True)
    parsers = [AutoTableParserOptionalCompound(), AutoSentenceParserOptionalCompound()]


class PerovskiteSolarCell(BaseModel):
    """ Class for perovskite photovoltaic devices. Uses a number of automatic parsers."""

    def __init__(self, **raw_data):
        """"""
        self._values = {}
        for key, value in six.iteritems(raw_data):
            setattr(self, key, value)
        # Set defaults
        for key, field in six.iteritems(self.fields):
            if key not in raw_data:
                setattr(self, key, copy.copy(field.default))
        self._record_method = None
        self.was_updated = self._updated
        self.calculated_properties = {}

    def set_calculated_properties(self, prop_key, property):
        self.calculated_properties[prop_key] = property

    specifier = StringType(parse_expression=Any().hide(), required=False, contextual=False)

    voc = ModelType(OpenCircuitVoltage, required=False, contextual=False)
    ff = ModelType(FillFactor, required=False, contextual=False)
    pce = ModelType(PowerConversionEfficiency, required=False, contextual=False)
    jsc = ModelType(ShortCircuitCurrentDensity, required=False, contextual=False)
    isc = ModelType(ShortCircuitCurrent, required=False, contextual=False)
    ref = ModelType(Reference, required=False, contextual=False)
    counter_electrode = ModelType(CounterElectrode, required=False, contextual=False)
    etl = ModelType(ElectronTransportLayer, required=False, contextual=False) # Electron_transport_layer
    htl = ModelType(HoleTransportLayer, required=False, contextual=False) # Hole trasport layer
    # ADd for interfacial layer? Or is this too specific / variable?
    perovskite = ModelType(Perovskite, required=False, contextual=False)
    active_area = ModelType(ActiveArea, required=False, contextual=False)
    solar_simulator = ModelType(SimulatedSolarLightIntensity, required=False, contextual=True)
    substrate = ModelType(Substrate, required=False, contextual=False)
    charge_transfer_resistance = ModelType(ChargeTransferResistance, required=False, contextual=False)
    series_resisitance = ModelType(SeriesResistance, required=False, contextual=False)
    specific_charge_transfer_resistance = ModelType(SpecificChargeTransferResistance, required=False, contextual=False)
    specific_series_resistance = ModelType(SpecificSeriesResistance, required=False, contextual=False)
    exposure_time = ModelType(ExposureTime, required=False, contextual=True)
    pin = ModelType(PowerIn, required=False, contextual=True)
    pmax = ModelType(PowerMax, required=False, contextual=True)

    parsers = [AutoTableParserOptionalCompound()]
