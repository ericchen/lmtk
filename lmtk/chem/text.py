# -*- coding: utf-8 -*-
"""
lmtk.chem.text
~~~~~~~~~~~~~~

Chemistry text handling.

:copyright: Copyright 2014 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

import re

from lmtk import text

# All chemical element names.
# Includes both aluminium and aluminum, both tungsten and wolfram, and some former names (plumbum, hydrargyrum).
ELEMENTS = {
    u'actinium', u'aluminium', u'aluminum', u'americium', u'antimony', u'argon', u'arsenic', u'astatine', u'barium',
    u'berkelium', u'beryllium', u'bismuth', u'bohrium', u'boron', u'bromine', u'cadmium', u'caesium', u'calcium',
    u'californium', u'carbon', u'cerium', u'cesium', u'chlorine', u'chromium', u'cobalt', u'copernicium', u'copper',
    u'curium', u'darmstadtium', u'dubnium', u'dysprosium', u'einsteinium', u'erbium', u'europium', u'fermium',
    u'flerovium', u'fluorine', u'francium', u'gadolinium', u'gallium', u'germanium', u'gold', u'hafnium', u'hassium',
    u'helium', u'holmium', u'hydrargyrum', u'hydrogen', u'indium', u'iodine', u'iridium', u'iron', u'kalium',
    u'krypton', u'lanthanum', u'lawrencium', u'lead', u'lithium', u'livermorium', u'lutetium', u'magnesium',
    u'manganese', u'meitnerium', u'mendelevium', u'mercury', u'molybdenum', u'natrium', u'neodymium', u'neon',
    u'neptunium', u'nickel', u'niobium', u'nitrogen', u'nobelium', u'osmium', u'oxygen', u'palladium', u'phosphorus',
    u'platinum', u'plumbum', u'plutonium', u'polonium', u'potassium', u'praseodymium', u'promethium', u'protactinium',
    u'radium', u'radon', u'rhenium', u'rhodium', u'roentgenium', u'rubidium', u'ruthenium', u'rutherfordium',
    u'samarium', u'scandium', u'seaborgium', u'selenium', u'silicon', u'silver', u'sodium', u'stannum', u'stibium',
    u'strontium', u'sulfur', u'tantalum', u'technetium', u'tellurium', u'terbium', u'thallium', u'thorium', u'thulium',
    u'tin', u'titanium', u'tungsten', u'ununoctium', u'ununpentium', u'ununseptium', u'ununtrium', u'uranium',
    u'vanadium', u'wolfram', u'xenon', u'ytterbium', u'yttrium', u'zinc', u'zirconium'
}

ELEMENT_SYMBOLS = {
    u'Ac', u'Ag', u'Al', u'Am', u'Ar', u'As', u'At', u'Au', u'B', u'Ba', u'Be', u'Bh', u'Bi', u'Bk', u'Br', u'C', u'Ca',
    u'Cd', u'Ce', u'Cf', u'Cl', u'Cm', u'Cn', u'Co', u'Cr', u'Cs', u'Cu', u'Db', u'Ds', u'Dy', u'Er', u'Es', u'Eu',
    u'F', u'Fe', u'Fl', u'Fm', u'Fr', u'Ga', u'Gd', u'Ge', u'H', u'He', u'Hf', u'Hg', u'Ho', u'Hs', u'I', u'In', u'Ir',
    u'K', u'Kr', u'La', u'Li', u'Lr', u'Lu', u'Lv', u'Md', u'Mg', u'Mn', u'Mo', u'Mt', u'N', u'Na', u'Nb', u'Nd', u'Ne',
    u'Ni', u'No', u'Np', u'O', u'Os', u'P', u'Pa', u'Pb', u'Pd', u'Pm', u'Po', u'Pr', u'Pt', u'Pu', u'Ra', u'Rb', u'Re',
    u'Rf', u'Rg', u'Rh', u'Rn', u'Ru', u'S', u'Sb', u'Sc', u'Se', u'Sg', u'Si', u'Sm', u'Sn', u'Sr', u'Ta', u'Tb',
    u'Tc', u'Te', u'Th', u'Ti', u'Tl', u'Tm', u'U', u'Uuo', u'Uup', u'Uus', u'Uut', u'V', u'W', u'Xe', u'Y', u'Yb',
    u'Zn', u'Zr'
}

# Formula regex?
# ((A[cglmrstu]|B[aehikr]?|C[adeflmnorsu]?|D[bsy]|E[rsu]|F[elmr]?|G[ade]|H[efgos]?|I[nr]?|Kr?|L[airuv]|M[dgnot]|N[abdeiop]?|Os?|P[abdmortu]?|R[abefghnu]|S[bcegimnr]?|T[abcehilm]|U|V|W|Xe|Yb?|Z[nr])\d?\d?)+

# Common solvent names.
# Use SOLVENT_RE for proper matching of solvent names.
SOLVENTS = {
    u'(CD3)2CO', u'(CDCl2)2', u'(CH3)2CHOH', u'(CH3)2CO', u'(CH3)2NCOH', u'[nBu4N][BF4]', u'1-butanol',
    u'1-butylimidazole', u'1-cyclohexanol', u'1-decanol', u'1-heptanol', u'1-hexanol', u'1-methylethyl acetate',
    u'1-octanol', u'1-pentanol', u'1-phenylethanol', u'1-propanol', u'1-undecanol', u'1,1,1-trifluoroethanol',
    u'1,1,1,3,3,3-hexafluoro-2-propanol', u'1,1,1,3,3,3-hexafluoropropan-2-ol', u'1,1,2-trichloroethane',
    u'1,2-c2h4cl2', u'1,2-dichloroethane', u'1,2-dimethoxyethane', u'1,2-dimethylbenzene', u'1,2-ethanediol',
    u'1,2,4-trichlorobenzene', u'1,4-dimethylbenzene', u'1,4-dioxane', u'2-(n-morpholino)ethanesulfonic acid',
    u'2-butanol', u'2-butanone', u'2-me-thf', u'2-methf', u'2-methoxy-2-methylpropane', u'2-methyl tetrahydrofuran',
    u'2-methylpentane', u'2-methylpropan-1-ol', u'2-methylpropan-2-ol', u'2-methyltetrahydrofuran', u'2-proh',
    u'2-propanol', u'2-propyl acetate', u'2-pyrrolidone', u'2,2,2-trifluoroethanol', u'2,2,4-trimethylpentane',
    u'2Me-THF', u'2MeTHF', u'3-methyl-pentane', u'4-methyl-1,3-dioxolan-2-one', u'acetic acid', u'aceto-nitrile',
    u'acetone', u'acetonitrile', u'acetononitrile', u'ACN', u'AcOEt', u'AcOH', u'AgNO3', u'aniline', u'anisole', u'AOT',
    u'BCN', u'benzene', u'benzonitrile', u'benzyl alcohol', u'BHDC', u'bromoform', u'BTN', u'Bu2O', u'Bu4NBr',
    u'Bu4NClO4', u'Bu4NPF6', u'BuCN', u'BuOH', u'butan-1-ol', u'butan-2-ol', u'butan-2-one', u'butane', u'butanol',
    u'butanone', u'butene', u'butyl acetate', u'butyl acetonitrile', u'butyl alcohol', u'butyl amine',
    u'butyl chloride', u'butyl imidazole', u'butyronitrile', u'c-hexane', u'C2D5CN', u'C2H4Cl2', u'C2H5CN', u'C2H5OH',
    u'C5H5N', u'C6D6', u'C6H12', u'C6H14', u'C6H5CH3', u'C6H5Cl', u'C6H6', u'C7D8', u'C7H8', u'carbon disulfide',
    u'carbon tetrachloride', u'CCl4', u'CD2Cl2', u'CD3CN', u'CD3COCD3', u'CD3OD', u'CD3SOCD3', u'CDCl3', u'CH2Cl2',
    u'CH2ClCH2Cl', u'CH3C6H5', u'CH3Cl', u'CH3CN', u'CH3CO2H', u'CH3COCH3', u'CH3COOH', u'CH3NHCOH', u'CH3NO2',
    u'CH3OD', u'CH3OH', u'CH3Ph', u'CH3SOCH3', u'CHCl2', u'CHCl3', u'chlorobenzene', u'chloroform', u'chloromethane',
    u'chlorotoluene', u'CHX', u'Cl2CH2', u'ClCH2CH2Cl', u'cumene', u'cyclohexane', u'cyclohexanol', u'cyclopentyl methyl ether',
    u'D2O', u'DCE', u'DCM', u'decalin', u'decan-1-ol', u'decane', u'decanol', u'DEE', u'di-isopropyl ether',
    u'di-n-butyl ether', u'di-n-hexyl ether', u'dibromoethane', u'dibutoxymethane', u'dibutyl ether',
    u'dichloro-methane', u'dichlorobenzene', u'dichloroethane', u'dichloromethane', u'diethoxymethane',
    u'diethyl carbonate', u'diethyl ether', u'diethylamine', u'diethylether', u'diglyme', u'dihexyl ether',
    u'diiodomethane', u'diisopropyl ether', u'diisopropylamine', u'dimethoxyethane', u'dimethoxymethane',
    u'dimethyl acetamide', u'dimethyl acetimide', u'dimethyl benzene', u'dimethyl carbonate', u'dimethyl ether',
    u'dimethyl formamide', u'dimethyl sulfoxide', u'dimethylacetamide', u'dimethylbenzene', u'dimethylformamide',
    u'dimethylformanide', u'dimethylsulfoxide', u'dioctyl sodium sulfosuccinate', u'dioxane', u'dioxolane',
    u'dipropyl ether', u'DMA', u'DMAc', u'DMF', u'DMSO', u'Et2O', u'EtAc', u'EtAcO', u'EtCN', u'ethane diol',
    u'ethane-1,2-diol', u'ethanol', u'ethyl (S)-2-hydroxypropanoate', u'ethyl acetate', u'ethyl benzoate',
    u'ethyl formate', u'ethyl lactate', u'ethyl propionate', u'ethylacetamide', u'ethylacetate', u'ethylene carbonate',
    u'ethylene glycol', u'ethyleneglycol', u'ethylhexan-1-ol', u'EtOAc', u'EtOD', u'EtOH', u'eucalyptol', u'F3-ethanol',
    u'F3-EtOH', u'formamide', u'formic acid', u'glacial acetic acid', u'glycerol', u'H2O', u'H2O + TX', u'H2O-Triton X',
    u'H2O2', u'H2SO4', u'HBF4', u'HCl', u'HClO4', u'HCO2H', u'HCONH2', u'HDA', u'heavy water', u'HEPES', u'heptan-1-ol',
    u'heptane', u'heptanol', u'heptene', u'HEX', u'hexadecylamine', u'hexafluoroisopropanol', u'hexafluoropropanol',
    u'hexan-1-ol', u'hexane', u'hexanes', u'hexanol', u'hexene', u'hexyl ether', u'HFIP,', u'HFP', u'HNO3',
    u'hydrochloric acid', u'hydrogen peroxide', u'iodobenzene', u'IPA', u'isohexane', u'isooctane', u'isopropanol',
    u'isopropyl benzene', u'KBr', u'KPB', u'LiCl', u'ligroine', u'limonene', u'MCH', u'Me-THF', u'Me2CO', u'MeCN',
    u'MeCO2Et', u'MeNO2', u'MeOD', u'MeOH', u'MES', u'mesitylene', u'methanamide', u'methanol', u'MeTHF',
    u'methoxybenzene', u'methoxyethylamine', u'methyl acetamide', u'methyl acetoacetate', u'methyl benzene',
    u'methyl butane', u'methyl cyclohexane', u'methyl ethyl ketone', u'methyl formamide', u'methyl formate',
    u'methyl isobutyl ketone', u'methyl laurate', u'methyl methanoate', u'methyl naphthalene', u'methyl pentane',
    u'methyl propan-1-ol', u'methyl propan-2-ol', u'methyl propionate', u'methyl pyrrolidin-2-one',
    u'methyl pyrrolidine', u'methyl pyrrolidinone', u'methyl t-butyl ether', u'methyl tetrahydrofuran',
    u'methyl-2-pyrrolidone', u'methylbenzene', u'methylcyclohexane', u'methylene chloride', u'methylformamide',
    u'methyltetrahydrofuran', u'MIBK', u'morpholine', u'mTHF', u'n-butanol', u'n-butyl acetate', u'n-decane',
    u'n-heptane', u'n-HEX', u'n-hexane', u'n-methylformamide', u'n-methylpyrrolidone', u'n-nonane', u'n-octanol',
    u'n-pentane', u'n-propanol', u'n,n-dimethylacetamide', u'n,n-dimethylformamide', u'n,n-DMF', u'Na2SO4', u'NaCl',
    u'NaClO4', u'NaHCO3', u'NaOH', u'nBu4NBF4', u'nitric acid', u'nitrobenzene', u'nitromethane', u'NMP', u'nonane',
    u'NPA', u'nujol', u'o-dichlorobenzene', u'o-xylene', u'octan-1-ol', u'octane', u'octanol', u'octene', u'ODCB',
    u'p-xylene', u'PBS', u'pentan-1-ol', u'pentane', u'pentanol', u'pentanone', u'pentene', u'PeOH', u'perchloric acid',
    u'PhCH3', u'PhCl', u'PhCN', u'phenoxyethanol', u'phenyl acetylene', u'Phenyl ethanol', u'phenylamine',
    u'phenylethanolamine', u'phenylmethanol', u'PhMe', u'phosphate', u'phosphate buffered saline', u'pinane',
    u'piperidine', u'polytetrafluoroethylene', u'potassium bromide', u'potassium phosphate buffer', u'PrCN', u'PrOH',
    u'propan-1-ol', u'propan-2-ol', u'propane', u'propane-1,2-diol', u'propane-1,2,3-triol', u'propanol', u'propene',
    u'propionic acid', u'propionitrile', u'propyl acetate', u'propyl amine', u'propylene carbonate',
    u'propylene glycol', u'pyridine', u'pyrrolidone', u'quinoline', u'SDS', u'silver nitrate', u'SNO2',
    u'sodium chloride', u'sodium hydroxide', u'sodium perchlorate', u'sulfuric acid', u't-butanol', u'TBABF4', u'TBAF',
    u'TBAH', u'TBAOH', u'TBAP', u'TBAPF6', u'TBP', u'TEA', u'TEAP', u'TEOA', u'tert-butanol', u'tert-butyl alcohol',
    u'tetrabutylammonium hexafluorophosphate', u'tetrabutylammonium hydroxide', u'tetrachloroethane',
    u'tetrachloroethylene', u'tetrachloromethane', u'tetrafluoroethylene', u'tetrahydrofuran', u'tetralin',
    u'tetramethylsilane', u'tetramethylurea', u'tetrapiperidine', u'TFA', u'TFE', u'THF', u'THF-d8', u'tin dioxide',
    u'titanium dioxide', u'toluene', u'tri-n-butyl phosphate', u'triacetate', u'triacetin', u'tribromomethane',
    u'tributyl phosphate', u'trichlorobenzene', u'trichloroethene', u'trichloromethane', u'triethyl amine',
    u'triethyl phosphate', u'triethylamine', u'trifluoroacetic acid', u'trifluoroethanol', u'trifluoroethanol ',
    u'trimethyl benzene', u'trimethyl pentane', u'tris', u'Triton X-100', u'TX-100', u'undecan-1-ol', u'undecanol',
    u'valeronitrile', u'water', u'xylene', u'xylol'
}

# Common chemical name prefixes
PREFIXES = {u'iso', u'tert', u'sec', u'ortho', u'meta', u'para', u'meso'}

# A regular expression that matches common solvents.
SOLVENT_RE = re.compile(ur'(?:^|\b)(?:(?:%s|d\d?\d?|[\dn](?:,[\dn]){0,3}|[imnoptDLRS])-?)?(?:%s)(?:-d\d?\d?)?(?=$|\b)'
                        % ('|'.join(re.escape(s) for s in PREFIXES),
                           '|'.join(re.escape(s).replace(ur'\ ', ur'[\s\-]?') for s in SOLVENTS)), re.I)

# Regular expressions for validating chemical identifiers
CAS_RE = re.compile(r'^\d{1,7}-\d\d-\d$')
INCHIKEY_RE = re.compile(r'^[A-Z]{14}-[A-Z]{10}-[A-Z\d]$')
INCHI_RE = re.compile(r'^(InChI=)?1S?/(p\+1|\d*[a-ik-z][a-ik-z\d\.]*(/c[\d\-*(),;]+)?(/h[\d\-*h(),;]+)?)'
                      r'(/[bmpqst][\d\-\.+*,;?]*|/i[hdt\d\-+*,;]*(/h[hdt\d]+)?|'
                      r'/r[a-ik-z\d]+(/c[\d\-*(),;]+)?(/h[\d\-*h(),;]+)?|/f[a-ik-z\d]*(/h[\d\-*h(),;]+)?)*$', re.I)
SMILES_RE = re.compile(r'^([BCNOPSFIbcnosp*]|Cl|Br|\[\d*(%(e)s|se|as|\*)(@+([THALSPBO]\d+)?)?(H\d?)?([\-+]+\d*)?(:\d+)?\])'
                       r'([BCNOPSFIbcnosp*]|Cl|Br|\[\d*(%(e)s|se|as|\*)(@+([THALSPBO]\d+)?)?(H\d?)?([\-+]+\d*)?(:\d+)?\]|'
                       r'[\-=#$:\\/\(\)%%\.+\d])*$' % {'e': '|'.join(ELEMENT_SYMBOLS)})


def normalize(s):
    """Normalize unicode, hyphens, whitespace, and some chemistry terms and formatting."""
    # Perform the standard text normalization
    s = text.normalize(s)
    # Normalize element spelling
    s = re.sub(ur'sulph', ur'sulf', s, flags=re.I)
    s = re.sub(ur'aluminum', ur'aluminium', s, flags=re.I)
    s = re.sub(ur'cesium', ur'caesium', s, flags=re.I)
    # Remove space between element and oxidation state (copper (II) --> copper(II))
    s = re.sub(ur'(%s) \((\d[+-]|[+-]\d|0|I{1,3}|IV|VI{1,3}|IX)\)' % '|'.join(ELEMENTS), ur'\1(\2)', s, flags=re.I)
    # Add space between numeric quantity and units (Only applies with certain characters before and after)
    s = re.sub(ur'(^|[^\w>\-∼~≈)])([∼~≈]?)((?:(?:(?:[0-9]|[1-9][0-9]+)(?:\.\d+)?|\.\d+)-)?(?:[0-9]|[1-9][0-9]+)(?:\.\d+)?|\.\d+)'
               ur'([cdGkmMnpTuμ]?(?:[JlLMmNVW]|[Gg]ramm?e?s?|Hz|[Mm][Oo][Ll](?:e|ar)?s?|h?Pa|ppm)(?:-?\d)?)($|[^\w<\-])',
               ur'\1\2\3 \4\5', s)
    # Stricter rules for g and s, as they often occur in other contexts
    s = re.sub(ur'(^|[^\w>\-∼~≈)])([∼~≈]?)((?:[0-9]|[1-9][0-9]+)(?:\.\d+)?|\.\d+)([kmnuμ]?(?:g)(?:-?\d)?)($|[^\w<\-])',
               ur'\1\2\3 \4\5', s)
    s = re.sub(ur'(^|[^\w>\-∼~≈)])([∼~≈]?)(?![12]s)((?:[0-9]|[1-9][0-9]+)(?:\.\d+)?|\.\d+)([mnpuμ]?(?:s)(?:-?\d)?)($|[^\w<\-])',
               ur'\1\2\3 \4\5', s)
    # Add space between numeric quantity and percentage
    s = re.sub(ur'\b(-?\d+(\.\d+)?|\d*\.\d+)%($|[^\w])', ur'\1 %\3', s)
    # Add space between pH and value
    s = re.sub(ur'\b(ph)(-?\d+(\.\d+)?)\b', ur'\1 \2', s, flags=re.I)
    # Normalise whitespace around temperature units ("10° C" to "10 °C")
    s = re.sub(ur'(\d)\s*([°º])\s*([cf]?)($|[^\w])', ur'\1 \2\3\4', s, flags=re.I)
    # Normalise space followed by combining character to the single combined character
    s = re.sub(ur' \u0307', ur'\u02d9', s)
    return s


def extract_inchis(s):
    """Return a list of InChI identifiers extracted from the string."""
    return [t for t in text.u(s).split() if INCHI_RE.match(t)]


def extract_inchikeys(s):
    """Return a list of InChIKey identifiers extracted from the string."""
    return [t for t in text.u(s).split() if INCHIKEY_RE.match(t)]


def extract_smiles(s):
    """Return a list of SMILES identifiers extracted from the string."""
    # TODO: This still gets a lot of false positives.
    smiles = []
    for t in text.u(s).split():
        if len(t) > 2 and SMILES_RE.match(t) and not t.endswith('.') and text.bracket_level(t) == 0:
            smiles.append(t)
    return smiles


def extract_cas(s):
    """Return a list of CAS identifiers extracted from the string."""
    return [t for t in text.u(s).split() if CAS_RE.match(t)]

