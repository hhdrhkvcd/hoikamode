#!/usr/bin/env python3
"""Static checks for the generated mod (things that typically crash HOI4 on load)."""
import collections
import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pdx  # noqa: E402

mod = sys.argv[1]
icons_file = sys.argv[2] if len(sys.argv) > 2 else None
errors, warnings = [], []


def read(p):
    with open(p, encoding='utf-8-sig', errors='strict') as f:
        return f.read()


# 1. brace balance + utf8 for every script file
for p in glob.glob(os.path.join(mod, '**', '*.txt'), recursive=True):
    if '/map/' in p and os.path.basename(p) in ('buildings.txt', 'unitstacks.txt', 'railways.txt', 'supply_nodes.txt',
                                                'weatherpositions.txt', 'positions.txt'):
        continue
    try:
        t = read(p)
    except UnicodeDecodeError:
        errors.append(f'not utf-8: {p}')
        continue
    t = re.sub(r'"[^"\n]*"', '""', t)
    t = re.sub(r'#[^\n]*', '', t)
    if t.count('{') != t.count('}'):
        errors.append(f'brace mismatch {t.count("{")}/{t.count("}")}: {p}')

# 2. tags
tags = set(re.findall(r'^([A-Z][A-Z0-9]{2})\s*=', read(os.path.join(mod, 'common/country_tags/00_countries.txt')), re.M))
for line in read(os.path.join(mod, 'common/country_tags/00_countries.txt')).splitlines():
    m = re.match(r'(\w+)\s*=\s*"([^"]+)"', line)
    if m and not os.path.exists(os.path.join(mod, 'common', m.group(2))):
        errors.append(f'missing country file {m.group(2)}')

# 3. states
defs = {}
with open(os.path.join(mod, 'map/definition.csv'), encoding='latin-1') as f:
    for line in f:
        p = line.strip().split(';')
        if len(p) > 6 and p[0].isdigit():
            defs[int(p[0])] = p
terrains = collections.Counter(p[6] for p in defs.values())
for t in terrains:
    if t not in {'unknown', 'ocean', 'lakes', 'forest', 'hills', 'mountain', 'plains', 'urban', 'jungle', 'marsh', 'desert',
                 'water_fjords', 'water_shallow_sea', 'water_deep_ocean'}:
        errors.append(f'non-vanilla terrain {t}')
prov_state = {}
owner = {}
state_provs = {}
for p in glob.glob(os.path.join(mod, 'history/states/*.txt')):
    st = pdx.get(pdx.parse(read(p)), 'state')
    sid = int(pdx.get(st, 'id'))
    provs = [int(x) for x in pdx.values(pdx.get(st, 'provinces'))]
    state_provs[sid] = set(provs)
    for x in provs:
        if x in prov_state:
            errors.append(f'province {x} in states {prov_state[x]} and {sid}')
        if x not in defs:
            errors.append(f'province {x} of state {sid} not in definition.csv')
        prov_state[x] = sid
    h = pdx.get(st, 'history')
    owner[sid] = pdx.get(h, 'owner')
    for k, _, v in h:
        if k in ('owner', 'add_core_of', 'add_claim_by', 'controller') and v not in tags:
            errors.append(f'state {sid}: undefined tag {k}={v}')
    for vp in pdx.get_all(h, 'victory_points'):
        if int(pdx.values(vp)[0]) not in provs:
            errors.append(f'state {sid}: VP outside state')
    b = pdx.get(h, 'buildings', [])
    for k, _, v in b:
        if isinstance(v, list) and int(k) not in provs:
            errors.append(f'state {sid}: province building outside state')
missing = [x for x, p in defs.items() if p[4] == 'land' and x not in prov_state and x != 0]
if missing:
    errors.append(f'land provinces without state: {missing[:10]}')
owners = collections.defaultdict(list)
for sid, o in owner.items():
    owners[o].append(sid)

# 4. country history
for p in glob.glob(os.path.join(mod, 'history/countries/*.txt')):
    tag = os.path.basename(p)[:3]
    if tag not in tags:
        errors.append(f'history for undefined tag {tag}')
    t = read(p)
    cap = int(re.search(r'capital\s*=\s*(\d+)', t).group(1))
    if tag in owners and cap not in owners[tag]:
        errors.append(f'{tag}: capital {cap} not owned')
    m = re.search(r'oob\s*=\s*"([^"]+)"', t)
    if m and not os.path.exists(os.path.join(mod, 'history/units', m.group(1) + '.txt')):
        errors.append(f'{tag}: oob missing')
for tag in owners:
    if not glob.glob(os.path.join(mod, 'history/countries', f'{tag} - *.txt')):
        errors.append(f'owner {tag} without history')

# 5. units placement
for p in glob.glob(os.path.join(mod, 'history/units/*.txt')):
    tag = os.path.basename(p)[:3]
    t = read(p)
    for loc in re.findall(r'location\s*=\s*(\d+)', t):
        loc = int(loc)
        if loc not in prov_state:
            errors.append(f'{p}: location {loc} not a state province')
        elif tag in owners and owner[prov_state[loc]] != tag and not os.path.basename(p).endswith(('_1991.txt', '_1992.txt', '_2006.txt', '_2008.txt')):
            errors.append(f'{p}: location {loc} not owned by {tag}')
    for tmpl in re.findall(r'division_template\s*=\s*"([^"]+)"', t):
        if f'name = "{tmpl}"' not in t:
            errors.append(f'{p}: template {tmpl} not defined')

# 6. localisation
loc = {}
for p in glob.glob(os.path.join(mod, 'localisation/**/*.yml'), recursive=True):
    raw = open(p, 'rb').read()
    if not raw.startswith(b'\xef\xbb\xbf'):
        errors.append(f'loc without BOM: {p}')
    lang = 'russian' if 'russian' in p else 'english'
    lines = raw.decode('utf-8-sig').splitlines()
    if not lines[0].startswith(f'l_{lang}:'):
        errors.append(f'bad loc header {p}')
    for ln in lines[1:]:
        if not ln.strip() or ln.strip().startswith('#'):
            continue
        m = re.match(r'^ ([A-Za-z0-9_.\-]+):\d* "(.*)"$', ln)
        if not m:
            errors.append(f'bad loc line in {os.path.basename(p)}: {ln[:80]}')
            continue
        if re.search(r'(?<!\\)"', m.group(2)):
            errors.append(f'unescaped quote: {ln[:80]}')
        loc.setdefault(lang, set()).add(m.group(1))

# 7. focus trees
icons = set(open(icons_file).read().split()) if icons_file else None
ideas = set(re.findall(r'^\t\t(BC_\w+)\s*=', read(os.path.join(mod, 'common/ideas/bc_ideas.txt')), re.M))
all_focus = set()
for p in glob.glob(os.path.join(mod, 'common/national_focus/*.txt')):
    tree = pdx.get(pdx.parse(read(p)), 'focus_tree')
    fs = pdx.get_all(tree, 'focus')
    ids = [pdx.get(f, 'id') for f in fs]
    pos = collections.Counter((pdx.get(f, 'x'), pdx.get(f, 'y')) for f in fs)
    for k, v in pos.items():
        if v > 1:
            errors.append(f'{os.path.basename(p)}: {v} focuses at {k}')
    for i in ids:
        if i in all_focus:
            errors.append(f'duplicate focus id {i}')
        all_focus.add(i)
    for f in fs:
        fid = pdx.get(f, 'id')
        y = int(pdx.get(f, 'y'))
        for pre in pdx.get_all(f, 'prerequisite') + pdx.get_all(f, 'mutually_exclusive'):
            for _, _, v in pre:
                if v not in ids:
                    errors.append(f'{fid}: unknown focus ref {v}')
        for pre in pdx.get_all(f, 'prerequisite'):
            for _, _, v in pre:
                py = int(pdx.get(next(ff for ff in fs if pdx.get(ff, 'id') == v), 'y'))
                if py >= y:
                    warnings.append(f'{fid}: prerequisite {v} not above')
        if icons is not None and pdx.get(f, 'icon') not in icons:
            errors.append(f'{fid}: icon {pdx.get(f, "icon")} not in vanilla goals.gfx')
        for lang in ('russian', 'english'):
            for key in (fid, fid + '_desc'):
                if key not in loc.get(lang, ()):
                    errors.append(f'missing loc {lang}:{key}')
        txt = pdx.dump(pdx.get(f, 'completion_reward'))
        for idea in re.findall(r'(?:add_ideas|remove_ideas)\s*=\s*(\w+)', txt):
            if idea not in ideas:
                errors.append(f'{fid}: unknown idea {idea}')
    tid = pdx.get(tree, 'id')
for t in ('SER_1980_tree',):
    if t not in loc.get('russian', ()):
        warnings.append(f'tree name loc {t}')

# 8. events
ev_text = read(os.path.join(mod, 'events/bc_yugoslavia.txt'))
ev_ids = re.findall(r'^\tid = (\S+)', ev_text, re.M)
for e in ev_ids:
    for lang in ('russian', 'english'):
        for suf in ('.t', '.d', '.a'):
            if e + suf not in loc.get(lang, ()):
                errors.append(f'missing loc {lang}:{e}{suf}')
called = set(re.findall(r'country_event\s*=\s*\{\s*id\s*=\s*(\S+)', open(os.path.join(mod, 'common/national_focus/bc_ser_focus.txt')).read()
                                                                        + ''.join(open(p).read() for p in glob.glob(os.path.join(mod, 'common/national_focus/*.txt')))))
for c in called:
    if c not in ev_ids:
        errors.append(f'called event {c} missing')
for oob in re.findall(r'load_oob\s*=\s*"([^"]+)"', ev_text):
    if not os.path.exists(os.path.join(mod, 'history/units', oob + '.txt')):
        errors.append(f'missing oob {oob}')
for tag in re.findall(r'release\s*=\s*(\w+)', ev_text):
    if tag not in tags:
        errors.append(f'release undefined tag {tag}')

# 9. state names
for sid in state_provs:
    for lang in ('russian', 'english'):
        if f'STATE_{sid}' not in loc.get(lang, ()):
            warnings.append(f'no state name {lang} {sid}')
for t in tags:
    if t not in loc.get('russian', ()):
        warnings.append(f'no country name {t}')

# 10. flags for owners
for t in owners:
    if not os.path.exists(os.path.join(mod, 'gfx/flags', t + '.tga')):
        warnings.append(f'no flag {t}')

print(f'states={len(state_provs)} owners={len(owners)} tags={len(tags)} focuses={len(all_focus)} events={len(ev_ids)}')
print('WARNINGS', len(warnings))
for w in warnings[:30]:
    print('  W', w)
print('ERRORS', len(errors))
for e in errors[:80]:
    print('  E', e)
sys.exit(1 if errors else 0)
