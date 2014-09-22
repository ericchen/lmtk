#!/usr/bin/env python
"""pdfextract - Python interface for the pdf-extract ruby tool

pdf-extract is a tool that can extract various areas of text from a PDF, especially a scholarly article PDF. It performs
structural analysis to determine column bounds, headers, footers, sections, titles and so on. It can analyse and
categorise sections into reference and non-reference sections and can split reference sections into individual
references.

https://github.com/CrossRef/pdfextract

"""

import logging
import os
import subprocess
import xml.etree.ElementTree as ET

from lmtk.store import config, fs
from lmtk.utils import find_binary, find_file


class PDFExtract(object):
    """Base class for using pdf-extract to extract information from PDF files.

    Initialise with a PDF file or the path to a PDF file.

        pdf = PDFExtract('/path/to/example.pdf')

    This class requires that you have pdf-extract installed (https://github.com/CrossRef/pdfextract).

    If pdf-extract was installed using RVM, you need to point lmtk towards your custom environment (use `rvm current`):

        from lmtk import config
        config['rvm'] = 'ruby-2.0.0-p195@lmtk'

    Alternatively, for a standard ruby environment, but with a non-standard location for the pdf-extract executable,
    just specify the path (use `which pdf-extract`):

        from lmtk import config
        config['pdf-extract_path'] = '/path/to/pdf-extract'

    You can also specify these details every time you use PDFExtract if you don't want to set the config:

        pdf = PDFExtract('/path/to/example.pdf', rvm='ruby-2.0.0-p195@lmtk')
        pdf = PDFExtract('/path/to/example.pdf', pdf-extract_path='/path/to/pdf-extract')

    """

    def __init__(self, pdffile, pdfextract_path=None):
        """Read the PDF and convert to XML using pdf-extract

        pdffile: path string or file object for the PDF
        pdfextract_path: optional path to the pdf-extract executable.

        """
        try:
            path = os.path.abspath(pdffile)
        except AttributeError:
            fskey = fs.save(pdffile)
            path = fs.fpath(fskey)
        if pdfextract_path is None:
            pdfextract_path = find_binary('pdf-extract')

        # Set up custom environment if using RVM
        customenv = os.environ.copy()
        if 'rvm' in config:
            rvm = config['rvm']
            try:
                envpath = find_file('~/.rvm/environments/%s' % rvm)
            except LookupError:
                try:
                    envpath = find_file('/usr/local/rvm/environments/%s' % rvm)
                except LookupError:
                    raise LookupError('RVM specified in config (%s) cannot be found' % rvm)
            p = subprocess.Popen('. %s; env' % envpath, stdout=subprocess.PIPE, shell=True)
            for line in p.stdout:
                (key, _, value) = line.partition('=')
                customenv[key] = value.rstrip()

        # Run the pdf-extract executable
        p = subprocess.Popen([pdfextract_path, 'extract', '--titles', '--references', '--sections', '--no-lines', path],
                             stdout=subprocess.PIPE, env=customenv)
        output = p.communicate()[0]
        self.tree = ET.fromstring(output.encode('utf-8'))
        self.xml = output

    @property
    def title(self):
        """Return the title of the article."""
        return ' '.join([e.text for e in self.tree.findall('title')])

    @property
    def sections(self):
        """Return a list of each text section in the article"""
        return [e.text for e in self.tree.findall('section')]

    @property
    def fulltext(self):
        """Return the entire text contents of the PDF.

        This is a crude dump of all the successfully extracted text, without any formatting or markup. It usually
        contains a lot of text that is often undesirable, such as page numbers and headers and footers.
        """
        return '\n\n'.join([e.text for e in self.tree.findall('section')])

    @property
    def references(self):
        """Return a list of all references in the article."""
        refs = []
        for refel in self.tree.findall('reference'):
            ref = {'citation': refel.text}
            if 'order' in refel.attrib:
                ref['number'] = refel.attrib['order']
            refs.append(ref)
        return refs

    @property
    def numpages(self):
        """Return the number of pages in the PDF"""
        num = 0
        for el in self.tree.findall('.//*[@page]'):
            if int(el.attrib['page']) > num:
                num = int(el.attrib['page'])
        return num


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    with open('../../samples/bmc.pdf', 'rb') as f:
        p = PDFExtract(f)
    #print p.xml
    print p.title
    print p.sections
    #print p.fulltext
    print p.references
    print p.numpages
