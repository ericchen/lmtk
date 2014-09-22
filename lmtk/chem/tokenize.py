# -*- coding: utf-8 -*-
"""
lmtk.chem.tokenize
~~~~~~~~~~~~~~~~~~

Chemistry-aware text tokenization.

:copyright: Copyright 2014 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""
import os
import re

from lmtk import text, html, utils
from .text import ELEMENTS, ELEMENT_SYMBOLS

class ChemTokenizer():
    """Chemistry-aware text tokenizer.

    ChemTokenizer splits a string on whitespace and then further splits tokens according to some rules.

    Parts of this class are based on the OSCAR4 Tokenizer, developed by the Murray-Rust research group at the Unilever
    Centre for Molecular Science Informatics, University of Cambridge and released under the Artistic License 2.0. See
    https://bitbucket.org/wwmm/oscar4 for more information.

    """

    def __init__(self):
        # Set up parameters and compile regular expressions
        self.oxstate = re.compile(r'(%s)\((o|i{1,4}|i{0,3}[xv]|[xv]i{0,4})\)$' % '|'.join(ELEMENTS | ELEMENT_SYMBOLS), re.I)
        self.bracketrange = re.compile(r'^\((\w+)\)-\((\w+)\)$')
        self.chemnamecolon = re.compile(ur"(η\d:η\d|"
                                        ur"\d+[a-g]?[′']*(alpha|beta)?,\d[a-g]?[′']*(alpha|beta)?(-([a-zA-Z][′']*)+)?:\d|"
                                        ur"\d[a-g]?[′']*(alpha|beta)?(-([a-zA-Z][′']*)+)?:\d[a-g]?[′']*(alpha|beta)?,\d)")
        self.chemnameequals = re.compile(r'[^=]*[CNHOP]+[0-9]*[\(\)]?=\(?[CNOP].*')
        self.quantity = re.compile(ur'^([∼~≈]?-?(?![12]s)\d+(?:\.\d+)?|\d*\.\d+)([cdGkmMnpTuµ]?'
                                   ur'(?:[gJlLMmNsVW]|[Gg]ramm?e?s?|Hz|[Mm][Oo][Ll](?:e|ar)?s?|h?Pa|ppm)(?:-?\d)?)$')
        self.percentage = re.compile(ur'^(-?\d+(?:\.\d+)?|\d*\.\d+)(%)$')
        self.ph = re.compile(ur'^(ph)(-?\d+(?:\.\d+)?|\d*\.\d+)$', re.I)
        self.temperature = re.compile(ur'^([∼~≈]?-?\d+(?:\.\d+)?|\d*\.\d+)?([°º])([cf])?$', re.I)
        self.initial = re.compile(ur'^(-?[A-Zv]\.)+$')
        self.linesymbol = re.compile(ur'^([\-–—−*+\.=_~×…·■●▲○◆▼△◇▽⬚]+)$')
        self.chemafterinitial = re.compile(r'^[a-z]+?(o[blnrs]a|i[cdlnv]a|o[lr]i|a[nt]a|[ae]ns|u[ms]|i[ais]|ae|e(ll)?a|et?i|u[cls]?a)$')
        propernoun = ur"(O'|Ma?c)?[A-Z][a-z]{3,}(s'|'s)?"
        self.propernounhyphen = re.compile(ur"(%s(%s))+%s" % (propernoun, '|'.join(text.HYPHENS), propernoun), re.U)
        self.concfollowing = {'=', '/', u'≈', u'≥', u'≤', u'>', u'<'}
        with open(utils.find_data(os.path.join('words', 'lastnames.txt')), 'r') as f:
            self.lastnames = {name.strip() for name in f}
        with open(utils.find_data(os.path.join('words', 'hyphen_splits.txt')), 'r') as f:
            self.hyphensplits = {word.lower().strip() for word in f}
        self.abbreviations = {
            '+vs.', '.e.g.', '1vs.', '24h.', '2vs.', '3vs.', '4vs.', '5vs.', '6vs.', '7vs.', '8vs.', '9vs.', 'abs.',
            'acad.', 'acc.', 'adm.', 'adv.', 'agric.', 'al.', 'ala.', 'allg.', 'am.', 'ampl.', 'anal.', 'angew.',
            'anh.', 'anorg.', 'appl.', 'approx.', 'apr.', 'aq.', 'ariz.', 'atmos.', 'aug.', 'aut.', 'av.', 'ave.',
            'avg.', 'bioanal.', 'biochem.', 'biochim.', 'biol.', 'biomater.', 'biomed.', 'biomol.', 'biophys.',
            'biosci.', 'biotech.', 'biotechnol.', 'bornm.', 'brev.', 'bros.', 'ca.', 'calif.', 'canc.', 'catal.', 'cf.',
            'cf.fig.', 'chem.', 'cheminf.', 'chim', 'chg.', 'chromatogr.', 'cli.', 'clin.', 'col.', 'colo.', 'comb.',
            'commun.', 'compd.', 'comput.', 'conc.', 'condens.', 'conn.', 'const.', 'corp.', 'cosmochim.', 'cryst.',
            'crystallogr.', 'ct.', 'curr.', 'dec.', 'dil.', 'dr.', 'ed.', 'elec.', 'electroanal.', 'engl.', 'environ.',
            'eq.', 'eqn.', 'eqns.', 'eqs.', 'equiv.', 'eqv.', 'et.', 'etc.', 'etm.', 'eur.', 'evs.', 'excit.', 'fal.',
            'feb.', 'fig.', 'figs.', 'fla.', 'fri.', 'fromref.', 'ft.', 'funct.', 'gen.', 'geochim.', 'gvs.', 'hlv.',
            'hoc.', 'ifvs.', 'inc.', 'inf.', 'inorg.', 'instrum.', 'int.', 'ipp.', 'ipvs.', 'ivs.', 'jan.', 'jpn.',
            'jr.', 'jvs.', 'kcatvs.', 'kemistil.', 'ketvs.', 'kinet.', 'kobsdvs.', 'kobsvs.', 'ksvs.', 'kvs.',
            'l-arg-conj.', 'lett.', 'liq.', 'lit.', 'ltd.', 'magn.', 'maj.', 'mater.', 'max.', 'med.', 'messrs.',
            'mfa.', 'mich.', 'minn.', 'mnvs.', 'mob.', 'mp.', 'mpn.', 'mpph.', 'mr.', 'mrs.', 'ms.', 'mshs.', 'mut.',
            'mvs.', 'nanotech.', 'nat.', 'natl.', 'nmvs.', 'nov.', 'nucl.', 'occ.', 'oct.', 'okla.', 'oncol.', 'opin.',
            'org.', 'pa.', 'ph.d.', 'pharm.', 'phd.', 'phm.', 'photobio.', 'photobiol.', 'photochem.', 'phys.',
            'physiol.', 'polym.', 'proc.', 'prod.', 'prof.', 'prog.', 'psvs.', 'radiat.', 'ref.', 'refs.', 'relat.',
            'rep.', 'reps.', 'res.', 'resp.', 'rev.', 's-1vs.', 'sat.', 'sci.', 'sel.', 'sen.', 'sep.', 'sept.', 'soc.',
            'sol.', 'spectrom.', 'spectrosc.', 'sr.', 'st.', 'struct.', 'stud.', 'sulf.', 'surf.', 'sym.', 'synth.',
            'syst.', 'technol.', 'temp.', 'tenn.', 'theor.', 'thurs.', 'tll.', 'toxicol.', 'trans.', 'tues.', 'tvs.',
            'univ.', 'v1.', 'v2.', 'vel.', 'viz.', 'vol.', 'vs.', 'vs.i.', 'vs.n.', 'vvs.', 'wed.', 'wt.', 'xmp.',
            'xvs.', 'yr.', 'zvs.', u'±s.d.', u'Λvs.', u'Δεvs.', u'ηvs.', u'φfvs.', u'χmtvs.', u'χmvs.', u'νs.',
            u'λexc.', u'λmax.', u'σvs.'
        }
        self.collocs = {
            ('a', 'commune'), ('a', 'niger'), ('c', 'limon'), ('d', 'bardawil'), ('e', 'antonini'), ('e', 'coli'),
            ('e', 'colia'), ('j', 'adv'), ('j', 'agric'), ('j', 'am'), ('j', 'anal'), ('j', 'appl'), ('j', 'biol'),
            ('j', 'biomed'), ('j', 'catal'), ('j', 'chem'), ('j', 'cheminf'), ('j', 'chromatogr'), ('j', 'comb'),
            ('j', 'electroanal'), ('j', 'inorg'), ('j', 'liquid'), ('j', 'mater'), ('j', 'membrane'), ('j', 'mol'),
            ('j', 'nucl'), ('j', 'org'), ('j', 'photochem'), ('j', 'phys'), ('j', 'radiat'), ('j', 'steroid'),
            ('j', 'struct'), ('l', 'extract'), ('l', 'mesenteroides'), ('m', '1.5'), ('mol', 'biol'), ('mol', 'struct'),
            ('n', 'crassa'), ('p', 'bursaria'), ('p', 'simplex'), ('p', 'ulysses'), ('p', u'νersutus'),
            ('s', 'cattleya'), ('s', 'coelicolor'), ('t', 'maritima')
        }
        self.nosplitprefix = {
            '.*ano', '.*ato', '.*azo', '.*boc', '.*bromo', '.*cbz', '.*chloro', '.*eno', '.*fluoro', '.*fmoc', '.*ido',
            '.*ino', '.*io', '.*iodo', '.*mercapto', '.*nitro', '.*ono', '.*oso', '.*oxalo', '.*oxo', '.*oxy',
            '.*phospho', '.*telluro', '.*tms', '.*yl', '.*ylen', '.*ylene', '.*yliden', '.*ylidene', '.*ylidyn',
            '.*ylidyne', 'aci', 'adeno', 'aldehydo', 'allo', 'alpha', 'altro', 'ambi', 'ante', 'anti', 'aorto',
            'arachno', 'arch', 'as', 'be', 'beta', 'bi', 'bio', 'bis', 'catena', 'centi', 'chi', 'chiro', 'circum',
            'cis', 'closo', 'co', 'colo', 'conjuncto', 'conta', 'contra', 'cortico', 'cosa', 'counter', 'cran',
            'crypto', 'cyclo', 'de', 'deca', 'deci', 'delta', 'demi', 'di', 'dis', 'dl', 'eco', 'electro', 'endo',
            'ennea', 'ent', 'epi', 'epsilon', 'erythro', 'eta', 'ex', 'exo', 'extra', 'ferro', 'galacto', 'gamma',
            'gastro', 'giga', 'gluco', 'glycero', 'graft', 'gulo', 'hemi', 'hepta', 'hexa', 'homo', 'hydro', 'hypho',
            'hypo', 'ideo', 'idio', 'in', 'infra', 'inter', 'intra', 'iota', 'iso', 'judeo', 'kappa', 'keto', 'kis',
            'lambda', 'lyxo', 'macro', 'manno', 'medi', 'meso', 'meta', 'micro', 'mid', 'milli', 'mini', 'mono', 'mu',
            'muco', 'multi', 'musculo', 'myo', 'nano', 'neo', 'neuro', 'nido', 'nitro', 'non', 'nona', 'nor', 'novem',
            'novi', 'nu', 'octa', 'octi', 'octo', 'omega', 'omicron', 'ortho', 'over', 'paleo', 'pan', 'para', 'pelvi',
            'penta', 'peri', 'pheno', 'phi', 'pi', 'pica', 'pneumo', 'poly', 'post', 'preter', 'pro', 'psi', 'quadri',
            'quater', 'quinque', 're', 'recto', 'rho', 'ribo', 'salpingo', 'scyllo', 'sec', 'semi', 'sept', 'septi',
            'sero', 'sesqui', 'sexi', 'sigma', 'sn', 'soci', 'sub', 'super', 'supra', 'sur', 'sym', 'syn', 'talo',
            'tau', 'tele', 'ter', 'tera', 'tert', 'tetra', 'theta', 'threo', 'trans', 'tri', 'triangulo', 'tris',
            'uber', 'ultra', 'un', 'uni', 'unsym', 'upsilon', 'veno', 'ventriculo', 'xi', 'xylo', 'zeta',
            u'\d[`′\']?(,\d\[`′\']?(,\d\[`′\']?)?)?'
        }
        self.split = {
            'absorption', 'acid', 'active', 'addition', 'adsorption', 'air', 'alkaline', 'all', 'analogous', 'angle',
            'area', 'armed', 'atom', 'atomic', 'average', 'band', 'bandwidth', 'based', 'binding', 'bioactivity',
            'biomonitor', 'black', 'blood', 'blue', 'bond', 'bonds', 'bottom', 'bound', 'bridged', 'broad', 'built',
            'caged', 'capped', 'carrier', 'cast', 'catalysed', 'catalyzed', 'cation', 'chains', 'charge', 'chemo',
            'chrome', 'circuit', 'coated', 'color', 'colour', 'complex', 'complexes', 'compounds', 'concentration',
            'configuration', 'conjugated', 'containing', 'coordinate', 'core', 'cored', 'cotransport', 'cross',
            'current', 'dark', 'dash', 'dashed', 'deficiency', 'deficient', 'density', 'dependence', 'dependent',
            'deplete', 'derivatised', 'derivatives', 'derivatized', 'derived', 'desorption', 'diabetes', 'diabetic',
            'dimensional', 'dimer', 'distribution', 'domain', 'donor', 'dot', 'double', 'driven', 'dual', 'dye',
            'efficiency', 'eight', 'electrolyte', 'electron', 'emersion', 'energy', 'enzyme', 'exchange', 'excimer',
            'expanded', 'extraction', 'field', 'film', 'first', 'five', 'form', 'formation', 'four', 'free',
            'frequency', 'front', 'function', 'functionalised', 'functionalized', 'fused', 'gas', 'generation',
            'geometry', 'grafted', 'grain', 'green', 'group', 'groups', 'guest', 'half', 'high', 'human', 'hybrid',
            'hyperaccumulator', 'immersion', 'independent', 'induced', 'inducible', 'insensitive', 'intermediate',
            'ions', 'isomer', 'isomers', 'kinase', 'known', 'lamp', 'laser', 'last', 'layer', 'left', 'ligand', 'light',
            'like', 'lined', 'linked', 'lipoprotein', 'liquid', 'long', 'low', 'lower', 'luminance', 'luminescence',
            'majority', 'material', 'mediated', 'medium', 'metal', 'migrated', 'mirror', 'mixed', 'mode', 'model',
            'modified', 'moiety', 'monomer', 'nanoparticle', 'nanotube', 'near', 'nearest', 'neighbor', 'neighbour',
            'nine', 'nonfermentative', 'note', 'octahedra', 'oil', 'only', 'open', 'order', 'organic', 'oxidase',
            'peak', 'peptide', 'phase', 'photocurrent', 'photon', 'photovoltage', 'pillared', 'plane', 'plasma',
            'point', 'polymer', 'poor', 'position', 'potential', 'protected', 'protein', 'pseudo', 'quasi', 'rate',
            'ratio', 'reaction', 'reactive', 'rearranged', 'red', 'reduction', 'release', 'replete', 'resistant',
            'responsive', 'rich', 'right', 'saturated', 'scale', 'scan', 'second', 'secretion', 'selective',
            'selectivity', 'self', 'sensitive', 'seven', 'shape', 'shell', 'short', 'side', 'signal', 'single',
            'six', 'solid', 'soluble', 'solution', 'solvent', 'space', 'specific', 'spectrum', 'split', 'stage',
            'state', 'step', 'strategy', 'substituent', 'substituted', 'substrate', 'surface', 'temperature',
            'template', 'terminal', 'terminus', 'tethered', 'the', 'thermal', 'thin', 'three', 'through', 'time',
            'transfer', 'transition', 'treated', 'treatment', 'triplet', 'two', 'type', 'units', 'upper', 'view',
            'visible', 'voltage', 'water', 'wave', 'white', 'wide', 'width', 'yellow', 'zero'
            # Remove these?
            # addition armed bridged caged capped catalysed catalyzed cored derivatised derivatized derived expanded
            # extraction function functionalised functionalized grafted lined linked mediated migrated pillared
            # protected reaction rearranged tethered transition
        }
        self.nosplitprefixre = re.compile(r'(\b|[0-9])(%s)(-n)?$' % '|'.join(self.nosplitprefix), re.I)
        self.splitprefixre = re.compile(ur'^(%s)$' % '|'.join(self.split), re.I)
        self.splitsuffixre = re.compile(ur'^(un|de|re|pre)?(%s)s?$' % '|'.join(self.split), re.I)

    def _hyphensplit(self, token):
        """Split token on hyphen according to rules."""
        # Iterate characters from end of string, ensuring at least 1 char before and 2 char after hyphen
        for i, c in enumerate(reversed(token[1:-2])):
            if c in text.HYPHENS:
                before = token[:-3-i]
                after = token[-2-i:]
                # Don't split on hyphens enclosed within brackets
                if text.bracket_level(token) == 0 and not text.bracket_level(after) == 0:
                    continue
                # Split on double-dashes
                if before[-1] in text.HYPHENS:
                    return [before[:-1], before[-1] + c, after]
                # Split on "-to-" "-in-" "-by-" "-of-"
                if len(before) > 2 and before[-3] in text.HYPHENS and before[-2:] in {'to', 'in', 'by', 'of'}:
                    return [before[:-3], before[-3], before[-2:], c, after]
                # Split on "-and-", "-per-"
                if len(before) > 3 and before[-4] in text.HYPHENS and before[-3:] in {'and', 'per'}:
                    return [before[:-4], before[-4], 'and', c, after]
                # Don't split if before matches self.nosplitprefixre or if token is in self.hyphensplits
                if self.nosplitprefixre.search(before) or token in self.hyphensplits or (after[0] == 'd' and
                                                                                         after[1].isdigit()):
                    continue
                # Split if after matches self.splitsuffixre or split token is in self.hyphensplits
                if (self.splitsuffixre.match(after) or self.splitprefixre.match(before) or
                        '%s %s' % (before, after) in self.hyphensplits):
                    return [before, c, after]
                # Split if token is hyphenated proper noun or
                if self.propernounhyphen.match(token) or (after.isalpha() and
                                                          (after.endswith('ing') or after.endswith('ed'))):
                    return [before, c, after]

    def _subtokenize(self, token, nexttoken):
        """Split token into subtokens according to rules, using the token and next token if it exists."""
        if len(token) <= 1 or token.lower() in self.abbreviations or self.linesymbol.match(token):
            return
        first = token[0]
        last = token[-1]

        # Split (\w+)-(\w+) to ( \w+ ) - ( \w+ )
        modtoken = self.bracketrange.sub(r'( \1 ) - ( \2 )', token)
        if not modtoken == token:
            return modtoken.split()

        # Split off open or close bracket off start or end under certain conditions
        for brp in [('(', ')'), ('[', ']'), ('{', '}')]:
            if first == brp[0]:
                bc = 1
                ci = 0
                for i, c in enumerate(token[1:]):
                    bc = bc+1 if c == brp[0] else bc
                    bc = bc-1 if c == brp[1] else bc
                    if bc == 0:
                        ci = i + 1
                        break
                if ci == 0:
                    return [first, token[1:]]
                elif ci == len(token) - 1 and (not last == ']' or (len(token) < 4 or
                                                                   (nexttoken and nexttoken in self.concfollowing) or
                                                                   token[1:-1].isupper() or token[1:-1].islower())):
                    return [first, token[1:]]
            if last == brp[1] and not self.oxstate.search(token):
                bc = 1
                ci = 0
                for i, c in enumerate(reversed(token[:-1])):
                    bc = bc+1 if c == brp[1] else bc
                    bc = bc-1 if c == brp[0] else bc
                    if bc == 0:
                        ci = i + 1
                        break
                if ci == 0:
                    return [token[:-1], last]
                elif ci == len(token) - 1 and (not last == ']' or (len(token) < 4 or
                                                                   (nexttoken and nexttoken in self.concfollowing) or
                                                                   token[1:-1].isupper() or token[1:-1].islower())):
                    return [token[:-1], last]

        # Split specific characters off start and end
        if first in text.QUOTES | {u'≡', u'≠', u'≣', u'≢', u'≥', u'≤', u'≧', u'≦', u'≩', u'≨', u'≫', u'≪', u'=', u'>'}:
            return [first, token[1:]]
        if last in text.QUOTES | {',', ';', ':', '!', '?', '=', u'™', u'÷', u'®', u'×', u'…'}:
            return [token[:-1], last]
        if last == '-' and nexttoken in {'and', 'or', '/', ','} and token[:-1].isalpha() and (
                token[:-1].islower() or (len(token) > 3 and token[0].isupper() and token[1:-1].islower())):
            return [token[:-1], last]

        # Split off multiple character endings
        for ending in ['(TM)', '(R)', '((TM))', '((R))', '...']:
            if token.endswith(ending) and len(ending) < len(token):
                return [token.rsplit(ending, 1)[0], ending]

        # Split off state endings, unless preceded by a digit
        for ending in ['(aq)', '(aq.)', '(s)', '(l)', '(g)']:
            if token.endswith(ending) and len(token) > len(ending):
                pre = token.rsplit(ending, 1)[0]
                if not pre.isdigit():
                    return [pre, ending]

        # Split off line symbol endings
        for ending in [u'(■)', u'(●)', u'(▲)', u'(○)', u'(◆)', u'(▼)', u'(△)', u'(◇)', u'(▽)', u'(⬚)', u'(×)', u'(□)', u'(•)']:
            if token.endswith(ending) and len(ending) < len(token):
                return [token.rsplit(ending, 1)[0], ending]

        # Split full stop off end under certain conditions
        if last == '.':
            if not nexttoken:
                return [token[:-1], last]
            before = token.rstrip('\'"-=<>/,.:;!?')
            after = text.unapostrophe(nexttoken.rstrip('\'"-=<>/,.:;!?)]}'))
            if not (re.match(r'[a-z]\.[a-z]', before, re.I) or
                    (before.lower(), after.lower()) in self.collocs or
                    (token.lower() in {'no.', 'p.', 'pp.'} and after.isdigit()) or
                    (re.match(r'^[A-Z]$', before) and self.chemafterinitial.match(after)) or
                    (self.initial.match(token) and (self.initial.match(nexttoken) or
                                                    after.lower() in text.NAME_SMALL or
                                                    after in self.lastnames))):
                return [token[:-1], last]

        # Quantities
        m = self.quantity.match(token)
        if m:
            return m.groups()
        m = self.percentage.match(token)
        if m:
            return m.groups()
        m = self.ph.match(token)
        if m:
            return m.groups()
        m = self.temperature.match(token)
        if m:
            return [g for g in m.groups() if g]

        # Characters to split on, with a set of exceptions for each character
        for i, c in enumerate(token):
            if c in ['<', '>', '/', u'×', u'÷', u'⋯']:
                if c == '<':
                    # Don't plit on '<' if part of HTML tag
                    if re.match(r'</?(%s)>' % '|'.join(html.INLINE_ELEMENTS), token[i:]):
                        continue
                elif c == '>':
                    # Don't split on '>' if an arrow like '->' or part of HTML tag
                    if (re.search(r'</?(%s)>$' % '|'.join(html.INLINE_ELEMENTS), token[:i+1]) or
                            (i > 2 and token[i-1] == '-' and not token[i-2] == '>')):
                        continue
                elif c == '/':
                    # Don't split on / if part of HTML tag or URL
                    if re.match(r'</(%s)>' % '|'.join(html.INLINE_ELEMENTS), token[i-1:]) or token.startswith('http'):
                        continue
                return [token[:i], token[i:i+1], token[i+1:]]

        # Split on '+' under certain conditions
        for i, c in enumerate(token):
            if c == '+':
                if i < len(token) - 2 and token[i+1] in text.HYPHENS:
                    # But don't split if light rotation: "(+-)-"
                    if not (i > 0 and token[i-1] == '(' and token[i+2] == ')'):
                        return [token[:i+1], token[i+1:i+2], token[i+2:]]
                # Don't split if last character is hyphen or unbalanced brackets in token
                if 0 < i < len(token) - 1 and (token[-1] in text.HYPHENS or
                                               not text.bracket_level(token) == text.bracket_level(token[i+1:]) == 0):
                    continue
                # Don't split + off the end
                if i == len(token) - 1:
                    continue
                return [token[:i], token[i:i+1], token[i+1:]]

        # Split on ':' unless in a chemical name like 2,2':6',2''-Terphenyl-1,1',1''-triol or in URL
        if ':' in token and not self.chemnamecolon.search(token) and not token.startswith('http'):
            return list(token.partition(':'))

        # Split on '=' unless in a chemical name like CH2=CH2
        if '=' in token and not self.chemnameequals.search(token):
            return list(token.partition('='))

        # Split on '-' under certain conditions
        hsplit = self._hyphensplit(token)
        if hsplit:
            return hsplit

    def tokenize(self, s):
        """Tokenize a string."""
        # Split on whitespace, but preserve certain HTML tags as a single token (e.g. '<a>ref. 1</a>')
        tokens = s.split()
        for tag in html.INLINE_ELEMENTS:
            for i in range(len(tokens)-1, 0, -1):
                if '</%s>' % tag in tokens[i]:
                    for j in range(i, 0, -1):
                        if '<%s>' % tag in tokens[j]:
                            tokens[j:i+1] = [' '.join(tokens[j:i+1])]
                            break
        # Recursively split tokens
        i = 0
        while i < len(tokens):
            subtokens = self._subtokenize(tokens[i], tokens[i+1] if i+1 < len(tokens) else None)
            if not subtokens:
                i += 1
            else:
                tokens[i:i+1] = subtokens
        tokens = [t for t in tokens if len(t) > 0]
        # Group tokens into sentences
        stops = []
        for i, x in enumerate(tokens):
            if x in {'.', '?', '!'}:
                if i < len(tokens) - 1 and tokens[i+1] in {'"', '\'', ')', ']', '}'}:
                    stops.append(i + 2)
                else:
                    stops.append(i + 1)
        sentences = [tokens[i:j] for i, j in zip([0] + stops, stops + [len(tokens)]) if i < j]
        return sentences


def tokenize(s):
    """A tokenizer designed for chemistry texts."""
    return ChemTokenizer().tokenize(s)


# TODO: Chemical entity tagger
# - Custom feature detector?
# - Feature ideas:
# word ends with ([IV]+) and has 2+ characters before
# word made up of element symbols and numbers  (TiO2, H2O2) + Me, Et, Ph, Ac
# word matches solvent_re
# word matches \d[a-h]′?-\d[a-h]′? -> identifier
# nitr carb sulf oxy amine amino ene ane oxi methyl di tri tetra pent hex prop ethyl but thiol idase nyl onic phen cyan quino hydro azole ate phos cyclo acet yl tert iso one ium phthalo pyri borate BF4 H2O cis trans bis
# ends with ation ing protein
# starts with \d(,\d)*-
# starts with [SLp]-
# word starts with non-
# contains \w-\d-\w
# word is all uppercase letters
# Preceded by complex(es) ligand(s) molecule(s) compound(s) of in for with "presence of" "added to" "addition of" "/CM ("
# Followed by complex(es) ligand(s) molecule(s) compound(s) metal crystal moiety porphyrin salt aqueous
# Followed by calculation(s) test(s) technique(s) value(s) spectr(um|a|oscopy) software basis functional method studies measurements analysis = constant(s) log
# matches ^[.+?]\d?$
# presence of some greek letters (alpha, beta, ...)
# [PuO2Cl2(thf)2]2 [Co3(CO)9{C(CO)O(CH2)2O(CO)CH=CH2}]2
# greek letters
# digits
# hyphens, other special characters (·′)
# brackets (square, curly, regular) - at start and end? especially square
# Letter or closing bracket followed by number
# All caps, previous is bracket or comma, before that tokens first character match characters in this token
# Suffix -ic followed by word acid

# TODO: A Regex based tagger for chemical terms other than chemical names
