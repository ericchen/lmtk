# Word Lists

This directory contains word list files. Each file contains a single word per line.

## hyphen_joins.txt

English words that can be acceptably created when joining two hyphenated word components.

Created using:

- All words with at least 1 hyphenation point in moby hyphenation list.
    - excluding those containing spaces, punctuation, numbers.
- Select words from web2, web2a (freebsd) and common, compound, crossword (moby). Removed:
    - Those starting or ending with a hyphen
    - Those containing spaces
    - Those containing !"#$%&'()*+,./:;<=>?@[\]^_`{|}~
    - Those containing numbers
    - Those containing only uppercase characters
    - Those with a length of four characters or less
- Words generated through an automated comparison of the PDF (hyphenated) and HTML (not hyphenated) of a number of scientific papers.
- Some hyphenated words were removed, for when it is more common to have the unhyphenated form.
    - Care must be taken here, in case the unhyphenator encounters the hyphenated form but it is split at another point.

## hyphen_splits.txt

Word list used by tokenizers to determine whether to split a hyphenated word into two separate tokens.

Generally speaking, if a hyphenated word is present in this list, it is not split. If a hyphenated word is present but
with a space instead of the hyphen, it is split.

Created using:

- Hyphenated words from hyphen_joins.txt.
- Words containing hyphens and/or spaces in the OSCAR ontology (derived from the CHEBI ontology).

## lastnames.txt

Common last names.

Compiled from:

- Lists of most common last names for various countries on Wikipedia.
- Bibliographic dump of authors of around 25000 papers from the RSC.
- Manual additions.

Note that some last names have other meanings. For example:

April, August, Ball, Best, Black, Blank, Block, Bone, Born, Car, Colon, Committee, Con, Constable, Cool, Cross, Crown,
Crystal, Day, Dot, Ethyl, Ferro, Field, Fine, Flavin, Gene, Gold, Grand, Green, Grey, Guest, Hard, Head, House, Joule,
June, Kelvin, Lake, Lion, Loss, Low, Main, Major, Man, March, Marks, Max, May, Meta, Nation, Nickel, North, Page, Palm,
Pen, Plane, Planes, Plant, Pore, Post, Prime, Ray, Real, Red, Rest, Rich, Rod, Rose, Sample, Screen, Self, Shell,
Singleton, Sky, Smart, Sol, Solar, Southern, Spray, Star, Sun, Tab, Top, Trace, Trip, Urban, Van, Very, Violet, Wells,
White, Wild, Wood, Young
