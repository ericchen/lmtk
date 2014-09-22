#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unit tests for chem package."""

import unittest

from lmtk.chem import normalize, SOLVENT_RE, ChemTokenizer, INCHI_RE, SMILES_RE


class TestNormalization(unittest.TestCase):
    """Test chem normalize function."""

    def test_quantities(self):
        self.assertEqual(u'The spectrum was recorded at 10 °C', normalize(u'The spectrum was recorded at 10° C'))
        self.assertEqual(u'Some Copper(II) oxide was added', normalize(u'Some Copper (II) oxide was added'))
        self.assertEqual(u'Placed at a distance of 7.2 cm.', normalize(u'Placed at a distance of 7.2cm.'))
        self.assertEqual(u'Addition of ~1.8 mg of CaCO3.', normalize(u'Addition of ~1.8mg of CaCO3.'))
        self.assertEqual(u'Recorded in HCl (pH 2).', normalize(u'Recorded in HCl (pH2).'))
        self.assertEqual(u'Experienced a pressure of 160 kPa.', normalize(u'Experienced a pressure of 160kPa.'))
        self.assertEqual(u'Brought to pH 10.5, gradually.', normalize(u'Brought to pH10.5, gradually.'))
        self.assertEqual(u'A volume of 24 cm3 was drained.', normalize(u'A volume of 24cm3 was drained.'))
        self.assertEqual(u'2 M H2SO4 was heated.', normalize(u'2M H2SO4 was heated.'))
        self.assertEqual(u'Increased by 110 %.', normalize(u'Increased by 110%.'))
        self.assertEqual(u'Increased by 110 %', normalize(u'Increased by 110%'))
        self.assertEqual(u'Up to 2 % contamination', normalize(u'Up to 2% contamination'))
        self.assertEqual(u'Then .03 % was added', normalize(u'Then .03% was added'))
        self.assertEqual(u'and ≈90 °', normalize(u'and ≈90°'))
        self.assertEqual(u'of 25 μM,', normalize(u'of 25μM,'))
        self.assertEqual(u'at angles α 0-45 °.', normalize(u'at angles α 0-45° .'))

    def test_nonquantities(self):
        self.assertEqual(u'(C2H5)4N', normalize(u'(C2H5)4N'))
        self.assertEqual(u'monomer 28M-Py2', normalize(u'monomer 28M-Py2'))
        self.assertEqual(u'[NiH-3L]', normalize(u'[NiH-3L]'))
        self.assertEqual(u'using Gaussian 09W', normalize(u'using Gaussian 09W'))
        self.assertEqual(u'B3LYP/6-31g(d)', normalize(u'B3LYP/6-31g(d)'))
        self.assertEqual(u'In the 1s and 2s state', normalize(u'In the 1s and 2s state'))
        self.assertEqual(u'Ph2SnCl2', normalize(u'Ph2SnCl2'))

    def test_punctuation(self):
        self.assertEqual(u'Sentence trails off...', normalize(u'Sentence trails off…'))
        self.assertEqual(u'[(R-DAB)PtMe4]˙', normalize(u'[(R-DAB)PtMe4] \u0307'))


class TestRegex(unittest.TestCase):

    def test_solvent(self):
        """Test solvent regex."""
        self.assertEqual([u'CH2Cl2'], SOLVENT_RE.findall(u'λmax(CH2Cl2)/nm'))
        self.assertEqual([u'acetonitrile', u'C6H6'], SOLVENT_RE.findall(u'Measured in acetonitrile and C6H6'))
        self.assertEqual([u'd2-dichloromethane'], SOLVENT_RE.findall(u'Spectra in d2-dichloromethane'))
        self.assertEqual([u'isopropanol'], SOLVENT_RE.findall(u'The solvent was isopropanol'))
        self.assertEqual([u'1,2-dichlorobenzene'], SOLVENT_RE.findall(u'Mixed with 1,2-dichlorobenzene.'))
        self.assertEqual([u'CHCl3', u'HCl'], SOLVENT_RE.findall(u'The mixture CHCl3/HCl was added.'))
        self.assertEqual([u'Ethyl acetate', u'Diethyl ether'], SOLVENT_RE.findall(u'Ethyl acetate. Diethyl ether.'))
        self.assertEqual([u'Ethylacetate', u'Diethylether'], SOLVENT_RE.findall(u'Ethylacetate. Diethylether.'))
        self.assertEqual([], SOLVENT_RE.findall(u'[Rh2(dihex)4]2+'))

    def test_inchi(self):
        """Test InChI regex."""
        self.assertFalse(INCHI_RE.match(u'InChI'))
        self.assertFalse(INCHI_RE.match(u'InChI=1S'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/C7H4N.Li/c1-2-7-4-3-5-8-6-7;/h3-6H;/q-1;+1'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/C9H13BO2S/c1-9(2)6-11-10(12-7-9)8-4-3-5-13-8/h3-5H,6-7H2,1-2H3'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/C7H12O/c8-6-7-4-2-1-3-5-7/h6-7H,1-5H2'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/Ca.2H2O.2H2/h;2*1H2;2*1H'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/2BrH.Fe/h2*1H;'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/C8H2Br2N2/c9-7-1-5(3-11)6(4-12)2-8(7)10/h1-2H'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/C9H10O3/c1-11-8-3-4-9(12-2)7(5-8)6-10/h3-6H,1-2H3'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/C8H13NOS/c1-6-11-7-8(1)9-2-4-10-5-3-9/h1H,2-7H2'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/C7H10N.BrH/c1-2-8-6-4-3-5-7-8;/h3-7H,2H2,1H3;1H/q+1;/p-1'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/C13H9N.C2H7N5/c1-2-6-11-10(5-1)9-14-13-8-4-3-7-12(11)13;3-1(4)7-2(5)6/h1-9H;(H7,3,4,5,6,7)'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/C26H56N/c1-5-7-9-11-13-15-17-19-21-23-25-27(3,4)26-24-22-20-18-16-14-12-10-8-6-2/h5-26H2,1-4H3/q+1'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/C12H10Si/c1-2-5-10-9(4-1)8-12-11(10)6-3-7-13-12/h1-7,13H,8H2'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/C7H10N2.Au/c1-9(2)7-3-5-8-6-4-7;/h3-6H,1-2H3;'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/C8H6Cl4/c1-3(2)4-5(9)7(11)8(12)6(4)10/h1-2H3'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/BH3IP/c2-1-3/h1H,3H2'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/C6H15N3/c1-2-4-8-9-6-5-7-3-1/h7-9H,1-6H2'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/2C8H5.Ru/c2*1-2-8-6-4-3-5-7-8;/h2*3-7H;/q2*-1;+2'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/HI/h1H/i/hD'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/F5P.FH.H3N/c1-6(2,3,4)5;;/h;1H;1H3'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/C10H16/c1-8(2)10-6-4-9(3)5-7-10/h4,10H,1,5-7H2,2-3H3'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/Mo.4O/q;;;2*-1'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/In.N'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/Au.H3P/h;1H3'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/Cd.Hg.Te'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/3CH3.In/h3*1H3;'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/In.3H2O/h;3*1H2/q+3;;;/p-3'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/I.W'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/Pt.H/q+1;'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/p+1/i/hD'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/p+1/i/hH'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/p+1/i/hT'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/C5H5N5O/c6-5-9-3-2(4(11)10-5)7-1-8-3/h1H,(H4,6,7,8,9,10,11)'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/C2H4ClNO2/c3-1(4)2(5)6/h1H,4H2,(H,5,6)/p+1/t1-/m1/s1'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/H2/h1H/i1+2T'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/CH2Cl2/c2-1-3/h1H2/i1D2'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/H2/h1H/i1+1D'))
        self.assertTrue(INCHI_RE.match(u'InChI=1S/H2O4S/c1-5(2,3)4/h(H2,1,2,3,4)/i/hD2'))

    def test_smiles(self):
        self.assertTrue(SMILES_RE.match(u'S=S'))
        self.assertTrue(SMILES_RE.match(u'P1P=P1'))
        self.assertTrue(SMILES_RE.match(u'[V].[Cu+2]'))
        self.assertTrue(SMILES_RE.match(u'O'))
        self.assertTrue(SMILES_RE.match(u'CC1=C(SC=N1)C=CC2=C(NC(SC2)C(C(=O)O)NC(=O)C(=NOC)C3=CSC(=N3)N)C(=O)O'))
        self.assertTrue(SMILES_RE.match(u'C1=CC=C(C=C1)C2=CC=C(C=C2)C3=NN=C(O3)C4=CC=CC=C4'))
        self.assertTrue(SMILES_RE.match(u'CC(=O)OO'))
        self.assertTrue(SMILES_RE.match(u'CCCCCCCC/C=C\CCCCCCCCN'))
        self.assertTrue(SMILES_RE.match(u'C[N+](C)(C)CCCCCC[N+](C)(C)C.[Br-]'))
        self.assertTrue(SMILES_RE.match(u'C([C@H](C(=O)O)N)F'))
        self.assertTrue(SMILES_RE.match(u'[Ru]'))
        self.assertTrue(SMILES_RE.match(u'[S-2].[Cu+2].[Cu+2]'))
        self.assertTrue(SMILES_RE.match(u'[Cd]=[Te]'))
        self.assertTrue(SMILES_RE.match(u'C1C[C@H](OC1)C(=O)O'))
        self.assertTrue(SMILES_RE.match(u'C(=O)(O)[O-].[OH-].[Zn+2]'))
        self.assertTrue(SMILES_RE.match(u'N#N'))
        self.assertTrue(SMILES_RE.match(u'[HH]'))
        self.assertTrue(SMILES_RE.match(u'[Li+].[Li+].[O-][Ti](=O)[O-]'))
        self.assertTrue(SMILES_RE.match(u'[F-]'))
        self.assertTrue(SMILES_RE.match(u'CC(C)[C@@H](C(=O)O)N'))
        self.assertTrue(SMILES_RE.match(u'CC(C)C(C#C)O'))
        self.assertTrue(SMILES_RE.match(u'CCCC#N'))
        self.assertTrue(SMILES_RE.match(u'C(/C=C\O)Cl'))


class TestChemTokenizer(unittest.TestCase):
    """Test ChemTokenizer.

    Some of these unit tests are taken from the OSCAR4 Tokenizer, developed by the Murray-Rust research group at the
    Unilever Centre for Molecular Science Informatics, University of Cambridge and released under the Artistic License
    2.0. See https://bitbucket.org/wwmm/oscar4 for more information.

    """

    def setUp(self):
        self.t = ChemTokenizer()

    def test_sentence(self):
        self.assertEqual([[u'The', u'quick', u'brown', u'fox', u'jumps', u'over',  u'the', u'lazy', u'dog']],
                         self.t.tokenize(u'The quick brown fox jumps over the lazy dog'))
        self.assertEqual([[u'On', u'a', u'$50,000', u'mortgage', u'of', u'30', u'years', u'at', u'8', u'percent',
                          u',', u'the', u'monthly', u'payment', u'would', u'be', u'$366.88', u'.']],
                         self.t.tokenize(u'On a $50,000 mortgage of 30 years at 8 percent, '
                                         u'the monthly payment would be $366.88.'))
        self.assertEqual([[u'I', u'bought', u'these', u'items', u':', u'books', u',', u'pencils', u',',
                          u'and', u'pens', u'.']],
                         self.t.tokenize(u'I bought these items: books, pencils, and pens.'))
        self.assertEqual([[u'Hello', u'there', u'.'], [u'Second', u'Sentence', u'.'], [u'More', u'stuff', u'?'],
                          [u'Yes', u'there', u'is', u'!'], [u'Wow', u'.']],
                         self.t.tokenize(u'Hello there. Second Sentence. More stuff? Yes there is! Wow.'))

    def test_sentence_end(self):
        self.assertEqual([[u'upon', u'addition', u'of', u'Ni(II)', u';']], self.t.tokenize(u'upon addition of Ni(II);'))
        self.assertEqual([[u'upon', u'addition', u'of', u'Ni(II)', u'.']], self.t.tokenize(u'upon addition of Ni(II).'))
        self.assertEqual([[u'complexes', u'in', u'THF', u'(', u'ii', u')', u'.']], self.t.tokenize(u'complexes in THF (ii).'))
        self.assertEqual([[u'complexes', u'in', u'THF', u'(', u'ii', u')', u',']], self.t.tokenize(u'complexes in THF (ii),'))
        self.assertEqual([[u'measured', u'at', u'303', u'K', u'.']], self.t.tokenize(u'measured at 303 K.'))
        self.assertEqual([[u'Sentence', u'trails', u'off', u'…']], self.t.tokenize(u'Sentence trails off…'))
        self.assertEqual([[u'Sentence', u'trails', u'off', u'...']], self.t.tokenize(normalize(u'Sentence trails off…')))
        self.assertEqual([[u'in', u'the', u'AUC', u'.']], self.t.tokenize(normalize(u'in the AUC.')))
        self.assertEqual([[u'at', u'3', u'T', u'.'], [u'In']], self.t.tokenize(normalize(u'at 3 T. In')))
        self.assertEqual([[u'for', u'lane', u'no.', u'11', u'.'], [u'Lane', u'1']], self.t.tokenize(normalize(u'for lane no. 11. Lane 1')))
        self.assertEqual([[u'under', u'A.', u'M.', u'1.5', u'illumination']], self.t.tokenize(normalize(u'under A. M. 1.5 illumination')))
        self.assertEqual([[u'space', u'group', u'P', u'(', u'No.', u'2', u')', u'.']], self.t.tokenize(normalize(u'space group P (No. 2).')))

    def test_abbreviations(self):
        self.assertEqual([[u'(', u'ca.', u'30', u'mL', u')']], self.t.tokenize(u'(ca. 30 mL)'))
        self.assertEqual([[u'Elements', u',', u'e.g.', u'calcium']], self.t.tokenize(u'Elements, e.g. calcium'))

    def test_brackets(self):
        self.assertEqual([[u'NaOH', u'(', u'aq', u')']], self.t.tokenize(u'NaOH(aq)'))
        self.assertEqual([[u'HCl', u'(', u'g', u')']], self.t.tokenize(u'HCl(g)'))
        self.assertEqual([[u'5(g)']], self.t.tokenize(u'5(g)'))
        self.assertEqual([[u'a', u')', u'UV-vis', u'spectrum', u'.']], self.t.tokenize(u'a) UV-vis spectrum.'))
        self.assertEqual([[u'(', u'c', u')', u'-', u'(', u'e', u')']], self.t.tokenize(u'(c)-(e)'))
        self.assertEqual([[u'THF', u'(', u'i', u')', u',', u'toluene', u'(', u'iii', u')']],
                         self.t.tokenize(u'THF (i), toluene (iii)'))
        self.assertEqual([[u'buffer', u'(', u'pH', u'7.4', u')', u'.']], self.t.tokenize(u'buffer (pH 7.4).'))

    def test_hyphens(self):
        self.assertEqual([[u'EA-', u'or', u'BA', u'-', u'modified', u'HPEI']],
                         self.t.tokenize(u'EA- or BA-modified HPEI'))
        self.assertEqual([[u'1-butanol']], self.t.tokenize(u'1-butanol'))
        self.assertEqual([[u'butan-1-ol']], self.t.tokenize(u'butan-1-ol'))
        self.assertEqual([[u'trans-but-2-ene']], self.t.tokenize(u'trans-but-2-ene'))
        self.assertEqual([[u'phosphinin-2(1H)-one']], self.t.tokenize(u'phosphinin-2(1H)-one'))
        self.assertEqual([[u'tetra-n-butylammonium', u'perchlorate']], self.t.tokenize(u'tetra-n-butylammonium perchlorate'))
        self.assertEqual([[u'The', u'H', u'-', u'bond', u'contacts']], self.t.tokenize(u'The H-bond contacts'))
        self.assertEqual([[u'spectrum', u'in', u'acetone-d6', u'.']], self.t.tokenize(u'spectrum in acetone-d6.'))
        self.assertEqual([[u'Tetra-n-butylammonium']], self.t.tokenize(u'Tetra-n-butylammonium'))
        self.assertEqual([[u'L-α-amino', u'acids']], self.t.tokenize(u'L-α-amino acids'))
        self.assertEqual([[u'5,8-dihydroxy-7-methoxycoumarin-5-ß-glycopyranoside']], self.t.tokenize(u'5,8-dihydroxy-7-methoxycoumarin-5-ß-glycopyranoside'))
        self.assertEqual([[u'z', u'-', u'position']], self.t.tokenize(u'z - position'))
        self.assertEqual([[u'6a-iso', u'and', u'7a-iso']], self.t.tokenize(u'6a-iso and 7a-iso'))
        self.assertEqual([[u'4-dehydro-β,β-carotenyl']], self.t.tokenize(u'4-dehydro-β,β-carotenyl'))
        self.assertEqual([[u'graphene-w-TiO2']], self.t.tokenize(u'graphene-w-TiO2'))
        self.assertEqual([[u'2,9-di-p-tolyl-1,10-phenanthroline']], self.t.tokenize(u'2,9-di-p-tolyl-1,10-phenanthroline'))
        self.assertEqual([[u'β,β-carotene']], self.t.tokenize(u'β,β-carotene'))
        self.assertEqual([[u'2,9-di-p-tolyl-1,10-phenanthroline']], self.t.tokenize(u'2,9-di-p-tolyl-1,10-phenanthroline'))
        self.assertEqual([[u'ANTH-OXA2t-tBu']], self.t.tokenize(u'ANTH-OXA2t-tBu'))
        self.assertEqual([[u'poly-d(AT)2']], self.t.tokenize(u'poly-d(AT)2'))
        self.assertEqual([[u'E', u'-', u'and', u'C', u'-', u'isomers']], self.t.tokenize(u'E - and C - isomers'))
        self.assertEqual([[u'3α,7α-dihydroxy-5β-cholic', u'acid']], self.t.tokenize(u'3α,7α-dihydroxy-5β-cholic acid'))
        self.assertEqual([[u'5α-androstan-3α,17β-diol']], self.t.tokenize(u'5α-androstan-3α,17β-diol'))
        self.assertEqual([[u'HPEI-star-mPDMS']], self.t.tokenize(u'HPEI-star-mPDMS'))
        self.assertEqual([[u'Non-platinum']], self.t.tokenize(u'Non-platinum'))
        self.assertEqual([[u'[60]fullerene-deoxy-6-(1,4-diiminodiphenyl)-β-cyclodextrin']], self.t.tokenize(u'[60]fullerene-deoxy-6-(1,4-diiminodiphenyl)-β-cyclodextrin'))
        self.assertEqual([[u'tri-s-triazines']], self.t.tokenize(u'tri-s-triazines'))
        self.assertEqual([[u'Bi-functional']], self.t.tokenize(u'Bi-functional'))
        self.assertEqual([[u'π', u'-', u'conjugated']], self.t.tokenize(u'π-conjugated'))
        self.assertEqual([[u'benzene-d6']], self.t.tokenize(u'benzene-d6'))
        self.assertEqual([[u'SDS-PAGE']], self.t.tokenize(u'SDS-PAGE'))
        self.assertEqual([[u'non-doped']], self.t.tokenize(u'non-doped'))
        self.assertEqual([[u'Uv-vis']], self.t.tokenize(u'Uv-vis'))
        self.assertEqual([[u'difluoro-boron-dipyrromethene']], self.t.tokenize(u'difluoro-boron-dipyrromethene'))
        self.assertEqual([[u'boron-tri-aza-anthracene']], self.t.tokenize(u'boron-tri-aza-anthracene'))
        self.assertEqual([[u'LA-BSA']], self.t.tokenize(u'LA-BSA'))
        self.assertEqual([[u'4-bromo-p-quaterphenyl']], self.t.tokenize(u'4-bromo-p-quaterphenyl'))
        self.assertEqual([[u'nitrobenzene-d5']], self.t.tokenize(u'nitrobenzene-d5'))
        self.assertEqual([[u'DMSO-d6']], self.t.tokenize(u'DMSO-d6'))
        self.assertEqual([[u'1,2-dichlorobenzene-d4']], self.t.tokenize(u'1,2-dichlorobenzene-d4'))
        self.assertEqual([[u'THF-d8']], self.t.tokenize(u'THF-d8'))
        self.assertEqual([[u'acetonitrile-d3']], self.t.tokenize(u'acetonitrile-d3'))
        self.assertEqual([[u'dichloromethane-d2']], self.t.tokenize(u'dichloromethane-d2'))
        self.assertEqual([[u'toluene-d8']], self.t.tokenize(u'toluene-d8'))
        self.assertEqual([[u'Tetrachloroethane-d2']], self.t.tokenize(u'Tetrachloroethane-d2'))
        self.assertEqual([[u'DMF-d7']], self.t.tokenize(u'DMF-d7'))
        self.assertEqual([[u'dimethyl', u'sulfoxide-d6']], self.t.tokenize(u'dimethyl sulfoxide-d6'))
        self.assertEqual([[u'pyridine-d5']], self.t.tokenize(u'pyridine-d5'))
        self.assertEqual([[u'tetrachloroethane-d2']], self.t.tokenize(u'tetrachloroethane-d2'))
        self.assertEqual([[u'meta-isomer']], self.t.tokenize(u'meta-isomer'))
        self.assertEqual([[u'X', u'-', u'Bonded']], self.t.tokenize(u'X-Bonded'))
        self.assertEqual([[u'tetra-substituted']], self.t.tokenize(u'tetra-substituted'))
        self.assertEqual([[u'N2', u'-', u'saturated']], self.t.tokenize(u'N2-saturated'))
        self.assertEqual([[u'α-Phenyl-substituted']], self.t.tokenize(u'α-Phenyl-substituted'))
        self.assertEqual([[u'3,6-disubstituted']], self.t.tokenize(u'3,6-disubstituted'))
        self.assertEqual([[u'6,6′-disubstituted']], self.t.tokenize(u'6,6′-disubstituted'))
        self.assertEqual([[u'alkyl-substituted']], self.t.tokenize(u'alkyl-substituted'))

    def test_multihyphens(self):
        self.assertEqual([[u'---']], self.t.tokenize(u'---'))
        self.assertEqual([[u'–––']], self.t.tokenize(u'–––'))
        self.assertEqual([[u'———']], self.t.tokenize(u'———'))
        self.assertEqual([[u'−−−']], self.t.tokenize(u'−−−'))
        self.assertEqual([[u'----']], self.t.tokenize(u'----'))
        self.assertEqual([[u'––––']], self.t.tokenize(u'––––'))
        self.assertEqual([[u'————']], self.t.tokenize(u'————'))
        self.assertEqual([[u'−−−−']], self.t.tokenize(u'−−−−'))

    def test_slashes(self):
        self.assertEqual([[u'methanol', u'/', u'water']], self.t.tokenize(u'methanol/water'))
        self.assertEqual([[u'B3LYP', u'/', u'6-311G(d,p)']], self.t.tokenize(normalize(u'B3LYP/6-311G(d,p)')))

    def test_iron_states(self):
        self.assertEqual([[u'Fe(III)']], self.t.tokenize(u'Fe(III)'))
        self.assertEqual([[u'Fe(iii)']], self.t.tokenize(u'Fe(iii)'))
        self.assertEqual([[u'Fe(3+)']], self.t.tokenize(u'Fe(3+)'))
        self.assertEqual([[u'Fe(0)']], self.t.tokenize(u'Fe(0)'))

    def test_identifiers(self):
        self.assertEqual([[u'4CN']], self.t.tokenize(u'4CN'))
        self.assertEqual([[u'2a']], self.t.tokenize(u'2a'))

    def test_html(self):
        self.assertEqual([[u'<strong>3g</strong>']], self.t.tokenize(normalize(u'<strong>3g</strong>')))
        self.assertEqual([[u'L<strong>a</strong>', u'from', u'<strong>ref. 72</strong>', u'.']],
                         self.t.tokenize(normalize(u'L<strong>a</strong> from <strong>ref. 72</strong>.')))
        self.assertEqual([[u'with', u'Ru(III)[<strong>9b and 10b</strong>]', u'(', u'<strong>ref. 34</strong>', u')']],
                         self.t.tokenize(normalize(u'with Ru(III)[<strong>9b and 10b</strong>] (<strong>ref. 34</strong>)')))

    def test_colon(self):
        self.assertEqual([[u'ethanol', u':', u'water']], self.t.tokenize(u'ethanol:water'))
        self.assertEqual([[u'1', u':', u'2']], self.t.tokenize(u'1:2'))
        self.assertEqual([[u'(', u'foo', u')', u':', u'(', u'bar', u')']], self.t.tokenize(u'(foo):(bar)'))
        self.assertEqual([[u'foo', u')', u':', u'(', u'bar']], self.t.tokenize(u'foo):(bar'))
        self.assertEqual([[u'[Os3(μ-H)(CO)10{μ-η1:η1-(C8H5N)-C-(C5H4N)}]']], self.t.tokenize(u'[Os3(μ-H)(CO)10{μ-η1:η1-(C8H5N)-C-(C5H4N)}]'))
        self.assertEqual([[u'4:7,10:13-diepoxy[15]annulenone']], self.t.tokenize(u'4:7,10:13-diepoxy[15]annulenone'))

    def test_lambda(self):
        self.assertEqual([[u'lambda5-phosphane']], self.t.tokenize(u'lambda5-phosphane'))
        self.assertEqual([[u'λ5-phosphane']], self.t.tokenize(u'λ5-phosphane'))

    def test_chem_names(self):
        self.assertEqual([[u'Tetrahydro', u'furan', u'(', u'THF', u')']], self.t.tokenize(u'Tetrahydro furan (THF)'))
        self.assertEqual([[u'(S)-alanine']], self.t.tokenize(u'(S)-alanine'))
        self.assertEqual([[u'D-glucose']], self.t.tokenize(u'D-glucose'))
        self.assertEqual([[u'spiro[4.5]decane']], self.t.tokenize(u'spiro[4.5]decane'))
        self.assertEqual([[u'β-D-Glucose']], self.t.tokenize(u'β-D-Glucose'))
        self.assertEqual([[u'L-alanyl-L-glutaminyl-L-arginyl-O-phosphono-L-seryl-L-alanyl-L-proline']],
                         self.t.tokenize(u'L-alanyl-L-glutaminyl-L-arginyl-O-phosphono-L-seryl-L-alanyl-L-proline'))
        self.assertEqual([[u'aluminium(3+)']], self.t.tokenize(u'aluminium(3+)'))
        self.assertEqual([[u'1-methyl-2-methylidene-cyclohexane']],
                         self.t.tokenize(u'1-methyl-2-methylidene-cyclohexane'))

    def test_rings(self):
        self.assertEqual([[u"2,2':6',2''-Terphenyl-1,1',1''-triol"]],
                         self.t.tokenize(u"2,2':6',2''-Terphenyl-1,1',1''-triol"))
        self.assertEqual([[u"phenothiazino[3',4':5,6][1,4]oxazino[2,3-i]benzo[5,6][1,4]thiazino[3,2-c]phenoxazine"]],
                         self.t.tokenize(u"phenothiazino[3',4':5,6][1,4]oxazino[2,3-i]benzo[5,6][1,4]thiazino[3,2-c]phenoxazine"))
        self.assertEqual([[u"phenanthro[4,5-bcd:1,2-c']difuran"]], self.t.tokenize(u"phenanthro[4,5-bcd:1,2-c']difuran"))

    def test_saccharide(self):
        self.assertEqual([[u'beta-D-Glucopyranosyl-(1->4)-D-glucose']],
                         self.t.tokenize(u'beta-D-Glucopyranosyl-(1->4)-D-glucose'))

    def test_polymer(self):
        self.assertEqual([[u"poly(2,2'-diamino-5-hexadecylbiphenyl-3,3'-diyl)"]],
                         self.t.tokenize(u"poly(2,2'-diamino-5-hexadecylbiphenyl-3,3'-diyl)"))

    def test_operators(self):
        self.assertEqual([[u'J', u'=', u'8.8']], self.t.tokenize(u'J=8.8'))
        self.assertEqual([[u'CH2=CH2']], self.t.tokenize(u'CH2=CH2'))
        self.assertEqual([[u'mL', u'×', u'3']], self.t.tokenize(u'mL×3'))
        self.assertEqual([[u'3', u'×']], self.t.tokenize(u'3×'))
        self.assertEqual([[u'×', u'3']], self.t.tokenize(u'×3'))
        self.assertEqual([[u'15', u'÷', u'3']], self.t.tokenize(u'15÷3'))
        self.assertEqual([[u'5', u'+', u'3']], self.t.tokenize(u'5+3'))
        self.assertEqual([[u'ESI+']], self.t.tokenize(u'ESI+'))
        self.assertEqual([[u'Ce3+']], self.t.tokenize(u'Ce3+'))

    def test_stereo(self):
        self.assertEqual([[u'(+)-chiraline']], self.t.tokenize(u'(+)-chiraline'))
        self.assertEqual([[u'(-)-chiraline']], self.t.tokenize(u'(-)-chiraline'))
        self.assertEqual([[u'(+-)-chiraline']], self.t.tokenize(u'(+-)-chiraline'))
        self.assertEqual([[u'(±)-chiraline']], self.t.tokenize(u'(±)-chiraline'))

    def test_trademarks(self):
        self.assertEqual([[u'CML', u'(', u'TM', u')']], self.t.tokenize(u'CML(TM)'))
        self.assertEqual([[u'Apple', u'(', u'R', u')']], self.t.tokenize(u'Apple(R)'))

    def test_hyphenbonds(self):
        self.assertEqual([[u'CH3-CH3']], self.t.tokenize(u'CH3-CH3'))
        self.assertEqual([[u'C-C(-N)-C(-O)=O']], self.t.tokenize(u'C-C(-N)-C(-O)=O'))

    def test_nmr(self):
        self.assertEqual([[u'proton-NMR']], self.t.tokenize(u'proton-NMR'))
        self.assertEqual([[u'13C-NMR']], self.t.tokenize(u'13C-NMR'))
        self.assertEqual([[u'1H-NMR']], self.t.tokenize(u'1H-NMR'))

    def test_quantities(self):
        # With normalized text (easy)
        self.assertEqual([[u'contamination', u'of', u'2', u'%', u'Cl2']], self.t.tokenize(normalize(u'contamination of 2% Cl2')))
        self.assertEqual([[u'Placed', u'at', u'a', u'distance', u'of', u'7.2', u'cm', u'.']], self.t.tokenize(normalize(u'Placed at a distance of 7.2cm.')))
        self.assertEqual([[u'Addition', u'of', u'~1.8', u'mg', u'of', u'CaCO3', u'.']], self.t.tokenize(normalize(u'Addition of ~1.8mg of CaCO3.')))
        self.assertEqual([[u'Recorded', u'in', u'HCl', u'(', u'pH', u'2', u')', u'.']], self.t.tokenize(normalize(u'Recorded in HCl (pH2).')))
        self.assertEqual([[u'Experienced', u'a', u'pressure', u'of', u'160', u'kPa', u'.']], self.t.tokenize(normalize(u'Experienced a pressure of 160kPa.')))
        self.assertEqual([[u'Brought', u'to', u'pH', u'10.5', u',', u'gradually', u'.']], self.t.tokenize(normalize(u'Brought to pH10.5, gradually.')))
        self.assertEqual([[u'A', u'volume', u'of', u'24', u'cm3', u'was', u'drained', u'.']], self.t.tokenize(normalize(u'A volume of 24cm3 was drained.')))
        self.assertEqual([[u'2', u'M', u'H2SO4', u'was', u'heated', u'.']], self.t.tokenize(normalize(u'2M H2SO4 was heated.')))
        self.assertEqual([[u'The', u'spectrum', u'was', u'recorded', u'at', u'10', u'°', u'C']], self.t.tokenize(normalize(u'The spectrum was recorded at 10° C')))
        self.assertEqual([[u'The', u'spectrum', u'was', u'recorded', u'at', u'10', u'°', u'C']], self.t.tokenize(normalize(u'The spectrum was recorded at 10°C')))
        self.assertEqual([[u'The', u'spectrum', u'was', u'recorded', u'at', u'10', u'°', u'C']], self.t.tokenize(normalize(u'The spectrum was recorded at 10 °C')))
        self.assertEqual([[u'and', u'≈90', u'°']], self.t.tokenize(normalize(u'and ≈90°')))
        # Without normalized text
        self.assertEqual([[u'contamination', u'of', u'2', u'%', u'Cl2']], self.t.tokenize(u'contamination of 2% Cl2'))
        self.assertEqual([[u'Placed', u'at', u'a', u'distance', u'of', u'7.2', u'cm', u'.']], self.t.tokenize(u'Placed at a distance of 7.2cm.'))
        self.assertEqual([[u'Addition', u'of', u'~1.8', u'mg', u'of', u'CaCO3', u'.']], self.t.tokenize(u'Addition of ~1.8mg of CaCO3.'))
        self.assertEqual([[u'Recorded', u'in', u'HCl', u'(', u'pH', u'2', u')', u'.']], self.t.tokenize(u'Recorded in HCl (pH2).'))
        self.assertEqual([[u'Experienced', u'a', u'pressure', u'of', u'160', u'kPa', u'.']], self.t.tokenize(u'Experienced a pressure of 160kPa.'))
        self.assertEqual([[u'Brought', u'to', u'pH', u'10.5', u',', u'gradually', u'.']], self.t.tokenize(u'Brought to pH10.5, gradually.'))
        self.assertEqual([[u'A', u'volume', u'of', u'24', u'cm3', u'was', u'drained', u'.']], self.t.tokenize(u'A volume of 24cm3 was drained.'))
        self.assertEqual([[u'2', u'M', u'H2SO4', u'was', u'heated', u'.']], self.t.tokenize(u'2M H2SO4 was heated.'))
        self.assertEqual([[u'The', u'spectrum', u'was', u'recorded', u'at', u'10', u'°', u'C']], self.t.tokenize(u'The spectrum was recorded at 10° C'))
        self.assertEqual([[u'The', u'spectrum', u'was', u'recorded', u'at', u'10', u'°', u'C']], self.t.tokenize(u'The spectrum was recorded at 10°C'))
        self.assertEqual([[u'The', u'spectrum', u'was', u'recorded', u'at', u'10', u'°', u'C']], self.t.tokenize(u'The spectrum was recorded at 10 °C'))
        self.assertEqual([[u'and', u'≈90', u'°']], self.t.tokenize(u'and ≈90°'))
        # Non-quantities
        self.assertEqual([[u'B3LYP', u'/', u'6-31g(d)']], self.t.tokenize(normalize(u'B3LYP/6-31g(d)')))
        self.assertEqual([[u'N', u'1s', u'spectra']], self.t.tokenize(u'N 1s spectra'))

    def test_linesymbols(self):
        self.assertEqual([[u'N', u'(', u'■', u')', u',', u'C2', u'(', u'●', u')', u',', u'C3', u'(', u'▲', u')']],
                         self.t.tokenize(u'N(■), C2(●), C3(▲)'))
        self.assertEqual([[u'1a', u'(', u'…', u')', u',', u'2a', u'(', u'.-.-.', u')']],
                         self.t.tokenize(u'1a (…) , 2a (.-.-.)'))
        self.assertEqual([[u'6b', u'(', u'...', u')', u',', u'7b', u'(', u'.-.-.', u')']],
                         self.t.tokenize(u'6b (...) , 7b (.-.-.)'))
        self.assertEqual([[u'6b', u'(', u'...', u')', u',', u'7b', u'(', u'.-.-.', u')']],
                         self.t.tokenize(normalize(u'6b (...) , 7b (.-.-.)')))
        self.assertEqual([[u'benzaldehyde', u'(', u'○', u')']], self.t.tokenize(u'benzaldehyde (○)'))
        self.assertEqual([[u'6', u'(', u'--', u')', u',', u'1', u'(', u'----', u')', u'and', u'3', u'(', u'·····', u')']],
                         self.t.tokenize(u'6 (--), 1 (----) and 3 (·····)'))
        self.assertEqual([[u'6', u'(', u'--', u')', u',', u'1', u'(', u'----', u')', u'and', u'3', u'(', u'·····', u')']],
                         self.t.tokenize(normalize(u'6 (--), 1 (----) and 3 (·····)')))

    def test_bracket_chems(self):
        self.assertEqual([[u'molecules', u'of', u'the', u'[NiL2]', u'complex']], self.t.tokenize(u'molecules of the [NiL2] complex'))
        self.assertEqual([[u'[Et3NBz][FeIIICl4]']], self.t.tokenize(u'[Et3NBz][FeIIICl4]'))
        self.assertEqual([[u'[2PA-Mmim][Tf2N]']], self.t.tokenize(u'[2PA-Mmim][Tf2N]'))
        self.assertEqual([[u'[', u'H2O', u']', u'≈', u'3000', u'ppm']], self.t.tokenize(u'[H2O] ≈ 3000 ppm'))
        self.assertEqual([[u'(', u'[', u'Cu+', u']', u'/', u'[', u'L', u']', u'=', u'3', u')']], self.t.tokenize(u'([Cu+]/[L] = 3)'))
        self.assertEqual([[u'(Ph3PO)(Ph3POH)(HSO4)']], self.t.tokenize(u'(Ph3PO)(Ph3POH)(HSO4)'))
        self.assertEqual([[u'(', u'iron(III)']], self.t.tokenize(u'(iron(III)'))

    def test_chem_formula(self):
        self.assertEqual([[u'(C2H5)4N']], self.t.tokenize(normalize(u'(C2H5)4N')))
        self.assertEqual([[u'(C2H5)4N']], self.t.tokenize(u'(C2H5)4N'))
        self.assertEqual([[u'monomer', u'28M-Py2']], self.t.tokenize(normalize(u'monomer 28M-Py2')))
        self.assertEqual([[u'monomer', u'28M-Py2']], self.t.tokenize(u'monomer 28M-Py2'))
        self.assertEqual([[u'ratio', u'Ag+', u'/', u'nucleoside', u'of', u'3', u':', u'1']], self.t.tokenize(u'ratio Ag+/nucleoside of 3:1'))
        self.assertEqual([[u'[Al(H2L)n]3-']], self.t.tokenize(u'[Al(H2L)n]3-'))
        self.assertEqual([[u'[Fe(CN)5(NO)]2-']], self.t.tokenize(u'[Fe(CN)5(NO)]2-'))

if __name__ == '__main__':
    unittest.main()

