#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""lmtk.chem - Chemistry text-mining tools."""

from .text import ELEMENT_SYMBOLS, ELEMENTS, SOLVENTS, PREFIXES, SOLVENT_RE, CAS_RE, INCHIKEY_RE, INCHI_RE, SMILES_RE, normalize
from .tokenize import ChemTokenizer
