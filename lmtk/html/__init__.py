#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""lmtk.html - Tools for extracting information from HTML documents."""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from .clean import BLOCK_ELEMENTS, INLINE_ELEMENTS, HtmlCleaner
from .meta import extract_metadata

