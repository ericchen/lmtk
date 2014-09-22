#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unit tests for bib package."""

import unittest

from lmtk.bib import BibtexParser, PersonName


class TestBibtexParser(unittest.TestCase):

    maxDiff = None

    bib1 = '''@Article{C3CE27013K,
author ="Zakharov, Boris A. and Losev, Evgeniy A. and Boldyreva, Elena V.",
title  ="Polymorphism of {"}glycine-glutaric acid{"} co-crystals: the same phase at low temperatures and high pressures",
journal  ="CrystEngComm",
year  ="2013",
volume  ="15",
issue  ="9",
pages  ="1693-1697",
publisher  ="The Royal Society of Chemistry",
doi  ="10.1039/C3CE27013K",
url  ="http://dx.doi.org/10.1039/C3CE27013K"}
'''

    bib1a = {
        u'publisher': u'The Royal Society of Chemistry',
        u'doi': u'10.1039/C3CE27013K',
        u'title': u'Polymorphism of "glycine-glutaric acid" co-crystals: the same phase at low temperatures and high pressures',
        u'issue': u'9',
        u'journal': u'CrystEngComm',
        u'author': [{u'middlename': u'A', u'lastname': u'Zakharov', u'name': u'Boris A Zakharov', u'firstname': u'Boris'},
                    {u'middlename': u'A', u'lastname': u'Losev', u'name': u'Evgeniy A Losev', u'firstname': u'Evgeniy'},
                    {u'middlename': u'V', u'lastname': u'Boldyreva', u'name': u'Elena V Boldyreva', u'firstname': u'Elena'}],
        u'pages': u'1693-1697',
        u'volume': u'15',
        u'link': u'http://dx.doi.org/10.1039/C3CE27013K',
        u'year': u'2013',
        u'type': u'article',
        u'id': u'C3CE27013K'
    }

    bib2 = '''@Article{C3RA40330K,
author ="Mutlu, Hatice and Hofsa[German sz ligature}, Robert and Montenegro, Rowena E. and Meier, Michael A. R.",
title  ="Self-metathesis of fatty acid methyl esters: full conversion by choosing the appropriate plant oil",
journal  ="RSC Adv.",
year  ="2013",
volume  ="3",
issue  ="15",
pages  ="4927-4934",
publisher  ="The Royal Society of Chemistry",
doi  ="10.1039/C3RA40330K",
url  ="http://dx.doi.org/10.1039/C3RA40330K"}
'''

    bib2a = {u'publisher': u'The Royal Society of Chemistry',
             u'doi': u'10.1039/C3RA40330K',
             u'title': u'Self-metathesis of fatty acid methyl esters: full conversion by choosing the appropriate plant oil',
             u'issue': u'15',
             u'journal': u'RSC Adv.',
             u'author': [{u'middlename': u'Robert', u'lastname': u'Mutlu', u'name': u'Hatice And Hofsa[german Sz Ligature Robert Mutlu', u'firstname': u'Hatice And Hofsa[german Sz Ligature'},
                         {u'middlename': u'E', u'lastname': u'Montenegro', u'name': u'Rowena E Montenegro', u'firstname': u'Rowena'},
                         {u'middlename': u'A R', u'lastname': u'Meier', u'name': u'Michael A R Meier', u'firstname': u'Michael'}],
             u'pages': u'4927-4934',
             u'volume': u'3',
             u'link': u'http://dx.doi.org/10.1039/C3RA40330K',
             u'year': u'2013',
             u'type': u'article',
             u'id': u'C3RA40330K'
    }

    def test_bib1(self):
        """Test BibTeX example 1."""
        bib = BibtexParser(self.bib1)
        bib.parse()
        self.assertEqual(self.bib1a, bib.records_list[0])

    def test_bib2(self):
        """Test BibTeX example 2."""
        bib = BibtexParser(self.bib2)
        bib.parse()
        self.assertEqual(self.bib2a, bib.records_list[0])

    def test_parse_names(self):
        res = [{u'lastname': u'van Linder', u'name': u'Bernd van Linder', u'firstname': u'Bernd'},
               {u'lastname': u'Meyer', u'name': u'John-Jules Ch Meyer', u'firstname': u'John-Jules Ch'},
               {u'middlename': u'van den', u'lastname': u'Eijkhof', u'name': u'Frank van den Eijkhof', u'firstname': u'Frank'}]
        self.assertEqual(res, BibtexParser.parse_names(u'Bernd {van Linder} and {John-Jules Ch.} Meyer and Eijkhof, Frank {v}an {d}en'))


        res = [{u'lastname': u'Smith', u'name': u'John "Jack and Jill" Smith', u'firstname': u'John', u'nickname': u'Jack and Jill'},
               {U'lastname': u'Thompson', u'name': u'Tom Thompson', u'firstname': u'Tom'}]
        self.assertEqual(res, BibtexParser.parse_names(u'John "Jack {and} Jill" Smith and Tom Thompson'))


class TestPersonName(unittest.TestCase):

    def test_names(self):
        """Test person name parser."""
        res = {
            u'lastname': u'Smith',
            u'nickname': u'Jack and Jill',
            u'name': u'John "Jack and Jill" Smith',
            u'firstname': u'John'
        }
        self.assertEqual(res, PersonName(u'John "Jack and Jill" Smith'))

        res = {
            u'lastname': u'Cierva y Codorn\xedu',
            u'prefix': u'de la',
            u'name': u'Juan de la Cierva y Codorn\xedu',
            u'firstname': u'Juan'
        }
        self.assertEqual(res, PersonName(u'Juan de la Cierva y Codorníu'))

        res = {
            u'lastname': u'Beethoven',
            u'prefix': u'von',
            u'name': u'Ludwig von Beethoven',
            u'firstname': u'Ludwig'
        }
        self.assertEqual(res, PersonName(u'Ludwig von Beethoven'))
        self.assertEqual(res, PersonName(u'von Beethoven, Ludwig'))
        self.assertEqual(res, PersonName(u'Beethoven, Ludwig von'))

        res = {
            u'suffix': u'Jr',
            u'firstname': u'George',
            u'middlename': u'Oscar',
            u'lastname': u'Bluth',
            u'nickname': u'Gob',
            u'name': u'George Oscar "Gob" Bluth Jr'
        }
        self.assertEqual(res, PersonName(u'George Oscar “Gob” Bluth, Jr.'))
        self.assertEqual(res, PersonName(u'George Oscar \'Gob\' Bluth, Jr.'))
        self.assertEqual(res, PersonName(u'George Oscar "Gob" Bluth, Jr.'))

        res = {
            u'middlename': u'Paul',
            u'lastname': u'Jones',
            u'name': u'John Paul Jones',
            u'firstname': u'John'
        }
        self.assertEqual(res, PersonName(u'John Paul Jones'))
        self.assertEqual(res, PersonName(u'Jones, John Paul'))

        res = {
            u'lastname': u'Brinch Hansen',
            u'name': u'Per Brinch Hansen',
            u'firstname': u'Per'
        }
        self.assertEqual(res, PersonName(u'Brinch Hansen, Per'))

        res = {
            u'middlename': u'Louis Xavier Joseph',
            u'lastname': u'Vallee Poussin',
            u'prefix': u'de la',
            u'name': u'Charles Louis Xavier Joseph de la Vallee Poussin',
            u'firstname': u'Charles'
        }
        self.assertEqual(res, PersonName(u'Charles Louis Xavier Joseph de la Vallee Poussin'))

        res = {
            u'lastname': u'Ford',
            u'suffix': u'Jr III',
            u'firstname': u'Henry',
            u'name': u'Henry Ford Jr III'
        }
        self.assertEqual(res, PersonName(u'Henry Ford, Jr., III'))
        self.assertEqual(res, PersonName(u'Henry Ford Jr. III'))
        self.assertEqual(res, PersonName(u'Ford, Jr., III, Henry'))

        res = {
            u'middlename': u'L',
            u'lastname': u'Steele Jr',
            u'name': u'Guy L Steele Jr',
            u'firstname': u'Guy'
        }
        self.assertEqual(res, PersonName(u'{Steele Jr.}, Guy L.', from_bibtex=True))
        self.assertEqual(res, PersonName(u'Guy L. {Steele Jr.}', from_bibtex=True))

        res = {
            u'middlename': u'Fitzgerald',
            u'lastname': u'Kennedy',
            u'nickname': u'Jack',
            u'name': u'John Fitzgerald "Jack" Kennedy',
            u'firstname': u'John'
        }
        self.assertEqual(res, PersonName(u'John Fitzgerald "Jack" Kennedy'))

    def test_capitalization(self):
        p = PersonName(u'juan q. xavier velasquez y garcia', from_bibtex=True)
        self.assertEqual(u'Juan Q Xavier Velasquez y Garcia', p.name)

    def test_equality(self):
        self.assertEqual(PersonName(u'Henry Ford, Jr., III'), PersonName(u'Ford, Jr., III, Henry'))
        self.assertEqual(PersonName(u'Jones, John Paul'), PersonName(u'John Paul Jones'))

    def test_could_be(self):
        self.assertTrue(PersonName(u'G. Bluth').could_be(PersonName(u'George Oscar Bluth Jr.')))
        self.assertFalse(PersonName(u'G. Bluth Sr.').could_be(PersonName(u'George Oscar Bluth Jr.')))
        self.assertFalse(PersonName(u'Oscar Bluth').could_be(PersonName(u'George Oscar Bluth')))
        self.assertTrue(PersonName(u'J F K').could_be(PersonName(u'John Fitzgerald "Jack" Kennedy')))


if __name__ == '__main__':
    unittest.main()
