LMTK: Literature Mining Toolkit
===============================

LMTK is a collection of tools for extracting information from the scientific literature using python. 

It is made up of the following packages:

- lmtk.scrape: Tools for scraping information from the web.
- lmtk.pdf: Tools for dealing with PDF documents.
- lmtk.html: Tools for dealing with HTML documents.
- lmtk.bib: Tools for dealing with bibliographic information.
- lmtk.chem: Chemistry-specific tools.

Dependencies
------------

Install dependencies using pip::

    pip install six
    pip install lxml
    pip install beautifulsoup4
    pip install requests
    pip install scrapy

Installation
------------

Download or clone the source, then use::

    python setup.py install
