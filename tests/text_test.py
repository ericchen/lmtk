#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unit tests for text package."""

import unittest

from lmtk.text import Unhyphenator, normalize, latex_to_unicode, extract_urls, extract_emails


class TestUnhyphenator(unittest.TestCase):

    def setUp(self):
        self.h = Unhyphenator()

    def test_unhyphenate(self):
        """Test unhyphenate function"""
        self.assertEqual('exclamation.', self.h.unhyphenate('excla-', 'mation.'))
        self.assertEqual('crystallization', self.h.unhyphenate('crystal-', 'lization'))
        self.assertEqual('solvatochromic', self.h.unhyphenate('solvato-', 'chromic'))
        self.assertEqual('catalysis,6', self.h.unhyphenate('cata-', 'lysis,6'))
        self.assertEqual('appreciable:', self.h.unhyphenate('appreci-', 'able:'))
        self.assertEqual('Corporation', self.h.unhyphenate('Cor-', 'poration'))
        self.assertEqual('conditions.32', self.h.unhyphenate('con-', 'ditions.32'))
        self.assertEqual('fluorescence', self.h.unhyphenate('fluor-', 'escence'))
        self.assertEqual('FACSIMILE.28', self.h.unhyphenate('FACSI-', 'MILE.28'))
        self.assertEqual('Atkinson', self.h.unhyphenate('Atkin-', 'son'))
        self.assertEqual('ortho-substituent', self.h.unhyphenate('ortho-', 'substituent'))
        self.assertEqual('femtosecond', self.h.unhyphenate('femto-', 'second'))
        self.assertEqual('charge-transfer', self.h.unhyphenate('charge-', 'transfer'))
        self.assertEqual('electron-deficient', self.h.unhyphenate('electron-', 'deficient'))
        self.assertEqual('Smith-Brown', self.h.unhyphenate('Smith-', 'Brown'))
        self.assertEqual('as-synthesized', self.h.unhyphenate('as-', 'synthesized'))
        self.assertEqual('two-dimensionally', self.h.unhyphenate('two-', 'dimensionally'))
        self.assertEqual('non-linear', self.h.unhyphenate('non-', 'linear'))
        self.assertEqual('breakthrough', self.h.unhyphenate('break-', 'through'))
        self.assertEqual('photo-generated', self.h.unhyphenate('photo-gen-', 'erated'))
        self.assertEqual(u'phthalocyanines’', self.h.unhyphenate(u'phthalocya-', u'nines’'))

    @unittest.expectedFailure
    def test_unhyphenate_hard(self):
        # Consider splitting on ()/\ before attempting join?
        self.assertEqual('hexaaquairidium(iii)', self.h.unhyphenate('hexaaquairid-', 'ium(iii)'))
        self.assertEqual('toluene/cyclohex-ane', self.h.unhyphenate('toluene/cyclohex', 'ane'))
        self.assertEqual('dipolarity/polarizability.', self.h.unhyphenate('dipolar-', 'ity/polarizability.'))


class TestNormalization(unittest.TestCase):

    def test_normalize(self):
        """Test normalize function."""
        # Weird control characters
        self.assertEqual(u'The quick brown fox jumped', normalize(u'The\u0003 quick br\u0005own fo\u0008x jumped'))
        # Unusual whitespace characters
        self.assertEqual(u'The quick brown fox jumped', normalize(u'The\u00A0quick\u2000brown\u2008fox\u000Bjumped'))
        # u2024 instead of full stop
        self.assertEqual(u'www.bbc.co.uk', normalize(u'www\u2024bbc\u2024co\u2024uk'))


class TestLaTeX(unittest.TestCase):

    def test_latex_to_unicode_names(self):
        self.assertEqual(u'Bernd van Linder', latex_to_unicode('Bernd {van Linder}', capitalize='name'))
        self.assertEqual(u'Bernd van Linder', latex_to_unicode('Bernd van Linder', capitalize='name'))
        self.assertEqual(u'John-Jules Ch. Meyer', latex_to_unicode('{John-Jules Ch.} meyer', capitalize='name'))
        self.assertEqual(u'Eijkhof, Frank van den', latex_to_unicode('eijkhof, frank {v}an {d}en', capitalize='name'))
        self.assertEqual(u'Feng, Wen-Mei Hwu', latex_to_unicode('Feng, Wen-mei Hwu', capitalize='name'))
        self.assertEqual(u'Feng, Wen-mei Hwu', latex_to_unicode('Feng, Wen{-mei} Hwu', capitalize='name'))
        self.assertEqual(u'McCartney, Paul', latex_to_unicode('McCartney, Paul', capitalize='name'))
        self.assertEqual(u'Leo MacGarry', latex_to_unicode('Leo MacGarry', capitalize='name'))
        self.assertEqual(u'Patrick O\'Mahoney', latex_to_unicode('Patrick O\'Mahoney', capitalize='name'))
        self.assertEqual(u'O\'Boyle, Jim', latex_to_unicode('O\'Boyle, Jim', capitalize='name'))


    def test_latex_to_unicode_titles(self):
        self.assertEqual(u'A guide for LMTK', latex_to_unicode('A Guide For {LMTK}', capitalize='sentence'))
        self.assertEqual(u'A Guide for LMTK', latex_to_unicode('A Guide For {LMTK}', capitalize='title'))
        self.assertEqual(u'A Guide for LMTK', latex_to_unicode('A Guide For {LMTK}', capitalize='title'))

    def test_latex_to_unicode_math(self):
        self.assertEqual(u'[g,f]-colorings of Partial k-trees',
                         latex_to_unicode('$[g,f]$-colorings of Partial $k$-trees', capitalize='title'))
        self.assertEqual(u'On K_3,3-free or K_5-free Graphs',
                         latex_to_unicode('On {$K_{3,3}$}-free or {$K_5$}-free graphs', capitalize='title'))
        self.assertEqual(u'Clique-width \u22643 Graphs',
                         latex_to_unicode('clique-width $\\leq 3$ graphs', capitalize='title'))
        self.assertEqual(u'An O(n^2.5) Algorithm',
                         latex_to_unicode('An {O}($n^{2.5}$) Algorithm', capitalize='title'))
        self.assertEqual(u'An n \xd7 N Board',
                         latex_to_unicode('an $n \\times n$ board', capitalize='title'))
        self.assertEqual(u'Of k-trees Is O(k)',
                         latex_to_unicode('of \\mbox{$k$-trees} is {$O(k)$}', capitalize='title'))


class TestExtraction(unittest.TestCase):

    def test_extract_urls(self):
        """Test extract_urls function."""
        self.assertEqual([u'example.com/test', u'google.ca:80/hello'],
                         extract_urls('Go to example.com/test. (Or google.ca:80/hello.)'))
        self.assertEqual([u'http://bit.ly/17YdfI9', u'bit.ly/17YdfI9'],
                         extract_urls('Check out http://bit.ly/17YdfI9 and bit.ly/17YdfI9'))

    def test_extract_emails(self):
        """Test extract_urls function."""
        self.assertEqual([u'matt+test@example.com', u'test%what@example.com'],
                         extract_emails('Send to <matt+test@example.com> or <test%what@example.com>'))
        self.assertEqual([u'example@example.com'],
                         extract_emails('The email is example@example.com.'))
        self.assertEqual([u'matt@server.department.company.ac.uk'],
                         extract_emails('What about <matt@server.department.company.ac.uk>?'))
        self.assertEqual([],
                         extract_emails('Invalid - matt@me...com, hithere@ex*ample.com'))


if __name__ == '__main__':
    unittest.main()
