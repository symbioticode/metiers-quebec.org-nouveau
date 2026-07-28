#!/usr/bin/env python3
import json

with open('/tmp/opencode/metiers-quebec-prototype/data/professions_details.json') as f:
    professions = json.load(f)

MOJIBAKE = {
    '\u00c3\u00a9': '\u00e9',  # é
    '\u00c3\u00a8': '\u00e8',  # è
    '\u00c3\u00a0': '\u00e0',  # à
    '\u00c3\u00a7': '\u00e7',  # ç
    '\u00c3\u00ae': '\u00ee',  # î
    '\u00c3\u00b4': '\u00f4',  # ô
    '\u00c3\u00b9': '\u00f9',  # ù
    '\u00c3\u00bc': '\u00fc',  # ü
    '\u00c3\u00a2': '\u00e2',  # â
    '\u00c3\u00aa': '\u00ea',  # ê
    '\u00c3\u00af': '\u00ef',  # ï
    '\u00c3\u0089': '\u00c9',  # É
    '\u00c3\u0088': '\u00c8',  # È
    '\u00c3\u0080': '\u00c0',  # À
    '\u00c3\u0087': '\u00c7',  # Ç
    '\u00c3\u00bb': '\u00fb',  # û
    '\u00c3\u0082': '\u00c2',  # Â
    '\u00c3\u0094': '\u00d4',  # Ô
    '\u00c3\u00b3': '\u00f3',  # ó
    '\u00c3\u00ad': '\u00ed',  # í
    '\u00c3\u008a': '\u00ca',  # Ê
    '\u00c3\u00a4': '\u00e4',  # ä
    '\u00c3\u00ab': '\u00eb',  # ë
    '\u00c3\u00ac': '\u00ec',  # ì
    '\u00c3\u00a3': '\u00e3',  # ã
    '\u00c3\u00a1': '\u00e1',  # á
    '\u00c3\u00b2': '\u00f2',  # ò
    '\u00c3\u00b1': '\u00f1',  # ñ
    '\u00c3\u0093': '\u00d3',  # Ó
    '\u00c3\u0096': '\u00d6',  # Ö
    '\u00c3\u009c': '\u00dc',  # Ü
    '\u00c3\u0084': '\u00c4',  # Ä
    '\u00c3\u009b': '\u00db',  # Û
    '\u00c3\u008b': '\u00cb',  # Ë
    '\u00c3\u008f': '\u00cf',  # Ï
    '\u00c3\u0095': '\u00d5',  # Õ
    '\u00c3\u0091': '\u00d1',  # Ñ
    '\u00c3\u0083': '\u00c3',  # Ã
    '\u00c2\u00ab': '\u00ab',  # «
    '\u00c2\u00bb': '\u00bb',  # »
    '\u00c2\u00a0': '\u00a0',  # non-breaking space
    '\u00c2\u00b0': '\u00b0',  # °
    '\u00c3\u0081': '\u00c1',  # Á
    '\u00c3\u009a': '\u00da',  # Ú
}

def fix_mojibake(text):
    if not text:
        return text
    for bad, good in MOJIBAKE.items():
        text = text.replace(bad, good)
    return text

fixed = 0
for p in professions:
    for sname in p.get('sections', {}):
        old = list(p['sections'][sname])
        p['sections'][sname] = [fix_mojibake(item) for item in p['sections'][sname]]
        if old != p['sections'][sname]:
            fixed += 1

with open('/tmp/opencode/metiers-quebec-prototype/data/professions_details.json', 'w') as f:
    json.dump(professions, f, ensure_ascii=False, indent=2)

print(f'Fixed {fixed} sections')

remaining = 0
for p in professions:
    for sname, content in p.get('sections', {}).items():
        for item in content:
            if '\u00c3' in item:
                remaining += 1
                break
print(f'Remaining Ã occurrences: {remaining}')
