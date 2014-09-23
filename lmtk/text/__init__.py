#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""lmtk.text - Tools for dealing with text."""

import os
import re
import string
import sys
import unicodedata

from lmtk.utils import find_data
from lmtk.text import latex


def to_unicode(text):
    """Return the given string as unicode."""
    if isinstance(text, str):
        for encoding in (sys.getdefaultencoding(), 'utf-8', 'iso-8859-1', 'cp1252', 'iso-8859-15' 'cp1255', 'cp1250'):
            try:
                return unicode(text, encoding)
            except UnicodeDecodeError:
                pass
        return unicode(text, 'utf-8', errors='ignore')
    return unicode(text)


def to_str(text):
    """Return the given string as a bytestring."""
    if isinstance(text, unicode):
        if sys.stdout.encoding:
            return text.encode(sys.stdout.encoding)
        return text.encode('utf-8')
    return str(text)


u = to_unicode
s = to_str


def latex_to_unicode(text, capitalize=False):
    """Replace LaTeX entities with the equivalent unicode and optionally capitalize.

    :param text: The LaTeX string to be converted
    :param capitalize: Can be 'sentence', 'name', 'title', 'upper', 'lower'
    """
    text = u(text)
    if capitalize:
        res = []
        brac_count = 0
        for i, c in enumerate(text):
            if c == '{':
                brac_count += 1
            if c == '}':
                brac_count -= 1
            if brac_count > 0:
                res.append(c)
            elif capitalize == 'upper' or (i == 0 and not capitalize == 'lower'):
                res.append(c.upper())
            elif capitalize == 'sentence' and (i > 2 and text[i - 1] == ' ' and text[i - 2] == '.'):
                res.append(c.upper())
            elif (capitalize == 'name' and text[i - 1] in [' ', '-']) or (capitalize == 'title' and text[i - 1] == ' '):
                nextword = text[i:].split(' ', 1)[0].rstrip(string.punctuation)
                nextword = nextword[:1].lower() + nextword[1:] if text else ''
                if capitalize == 'name' and nextword in NAME_SMALL:
                    res.append(c.lower())
                elif capitalize == 'title' and nextword in SMALL:
                    res.append(c.lower())
                else:
                    res.append(c.upper())
            elif capitalize == 'name' and c == c.upper():
                n1 = text[i - 1] if i > 0 else None
                n2 = text[i - 2] if i > 1 else None
                n3 = text[i - 3] if i > 2 else None
                n4 = text[i - 4] if i > 3 else None
                if n2 == 'M' and n1 == 'c' and (not n3 or n3 == ' '):
                    res.append(c)  # McCartney
                elif n2 == 'O' and n1 == '\'' and (not n3 or n3 == ' '):
                    res.append(c)  # O'Boyle
                elif n3 == 'M' and n2 == 'a' and n1 == 'c' and (not n4 or n4 == ' '):
                    res.append(c)  # MacGarry
                else:
                    res.append(c.lower())
            else:
                res.append(c.lower())
        text = ''.join(res)
    if any(i in text for i in ['\\', '{', '}', '$', '&', '%', '#', '_']):
        for k, v in latex.LATEX_MAPPINGS.iteritems():
            text = text.replace(k, v)
        for k, v in latex.LATEX_SUB_MAPPINGS.iteritems():
            text = text.replace(k, v)
        for mod in [u'mathbb', u'mathbf', u'mathbit', u'mathfrak', u'mathrm', u'mathscr', u'mathsf',
                    u'mathsfbf', u'mathsfbfsl', u'mathsfsl', u'mathsl', u'mathslbb', u'mathtt']:
            text = re.sub(ur'\\%s\{([\\\w]+)\}' % mod, ur'\1', text)
        for k, v in latex.LATEX_SUB_SUB_MAPPINGS.iteritems():
            text = text.replace(k, v)
        for k, v in latex.LATEX_COMBINING_CHARS.iteritems():
            text = re.sub(ur'%s\{?(\w)\}?' % k, ur'\1%s' % v, text)
        text = re.sub(ur'\\noopsort\{.*?\}', ur'', text)
        text = re.sub(ur'\\path\|(.*?)\|', ur'\1', text)
        text = re.sub(ur'(?<!\\)[{}$]', ur'', text)
        text = re.sub(ur'\\([{}$&_])', ur'\1', text)
    text = normalize(text, collapse=False)
    return text


def normalize(text, form='NFKC', collapse=True):
    """Normalize unicode, hyphens, whitespace.

    :param text: The string to normalize.
    :param form: Normal form for unicode normalization.
    :param collapse: Whether to collapse tabs and newlines down to spaces.

    By default, the normal form NFKC is used for unicode normalization. This applies a compatibility decomposition,
    under which equivalent characters are unified, followed by a canonical composition. See Python docs for information
    on normal forms: http://docs.python.org/2/library/unicodedata.html#unicodedata.normalize
    """

    # Normalize to canonical unicode (using NKFC by default)
    text = unicodedata.normalize(form, u(text))

    # Strip out any control characters (they occasionally creep in somehow)
    for control in CONTROLS:
        text = text.replace(control, u'')

    # Normalize hyphens (unify all dash, minus and hyphen characters, remove soft hyphens)
    for hyphen in HYPHENS:
        text = text.replace(hyphen, u'-')
    text = text.replace(u'\u00AD', u'')

    # Normalize separate double quotes
    text = text.replace(u'"‘', u'“').replace(u'’\'', u'”').replace(u'\'\'', u'”').replace(u'``', u'“')
    # Possible further normalization to ascii:
    # \u201c \u201d -> \u0022
    # \u2018 \u2019 \u0060 \u00b4 -> \u0027

    # Normalize unusual whitespace not caught by unicodedata
    text = text.replace(u'\u000B', u' ').replace(u'\u000C', u' ').replace(u'\u0085', ' ')
    text = text.replace(u'\u2028', u'\n').replace(u'\u2029', u'\n').replace('\r\n', '\n').replace('\r', '\n')
    if collapse:
        text = ' '.join(text.split())
    else:
        # TODO: If not collapse, just normalize newlines to '\n'
        pass
    return text


def dequirk_string(text):
    """Excessive string normalization.

    This is useful when doing fuzzy string comparisons. A common use case is to run this before calculating the
    Levenshtein distance between two strings, so that only "important" differences are counted.
    """
    # Lowercase and normalize unicode
    text = normalize(text.lower())
    # Remove all whitespace
    text = ''.join(text.split())
    # Convert all quotes and primes to '
    for quote in QUOTES | PRIMES:
        text = text.replace(quote, u'\'')
    # Replace all brackets with regular brackets
    for ob in {'(', '<', '[', '{', '&lt;'}:
        text = text.replace(ob, '(')
    for cb in {')', '>', ']', '}', '&gt;'}:
        text = text.replace(cb, '(')
    return text


def levenshtein(s1, s2, allow_substring=False):
    """Return the Levenshtein distance between two strings.

    The Levenshtein distance (a.k.a "edit difference") is the number of characters that need to be substituted,
    inserted or deleted to transform s1 into s2.

    Setting the `allow_substring` parameter to True allows s1 to be a
    substring of s2, so that, for example, "hello" and "hello there" would have a distance of zero.

    :param s1: The first string
    :param s2: The second string
    :param allow_substring: Whether to allow s1 to be a substring of s2
    :type s1: str
    :type s2: str
    :type allow_substring: bool
    :rtype int
    """
    len1, len2 = len(s1), len(s2)
    lev = []
    for i in range(len1 + 1):
        lev.append([0] * (len2 + 1))
    for i in range(len1 + 1):
        lev[i][0] = i
    for j in range(len2 + 1):
        lev[0][j] = 0 if allow_substring else j
    for i in range(len1):
        for j in range(len2):
            lev[i + 1][j + 1] = min(lev[i][j + 1] + 1, lev[i + 1][j] + 1, lev[i][j] + (s1[i] != s2[j]))
    return min(lev[len1]) if allow_substring else lev[len1][len2]


class Unhyphenator:
    """Unhyphenation algorithms for unwrapping hard-wrapped text."""

    def __init__(self, joins=None):
        """Initialise patterns and exceptions.

        :param joins: A list words that are acceptable to form by joining two components.

        """
        self.joins = joins
        if joins is None:
            with open(find_data(os.path.join('words', 'hyphen_joins.txt')), 'r') as jf:
                self.joins = set(word.strip().lower() for word in jf)

    def unhyphenate(self, part1, part2):
        """Given two word components, return a string with them joined appropriately."""
        part1 = part1.rstrip('-')
        join1 = '%s-%s' % (part1, part2)
        join2 = '%s%s' % (part1, part2)
        p1s = part1.lower().lstrip(u'\'\"`’”“-([{/\\~')
        p2s = part2.lower().rstrip(u'\'\"`’”“-,.:;!?)]}/\\0123456789')
        p2s = re.sub('\'s$', '', p2s)
        j1s = '%s-%s' % (p1s, p2s)
        j2s = '%s%s' % (p1s, p2s)
        # If either comp is not alpha or join with hyphen is in joins list, join with hyphen
        if not re.match('^[a-z-]+$', p1s) or not re.match('^[a-z-]+$', p2s) or j1s in self.joins:
            return join1
        # If join without hyphen is in word list, join without hyphen
        if j2s in self.joins:
            return join2
        return join1

    def unwrap_text(self, text):
        """Unwrap multiple lines of hard-wrapped text, unhyphenating words where applicable."""
        unwrapped = ''
        for line in text.split('\n'):
            if not line.split():
                # Line is whitespace, just add as a new line
                unwrapped += '\n\n'
            elif not unwrapped.split('\n', 1):
                # First line, just add it
                unwrapped += line
            else:
                if not unwrapped.endswith('-'):
                    # Regular line unwrap, add with a space
                    if not unwrapped.endswith('\n'):
                        unwrapped += ' '
                    unwrapped += line
                else:
                    # Hyphenated line unwrap, determine whether to remove hyphen
                    pcomps = unwrapped.rsplit(None, 1)
                    lcomps = line.split(' ', 2)
                    if lcomps[0] in ['and', 'or'] and len(lcomps) > 1 and '-' in lcomps[1]:
                        # Keep hyphen and add space
                        unwrapped += ' ' + line
                    else:
                        join = unhyphenate(pcomps[-1], lcomps[0])
                        unwrapped = pcomps[0] if len(pcomps) > 1 else ''
                        unwrapped += ' ' + join
                        unwrapped += ' ' + lcomps[1] if len(lcomps) > 1 else ''
                        unwrapped += ' ' + lcomps[2] if len(lcomps) > 2 else ''
        return unwrapped


unhyphenator = Unhyphenator()
unhyphenate = unhyphenator.unhyphenate
unwrap_text = unhyphenator.unwrap_text


def extract_urls(text):
    """Return a list of URLs extracted from the text.

    Works on URLs beginning with http://, https://, www. or ending with a number of common TLDs (not all, given by
    lmtk.text.TLDS). Trailing punctuation and enclosing brackets are automatically stripped out.

    This function is not designed to work on HTML input. For HTML, use BeautifulSoup to extract attributes and text,
    which can then be passed to this function individually.

    """
    text = u(text).replace(u'\u2024', '.')
    words = re.compile(r'(\s+)').split(text)
    urls = []
    for i, word in enumerate(words):
        if '.' in word or ':' in word:
            # Strip off brackets (leave closing bracket if balanced with opening bracket within URL)
            for op, cl in [('(', ')'), ('<', '>'), ('[', ']'), ('&lt;', '&gt;')]:
                if word.startswith(op):
                    word = word[len(op):]
                if word.endswith(cl) and word.count(cl) == word.count(op) + 1:
                    word = word[:-len(cl)]
            # Strip off trailing punctuation
            if any(word.endswith(p) for p in ['.', ',', ':', ';']):
                word = word[:-1]
            # Match word against URL regular expressions
            if URL_START_RE.match(word) or URL_END_RE.search(word):
                urls.append(word)
    return urls


def extract_emails(text):
    """Return a list of email addresses extracted from the string."""
    text = u(text).replace(u'\u2024', '.')
    emails = []
    for m in EMAIL_RE.findall(text):
        emails.append(m[0])
    return emails


def bracket_level(text):
    """Return 0 if string contains balanced brackets or no brackets."""
    level = 0
    for c in text:
        if c in {'(', '[', '{'}:
            level += 1
        elif c in {')', ']', '}'}:
            level -= 1
    return level


def unapostrophe(text):
    """Strip apostrophe and 's' from the end of a string."""
    text = re.sub(r'[%s]s?$' % ''.join(APOSTROPHES), '', text)
    return text


QUOTES = {
    u'\u201a', u'\u201b', u'\u201c', u'\u201d', u'\u201e', u'\u201f', u'\u0022', u'\u2018', u'\u2019', u'\u0060',
    u'\u00b4', u'\u0027'
}
PRIMES = {u'\'', u'`', u'\u2032', u'\u2033', u'\u2034'}
HYPHENS = {u'\u2010', u'\u2011', u'\u2012', u'\u2013', u'\u2014', u'\u2015', u'\u002d', u'\u2212'}
APOSTROPHES = {u'\u0027', u'\u0060', u'\u00b4', u'\u2019'}
CONTROLS = {u'\u0001', u'\u0002', u'\u0003', u'\u0004', u'\u0005', u'\u0006', u'\u0007', u'\u0008'}

SMALL = {
    'a', 'an', 'and', 'as', 'at', 'but', 'by', 'en', 'for', 'if', 'in', 'of', 'on', 'or', 'the', 'to', 'v', 'v', 'via',
    'vs', 'vs'
}

NAME_SMALL = {
    'abu', 'bon', 'bin', 'da', 'dal', 'de', 'del', 'der', 'de', 'di', u'dí', 'ibn', 'la', 'le', 'san', 'st', 'ste',
    'van', 'vel', 'von', 'y'
}

# This isn't every possible TLD, just the most common, to avoid false positives.
TLDS = {
    '.aero', '.asia', '.biz', '.cat', '.com', '.coop', '.edu', '.eu', '.gov', '.info', '.int', '.jobs.', '.mil',
    '.mobi', '.museum', '.name', '.net', '.org', '.pro', '.tel', '.travel', '.xxx', '.ad', '.as', '.ar', '.au', '.br',
    '.bz', '.ca', '.cc', '.cd', '.co', '.ch', '.cn', '.de', '.dj', '.es', '.fr', '.fm', '.it', '.io', '.jp', '.la',
    '.ly', '.me', '.ms', '.nl', '.no', '.nu', '.ru', '.sc', '.se', '.sr', '.su', '.tk', '.tv', '.uk', '.us', '.ws'
}

URL_START_RE = re.compile(r'^(https?://.+?|www\..+?\..+?)', re.I)
URL_END_RE = re.compile(r'(%s)(\/|:|$)' % '|'.join(TLDS), re.I)
EMAIL_RE = re.compile(r'([\w\-\.\+%]+@(\w[\w\-]+\.)+[\w\-]+)', re.I)
DOI_RE = re.compile(r'^10\.\d{4,}(?:\.\d+)*/\S+$', re.U)
ISSN_RE = re.compile(r'^[A-Za-z0-9]{4}-[A-Za-z0-9]{4}$')
