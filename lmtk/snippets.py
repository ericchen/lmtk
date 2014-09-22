#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""lmtk.snippets - Useful code snippets."""
import glob
import json

import os
import pickle
import random
import requests

from bs4 import BeautifulSoup

from lmtk.bib import BibtexParser
from lmtk.html import clean_html, HTML
from lmtk.pub.rsc import RSCHTML
from lmtk.utils import find_data
from lmtk.text import u


def create_corpus():
    import pymongo
    fout = open(find_data(os.path.join('uvvis', 'abstracts2.txt')), 'w')
    from bs4 import BeautifulSoup
    db = pymongo.Connection().uvVisDb
    for paper in db.papers.find({'html': {'$exists': True}}):
        soup = BeautifulSoup(paper['html'], 'lxml')
        abstract = soup.find('p', {'class': 'p'})
        if abstract:
            abstract = clean_html(abstract)
            fout.write(abstract.encode('utf-8'))
            fout.write('\n')
        # TODO: Captions (figures and tables)
        # for capspan in soup.select('span[id^=tab]'):
        #     number = capspan['id'][3:]
        #     caption = clean_html(capspan)


def run_tokenizer():
    """Write ChemTokenizer tokens to a file."""
    from lmtk.chem import ChemTokenizer, normalize
    ct = ChemTokenizer()
    inpath = find_data(os.path.join('uvvis', 'captions.txt'))
    outpath = find_data(os.path.join('uvvis', 'captions-tokens2.txt'))
    with open(inpath, 'r') as fin, open(outpath, 'w') as fout:
        for line in fin:
            sents = ct.tokenize(normalize(line))
            for sent in sents:
                fout.write(' '.join(sent).encode('utf-8'))
                fout.write('\n')


def train_maxent_pos_tagger():
    """Train a maximum entropy POS tagger using the megam algorithm.

    The result of this is similar to the default nltk POS tagger, but slightly worse. The training method for the
    default nltk POS tagger is not public, but likely a larger training corpus was used (e.g. full Penn Treebank).

    If megam is not available, alternatively nltk has a (much slower) built-in algorithm.

    """
    from nltk.tag.sequential import ClassifierBasedPOSTagger
    from nltk.classify import MaxentClassifier
    from nltk.corpus import treebank
    from nltk.classify import megam
    megam.config_megam('/usr/local/bin/megam')
    train_sents = treebank.tagged_sents()
    #tagger = ClassifierBasedPOSTagger(train=train_sents, classifier_builder=MaxentClassifier.train)
    tagger = ClassifierBasedPOSTagger(train=train_sents, classifier_builder=lambda train_feats: MaxentClassifier.train(train_feats, algorithm='megam', max_iter=10, min_lldelta=0.1))
    with open(find_data(os.path.join('tag', 'maxent.pickle')), 'wb') as f:
        pickle.dump(tagger, f)


def train_tagger():
    """Train POS tagger on the Penn Treebank subset available in NLTK.

    This is the training process used for the default lmtk tagger. Run the tagger using `lmtk.text.pos_tag()`.

    """
    import pickle
    from nltk.corpus import treebank, names
    from nltk.tag import DefaultTagger, AffixTagger, UnigramTagger, BigramTagger, TrigramTagger, RegexpTagger
    from lmtk.text import NameTagger

    # Get tagged penn treebank corpus and rename some of the tags to match our conventions
    train_sents = treebank.tagged_sents()
    for sent in train_sents:
        for i, (token, tag) in enumerate(sent):
            if token == '(':
                sent[i] = (token, '-LRB-')
            elif token == ')':
                sent[i] = (token, '-RRB-')
            elif token == '[':
                sent[i] = (token, '-LSB-')
            elif token == ']':
                sent[i] = (token, '-RSB-')
            elif token == '{':
                sent[i] = (token, '-LCB-')
            elif token == '}':
                sent[i] = (token, '-RCB-')
            elif token == '-' or token == '--':
                sent[i] = (token, 'DASH')
            elif tag == '.':
                sent[i] = (token, 'STOP')
            elif tag == ',':
                sent[i] = (token, 'COMMA')
            elif tag == ':':
                sent[i] = (token, 'COLON')
            elif tag == '#' or tag == '$':
                sent[i] = (token, 'SYM')
            elif tag == '``' or tag == '\'\'':
                sent[i] = (token, 'QUOTE')

    # Get list of names, removing those with other meanings
    blacklist = {
        'April', 'August', 'Ball', 'Best', 'Black', 'Blank', 'Block', 'Bone', 'Born', 'Car', 'Colon', 'Committee',
        'Con', 'Constable', 'Cool', 'Cross', 'Crown', 'Crystal', 'Day', 'Dot', 'Ethyl', 'Ferro', 'Field', 'Fine',
        'Flavin', 'Gene', 'Gold', 'Grand', 'Green', 'Grey', 'Guest', 'Hard', 'Head', 'House', 'Joule', 'June', 'Kelvin',
        'Lake', 'Lion', 'Loss', 'Low', 'Main', 'Major', 'Man', 'March', 'Marks', 'Max', 'May', 'Meta', 'Nation',
        'Nickel', 'North', 'Page', 'Palm', 'Pen', 'Plane', 'Planes', 'Plant', 'Pore', 'Post', 'Prime', 'Ray', 'Real',
        'Red', 'Rest', 'Rich', 'Rod', 'Rose', 'Sample', 'Screen', 'Self', 'Shell', 'Singleton', 'Sky', 'Smart', 'Sol',
        'Solar', 'Southern', 'Spray', 'Star', 'Sun', 'Tab', 'Top', 'Trace', 'Trip', 'Urban', 'Van', 'Very', 'Violet',
        'Wells', 'White', 'Wild', 'Wood', 'Young'
    }
    with open(find_data(os.path.join('words', 'lastnames.txt')), 'r') as nf:
        nameset = (set(names.words()) | set(word.strip().lower() for word in nf)) - blacklist

    # Regex rules for tags
    patterns = [
        (r'^\($', '-LRB-'),  # Left regular bracket
        (r'^\)$', '-RRB-'),  # Right regular bracket
        (r'^\[$', '-LSB-'),  # Left square bracket
        (r'^\]$', '-RSB-'),  # Right square bracket
        (r'^\{$', '-LCB-'),  # Left curly bracket
        (r'^\}$', '-RCB-'),  # Right curly bracket
        (r'^[\?\.!]$', 'STOP'),  # Stops
        (r'^,$', 'COMMA'),  # Comma
        (r'^([:;]|\.\.\.)$', 'COLON'),  # Comma
        (ur'^[=×#\$\+<>]$', 'SYM'),  # Symbols
        (ur'^[\-–—+/\\]$', 'DASH'),  # Dashes, plus, slashes
        (ur'^(``|\'\'|[“”‘’`´])$', 'QUOTE'),  # Quotes
        (r'^[~#]?[\-]?(\d+\.?\d*|\.\d+)$', 'CD'),  # Numbers
        (ur'^[\-±\+]?\d+(\.?\d)*x?\d+([\-±\+/\^]*\d+(\.\d)?)*$', 'CD'),  # Numbers
        (r'^(et\.?|al\.?)$', 'FW'),  # Foreign words
        (r'(.*wise|thereby)$', 'RB'),  # Adverbs
        (r'^(wt\.|[Vv]alve|[Ii]nlet|[Oo]utlet|[Cc]ondenser|[Ss]tirrer|[Ss]yringe|[Oo]ven|[Vv]essel|[Tt]ube|[Ff]lask|'
         r'[Ss]ample|[Nn]ano(sphere|tube|sheet)|[Cc]olloid|[Ss]olvent|[Cc]omposite|[Ll]ipid|([Nn]ano)?[Dd]endrite|'
         r'[Cc]lip|[Dd]erivative|[Ff]luorophore|[Ss]pectroscopy|[Cc]omplex|[Aa]ssay|[Aa]cid|[Ll]igand)$', 'NN'),  # Nouns
        (r'^([Nn]anotubes|[Ss]pectra)$', 'NNS'),  # Plural nouns
        (r'^([Tt]owards|[Oo]utside)$', 'IN'),  # Preposition
        (r'^([Dd]etect)$', 'VB'),  # Verbs
        (r'^([Ss]hortest)$', 'JJS'),  # Superlative adjectives
        (r'^([Bb]eige|[Bb]rown|[Cc]yan|[Gg]reen|[Gg]rey|[Mm]agenta|[Oo]range|[Pp]urple|[Yy]ellow|[Aa]cidic|aq\.|liq\.|'
         r'[Dd]ilute|[Cc]olloidal|([Nn]ano)?[Cc]rystalline|[Pp]ristine|[Bb]ulky|([Nn]ano)?[Hh]ybrid|[Uu]nbound|ambient|'
         r'[Ii]nfrared|[Pp]yramidal|(.*-)?[Pp]lanar|[Pp]yridoxal|[Vv]alent|[Tt]riplet|[Uu]ltraviolet)$', 'JJ'),  # Adjectives
    ]

    # Create tagger backoff chain
    tagger = DefaultTagger('NN')
    tagger = AffixTagger(train_sents, backoff=tagger, min_stem_length=-3)
    tagger = NameTagger(nameset, backoff=tagger)
    tagger = UnigramTagger(train_sents, backoff=tagger)
    tagger = BigramTagger(train_sents, backoff=tagger)
    tagger = TrigramTagger(train_sents, backoff=tagger)
    tagger = RegexpTagger(patterns, backoff=tagger)

    # Pickle tagger
    with open(find_data(os.path.join('tag', 'tagger.pickle')), 'wb') as f:
        pickle.dump(tagger, f, -1)


def run_tagger():
    """Run POS tagger."""
    #from lmtk.text import pos_tag

    with open(find_data(os.path.join('tag', 'chem-fast.pickle')), 'rb') as f:
        tagger = pickle.load(f)

    inpath = find_data(os.path.join('uvvis', 'abstracts-tokens.txt'))
    outpath = find_data(os.path.join('uvvis', 'abstracts-tags-chem-fast2.txt'))
    with open(inpath, 'r') as fin, open(outpath, 'w') as fout:
        for line in fin:
            tokens = u(line).split()
            #tts = pos_tag(tokens)
            tts = tagger.tag(tokens)
            outline = []
            for tt in tts:
                if tt[1] == 'CM':
                    outline.append('/'.join(tt))
                else:
                    outline.append(tt[0])
            fout.write(' '.join(outline).encode('utf-8'))
            fout.write('\n')


def dump_treebank():
    """Write Penn treebank to files.

    Some of the tags are modified to match our conventions.
    """
    from nltk.corpus import treebank
    tb = treebank.sents()
    with open(find_data(os.path.join('uvvis', 'treebank-tokens.txt')), 'w') as f:
        for sent in tb:
            f.write(' '.join(t for t in sent))
            f.write('\n')
    tb = treebank.tagged_sents()
    with open(find_data(os.path.join('uvvis', 'treebank-tags-gold.txt')), 'w') as f:
        for sent in tb:
            for i, (token, tag) in enumerate(sent):
                if token == '(':
                    sent[i] = (token, '-LRB-')
                elif token == ')':
                    sent[i] = (token, '-RRB-')
                elif token == '[':
                    sent[i] = (token, '-LSB-')
                elif token == ']':
                    sent[i] = (token, '-RSB-')
                elif token == '{':
                    sent[i] = (token, '-LCB-')
                elif token == '}':
                    sent[i] = (token, '-RCB-')
                elif token == '-' or token == '--':
                    sent[i] = (token, 'DASH')
                elif tag == '.':
                    sent[i] = (token, 'STOP')
                elif tag == ',':
                    sent[i] = (token, 'COMMA')
                elif tag == ':':
                    sent[i] = (token, 'COLON')
                elif tag == '#' or tag == '$':
                    sent[i] = (token, 'SYM')
                elif tag == '``' or tag == '\'\'':
                    sent[i] = (token, 'QUOTE')
            f.write(' '.join('/'.join(tt) for tt in sent).encode('utf-8'))
            f.write('\n')


def train_maxent_chem_tagger():
    """Train a maximum entropy POS tagger for chemical names using the megam algorithm."""
    from nltk.tag.sequential import ClassifierBasedPOSTagger
    from nltk.classify import MaxentClassifier
    from nltk.classify import megam
    megam.config_megam('/usr/local/bin/megam')

    train_sents = []
    with open(find_data(os.path.join('uvvis', 'abstracts-tags-gold.txt')), 'r') as f:
        for i, line in enumerate(f):
            tts = u(line).split()
            for i, tt in enumerate(tts):
                if tt.endswith('/CM'):
                    tts[i] = (tt[:-3], 'CM')
                else:
                    tts[i] = (tt, '-NONE-')
            train_sents.append(tts)
    print 'Training on %s sentences' % len(train_sents)
    #tagger = ClassifierBasedPOSTagger(train=train_sents, classifier_builder=MaxentClassifier.train)
    tagger = ClassifierBasedPOSTagger(train=train_sents, classifier_builder=lambda train_feats: MaxentClassifier.train(train_feats, algorithm='megam', max_iter=10, min_lldelta=0.1))
    with open(find_data(os.path.join('tag', 'chem-maxent.pickle')), 'wb') as f:
        pickle.dump(tagger, f)


def train_fast_chem_tagger():
    """Train a fast POS tagger for chemical names."""
    import pickle
    from nltk.tag import DefaultTagger, AffixTagger, UnigramTagger, BigramTagger, TrigramTagger

    train_sents = []
    with open(find_data(os.path.join('uvvis', 'abstracts-tags-gold.txt')), 'r') as f:
        for i, line in enumerate(f):
            tts = u(line).split()
            for i, tt in enumerate(tts):
                if tt.endswith('/CM'):
                    tts[i] = (tt[:-3], 'CM')
                else:
                    tts[i] = (tt, '-NONE-')
            train_sents.append(tts)
    print 'Training on %s sentences' % len(train_sents)

    # Create tagger backoff chain
    tagger = DefaultTagger('-NONE-')
    tagger = AffixTagger(train_sents, backoff=tagger, min_stem_length=-3)
    tagger = UnigramTagger(train_sents, backoff=tagger)
    tagger = BigramTagger(train_sents, backoff=tagger)
    tagger = TrigramTagger(train_sents, backoff=tagger)

    # Pickle tagger
    with open(find_data(os.path.join('tag', 'chem-fast.pickle')), 'wb') as f:
        pickle.dump(tagger, f, -1)


def create_gold_all():
    """"Use lmtk tagger to tag tokens that are not CM in gold corpus."""
    # Open gold corpus, gold-all
    # for each line
        # split tokens, remove /CM from end
        # tag tokens
        # overwrite tokens with /CM
        # write to gold-all

def calculate_accuracy():
    """Compare the results of a POS tagger against a gold standard."""
    from nltk.metrics import accuracy
    print 'reading gold'
    with open(find_data(os.path.join('uvvis', 'abstracts-tags-gold.txt')), 'r') as f:
        gold = []
        for line in f:
            tts = u(line).split()
            for tt in tts:
                if tt.endswith('/CM'):
                    gold.append((tt[:-3], 'CM'))
                else:
                    gold.append((tt, '-NONE-'))
            #tts = [tuple(tt.rsplit('/', 1)) for tt in tts]
            #gold.append(tts)
    #print 'summing gold'
    #gold = sum(gold, [])

    print 'reading test'
    with open(find_data(os.path.join('uvvis', 'abstracts-tags-chem-maxent.txt')), 'r') as f:
        test = []
        for line in f:
            tts = u(line).split()
            for tt in tts:
                if tt.endswith('/CM'):
                    test.append((tt[:-3], 'CM'))
                else:
                    test.append((tt, '-NONE-'))
            #tts = [tuple(tt.rsplit('/', 1)) for tt in tts]
            #test.append(tts)
    #print 'summing test'
    #test = sum(test, [])
    print 'calculating accuracy'
    print accuracy(gold, test)

    # Treebank Gold
    # megam2: 0.955103500338
    # opennlp: 0.921331797052
    # postag: 0.995699074258
    # japerk: 0.993275457905
    # fasttagger: 0.99417934761
    # fasttagger2: 0.992361635345

    # Abstracts vs. opennlp
    # megam2: 0.857079035748
    # postag: 0.875302270372
    # japerk: 0.783409479926
    # fasttagger: 0.814692353047
    # fasttagger2: 0.814510536282

    # chem tagger
    # maxent: 0.977172921821
    # fast: 0.995645315561


def split_gold_tokens():
    pos = set()
    neg = set()
    with open(find_data(os.path.join('uvvis', 'abstracts-tags-gold.txt')), 'r') as f:
        for line in f:
            tts = u(line).split()
            for tt in tts:
                if tt.endswith('/CM'):
                    pos.add(tt[:-3])
                else:
                    neg.add(tt)
    cms = set()
    noncms = set()
    mixedcms = set()
    for token in pos:
        if not token in neg:
            cms.add(token)
        elif not token in mixedcms:
            mixedcms.add(token)
    for token in neg:
        if not token in pos:
            noncms.add(token)
        elif not token in mixedcms:
            mixedcms.add(token)
    with open(find_data(os.path.join('uvvis', 'cms.txt')), 'w') as f:
        for token in cms:
            f.write(token.encode('utf-8'))
            f.write('\n')
    with open(find_data(os.path.join('uvvis', 'noncms.txt')), 'w') as f:
        for token in noncms:
            f.write(token.encode('utf-8'))
            f.write('\n')
    with open(find_data(os.path.join('uvvis', 'mixedcms.txt')), 'w') as f:
        for token in mixedcms:
            f.write(token.encode('utf-8'))
            f.write('\n')


def build_rsc_full_corpus():
    """Select 200 articles at random from the RSC BibTeX file and download the HTML."""
    with open(find_data(os.path.join('ner', 'rsc_2013-02.bib')), 'r') as f:
        bib = BibTeXParser(f.read())
        bib.parse()
    # journals = {}
    # for article in bib.records_list:
    #     journals[article['journal']] = journals.get(article['journal'], 0) + 1
    # print journals
    random.seed(201309051447)
    rndi = set()
    while len(rndi) < 200:
        rand_int = random.randint(1, len(bib.records_list))
        if rand_int not in rndi:
            rndi.add(rand_int)
    corpus = []
    for i, article in enumerate(bib.records_list):
        if i in rndi:
            corpus.append(article)
    with open(find_data(os.path.join('ner', 'corpus.json')), 'w') as f:
        json.dump(corpus, f)
    s = requests.Session()
    for article in corpus:
        pid = article['doi'].split('/', 1)[1].lower()
        html_url = 'http://pubs.rsc.org/en/content/articlehtml/x/x/%s' % pid
        with open(find_data(os.path.join('ner', 'full', '%s.html' % pid)), 'w') as f:
            f.write(s.get(html_url).text.encode('utf-8'))


def build_rsc_abstract_corpus():
    """Parse RSC BibTeX file and download the HTML for every article."""
    with open(find_data(os.path.join('ner', 'rsc_2013-02.bib')), 'r') as f:
        bib = BibTeXParser(f.read())
        bib.parse()
    s = requests.Session()
    for article in bib.records_list:
        print article
        pid = article['doi'].split('/', 1)[1].lower()
        html_url = 'http://pubs.rsc.org/en/content/articlehtml/x/x/%s' % pid
        with open(find_data(os.path.join('ner', 'abs', '%s.html' % pid)), 'w') as f:
            f.write(s.get(html_url).text.encode('utf-8'))


def build_rsc_open_corpus():
    """Download open access papers from RSC."""
    import pymongo
    db = pymongo.Connection().ner
    #db.papers.create_index('doi', unique=True, drop_dups=True)
    sercodes = ['AN', 'AY', 'CY', 'CC', 'SC', 'CE', 'DT', 'EE', 'GC', 'TA', 'TB', 'TC', 'MD', 'NR', 'NJ', 'OB', 'PP', 'CP', 'PY', 'RA']
    decades = ['2011-2013']  #  '2001-2010'
    session = requests.Session()
    for decade in decades:
        for sercode in sercodes:
            data = {
                'decade': '%s#Archive##%s##dcdname' % (decade, sercode),
                'sercode': sercode
            }
            request = session.get('http://pubs.rsc.org/en/journals/getyears', params=data)
            years = [t['Value'] for t in request.json() if 'Value' in t and not t['Value'] == '0']
            for year in years:
                data = {
                    'year': year,
                    'sercode': sercode
                }
                request = session.get('http://pubs.rsc.org/en/journals/getissues', params=data)
                issues = [t['Value'] for t in request.json() if 'Value' in t and not t['Value'] == '0']
                for issue in issues:
                    name, issueid = issue.split('#')[1:3]
                    print 'Issue: %s/%s' % (name, issueid)
                    pagenumber = 1
                    totalpages = 1
                    while pagenumber <= totalpages:
                        print 'Page %s' % pagenumber
                        data = {
                            'name': name,
                            'issueid': issueid,
                            'jname': '',
                            'iscontentavailable': 'True',
                            'pagenumber': str(pagenumber)
                        }
                        request = session.post('http://pubs.rsc.org/en/journals/issues', data)
                        soup = BeautifulSoup(request.text, 'lxml')
                        totalpages = int(soup.find('span', id='totalPages').text.strip())
                        pagenumber += 1
                        for box in soup('div', class_='grey_box_middle_s4_jrnls'):
                            oabox = box.find('div', class_='search_jrnl_article_new')
                            paper = {
                                'title': box.find('h2', class_='title_text_s4_jrnls').text.strip(),
                                'doi': '10.1039/%s' % oabox['id'].lower(),
                                'oa': oabox.text.strip() == 'Open Access',
                                'cit': ' '.join(box.find('div', class_='grey_left_box_text_s4_new').text.split()),
                                'j': sercode
                            }
                            print '%s: %s - %s' % (paper['doi'], paper['oa'], paper['title'])
                            db.papers.insert(paper)


def download_open_corpus():
    import pymongo
    session = requests.Session()
    db = pymongo.Connection().ner
    for article in db.papers.find({'oa': True}):
        pid = article['doi'].split('/', 1)[1].lower()
        print pid
        fpath = find_data(os.path.join('ner', 'open', '%s.html' % pid))
        if not os.path.exists(fpath):
            html_url = 'http://pubs.rsc.org/en/content/articlehtml/x/x/%s' % pid
            with open(find_data(fpath), 'w') as f:
                f.write(session.get(html_url).text.encode('utf-8'))


def get_open_citations():
    import pymongo
    session = requests.Session()
    db = pymongo.Connection().ner
    data = {'ResultAbstractFormat': 'BibTex'}
    for article in db.papers.find({'oa': True}):
        pid = article['doi'].split('/', 1)[1]
        bibtex = session.post('http://pubs.rsc.org/en/content/getformatedresult/%s?downloadtype=article' % pid, data)
        bp = BibTeXParser(bibtex.text)
        bp.parse()
        article = dict(bp.records_list[0].items() + article.items())
        db.papers.save(article)


def prepare_rsc_html():
    """For each HTML file, extract headings, abstract and paragraphs and convert to plain text."""
    # for fn in glob.glob('data/ner/full/*.html'):
    #     with open(fn, 'r') as fin, open(fn[:-4]+'txt', 'w') as fout:
    #         print fn
    #         h = RSCHTML(fin)
    #         body = []
    #         on = True
    #         ignore = {'Experimental', 'Acknowledgements', 'References', 'Notes and references'}
    #         for s in h.sections:
    #             print s
    #             if s['type'] == 'heading' and s['text'] in ignore:
    #                 on = False
    #             elif s['type'] == 'heading' and s['text'] not in ignore:
    #                 on = True
    #             elif on:
    #                 body.append(s['text'])
    #         output = h.title + u'\n\n' + h.abstract + u'\n\n' + u'\n\n'.join(body)
    #         fout.write(output.encode('utf-8'))
    for fn in glob.glob('data/ner/abs/*.html'):
        if not os.path.exists(fn[:-4]+'txt'):
            with open(fn, 'r') as fin, open(fn[:-4]+'txt', 'w') as fout:
                print fn
                h = RSCHTML(fin)
                fout.write(h.abstract.encode('utf-8'))


def build_corpus_file():
    # Build file for 200 full articles
    with open('data/ner/full.txt', 'w') as fout:
        for fn in glob.glob('data/ner/full/*.txt'):
            with open(fn, 'r') as fin:
                fout.write(fin.read())
                fout.write('\n\n')
        # for fn in glob.glob('data/ner/abs/*.txt'):
        #     with open(fn, 'r') as fin:
        #         fout.write(fin.read())
        #         fout.write('\n\n')
    # Build file for 1600 abstracts
    with open('data/ner/abs.txt', 'w') as fout:
        for fn in glob.glob('data/ner/abs/*.txt'):
            with open(fn, 'r') as fin:
                fout.write(fin.read())
                fout.write('\n\n')
    # check lengths
    # Consider choosing a different subset of 200ish abstracts


if __name__ == '__main__':
    #create_corpus()
    #train_tagger()
    #train_maxent_pos_tagger()
    #train_maxent_chem_tagger()
    #train_fast_chem_tagger()
    #run_tokenizer()
    #run_tagger()
    #dump_treebank()
    #calculate_accuracy()
    #split_gold_tokens()
    #build_rsc_abstract_corpus()
    #build_rsc_full_corpus()
    #build_rsc_open_corpus()
    #prepare_rsc_html()
    #download_open_corpus()
    #get_open_citations()
    build_corpus_file()
