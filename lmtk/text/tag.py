#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""lmtk.text.tag - POS Taggers."""

import os
import pickle

#from nltk.tag import SequentialBackoffTagger

from lmtk.utils import find_data


# class NameTagger(SequentialBackoffTagger):
#     """Tagger for tagging names as proper nouns.
#
#     Given a list of names and a tag (default NNP), NameTagger will tag the names appropriately. This is useful for
#     lists of proper names such as for places and people. NameTagger is a subclass of the nltk `SequentialBackoffTagger`
#     so it can be used in a backoff chain.
#
#     For a token to match the name, the first letter must be uppercase and the last letter must be lowercase. However
#     the token does not need to match the case of the name in the list exactly.
#
#     """
#
#     def __init__(self, names, tag='NNP', *args, **kwargs):
#         SequentialBackoffTagger.__init__(self, *args, **kwargs)
#         self._names = {n.lower() for n in names if len(n) > 2}
#         self._tag = tag
#
#     def choose_tag(self, tokens, index, history):
#         word = tokens[index]
#         if word[0].isupper() and word[-1].islower() and word.lower() in self._names:
#             return self._tag
#
#     def __repr__(self):
#         return '<NameTagger: size=%d tag=%s>' % (len(self._names), self._tag)
#
#
# def pos_tag(tokens):
#     """POS tag tokens using the default tagger"""
#     if not pos_tag.tagger:
#         pos_tag.tagger = pickle.load(open(find_data(os.path.join('tag', 'tagger.pickle')), 'rb'))
#     return pos_tag.tagger.tag(tokens)
#
# pos_tag.tagger = None


