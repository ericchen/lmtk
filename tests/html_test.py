#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unit tests for html package."""

import unittest

from lmtk.html import HtmlCleaner


class TestClean(unittest.TestCase):

    D1 = '''
        <html>
            <head><title>title</title></head>
            <body>
                Start body<!-- A comment --><script>alert(\'test\');</script><p>This i<span>s</span>s a <strong>test</strong>.
                Test <a href="link">link</a>
            </body>
        </html>
    '''
    C1A = u'title\nStart body\nThis iss a <strong>test</strong>. Test <a href="link">link</a>'
    C1B = u'title\nStart body\nThis iss a <strong>test</strong>. Test <a>link</a>'

    D2 = '<p>First<p>Second<p>Third<p>Fourth<p>Fifth<p>'
    C2 = u'First\nSecond\nThird\nFourth\nFifth'

    def test_clean_html(self):
        """Test clean_html function."""
        clean1 = HtmlCleaner(allowed_tags=['a', 'strong'], allowed_attrs=['href'])
        clean2 = HtmlCleaner(allowed_tags=['a', 'strong'])
        clean3 = HtmlCleaner()
        self.assertEqual(self.C1A, clean1(self.D1))
        self.assertEqual(self.C1B, clean2(self.D1))
        self.assertEqual(self.C2, clean3(self.D2))


if __name__ == '__main__':
    unittest.main()
