#!/usr/bin/env python3
"""Builds the standalone "Balkan Collapse 1980" HOI4 mod.

Inputs (see README_BUILD.md):
  --md-archive  folder with the extracted милениум.part1.rar (history/, map/, states/)
  --md-repo     sparse checkout of github.com/MillenniumDawn/Millennium-Dawn
                (common/country_tags, common/countries, localisation, gfx/flags)
  --old-mod     extracted Balkan_Collapse_1980 (9).zip (pictures, Balkan flags)
  --out         output folder (the mod folder "Balkan_Collapse" + .mod file are created inside)

The Millennium Dawn map/state data is © Millennium Dawn team, CC BY-SA 4.0.
"""
import argparse
import collections
import glob
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pdx  # noqa: E402
import balkan_content  # noqa: E402

IDEOLOGIES = ['democratic', 'communism', 'fascism', 'neutrality']

# --------------------------------------------------------------------------
# 1980 world: owners of the year-2000 Millennium map remapped to May 1980
# --------------------------------------------------------------------------
OWNER_1980 = {}
for t in 'UKR BLR LIT LAT EST MLV PMR GEO ABK SOO ARM NKR AZE KAZ UZB TRK KYR TAJ CHE CRM DPR LPR'.split():
    OWNER_1980[t] = 'SOV'
for t in 'CRO SLV BOS RSK MNT KOS FYR HZG VOJ'.split():
    OWNER_1980[t] = 'SER'           # SFRY is played with the SER tag
OWNER_1980.update({
    'SLO': 'CZE', 'ERI': 'ETH', 'SSU': 'SUD', 'NAM': 'SAF', 'TIM': 'IND',
    'AQY': 'YEM', 'HOU': 'YEM',
    'SML': 'SOM', 'PUN': 'SOM', 'SNA': 'SOM', 'JUB': 'SOM', 'SWS': 'SOM', 'SHB': 'SOM', 'AIA': 'SOM',
    'TAL': 'AFG', 'BDA': 'AFG', 'HAZ': 'AFG',
    'KAC': 'BRM', 'SHN': 'BRM', 'KAR': 'BRM', 'WAA': 'BRM', 'NHN': 'BRM', 'CHS': 'BRM', 'ARK': 'BRM',
    'HEZ': 'LEB', 'PAL': 'ISR', 'HAM': 'ISR',
    'KUR': 'IRQ', 'PUK': 'IRQ', 'IEK': 'IRQ',
    'RCD': 'DRC', 'MLC': 'DRC', 'UNI': 'AGL', 'LUR': 'LIB', 'AFR': 'SIE', 'SHA': 'MOR',
    'TML': 'SRI', 'NPM': 'NEP',
    'HKG': 'ENG', 'BRU': 'ENG', 'BLZ': 'ENG', 'ANT': 'ENG', 'STK': 'ENG',
    'MAC': 'POR', 'MAR': 'USA', 'MIC': 'USA', 'PAU': 'USA',
    'GRN': 'DEN', 'FAO': 'DEN',
})
DDR_STATES = {1079, 45, 44, 539, 545, 972}   # Brandenburg, Berlin, Saxony, Mecklenburg, Thuringia, Saxony-Anhalt
MILITARY_BASE_OWNER = {488: 'KUW', 624: 'BHR'}  # bases that did not exist in 1980

YUGO_STATES = {
    'SLV': [124, 125], 'CRO': [126, 127], 'BOS': [128, 129, 1051, 1052, 1053, 1054],
    'SER': [130, 131, 132, 998], 'KOS': [133], 'MNT': [134], 'FYR': [135, 136],
}
RSK_STATES = [129, 1053, 1054]

# Vanilla building types we keep (everything else is Millennium-only)
STATE_BUILDINGS = {'infrastructure', 'industrial_complex', 'arms_factory', 'dockyard', 'air_base',
                   'anti_air_building', 'radar_station', 'synthetic_refinery', 'fuel_silo',
                   'nuclear_reactor', 'bunker', 'coastal_bunker', 'naval_base'}
PROVINCE_BUILDINGS = {'naval_base', 'bunker', 'coastal_bunker'}
MAP_BUILDING_TYPES = {'air_base', 'anti_air_building', 'arms_factory', 'bunker', 'coastal_bunker', 'dockyard',
                      'floating_harbor', 'fuel_silo', 'industrial_complex', 'landmark_spawn', 'naval_base_spawn',
                      'nuclear_reactor', 'nuclear_reactor_spawn', 'radar_station', 'rocket_site_spawn',
                      'special_project_facility_spawn', 'stronghold_network', 'supply_node', 'synthetic_refinery'}
RESOURCES = {'oil', 'aluminium', 'rubber', 'tungsten', 'steel', 'chromium'}
# Millennium state_category -> vanilla state_category (+ shared building slots)
CATEGORY = {'state_inhospitable': 'wasteland', 'state_military_base': 'enclave', 'state_00': 'pastoral',
            'state_01': 'rural', 'state_02': 'town', 'state_03': 'large_town', 'state_04': 'city',
            'state_05': 'city', 'state_06': 'large_city', 'state_07': 'large_city', 'state_08': 'large_city'}
SLOTS = {'wasteland': 0, 'enclave': 0, 'pastoral': 1, 'rural': 2, 'town': 4, 'large_town': 5, 'city': 6,
         'large_city': 8, 'metropolis': 10, 'megalopolis': 12}
GFX_CULTURE = {'arab_republic_gfx': 'middle_eastern_gfx', 'asian_european_gfx': 'eastern_european_gfx',
               'donbas_gfx': 'eastern_european_gfx', 'jihadist_gfx': 'middle_eastern_gfx',
               'kurdish_gfx': 'middle_eastern_gfx', 'saharan_gfx': 'african_gfx'}

COMMUNIST_1980 = set('SOV CHI SER CZE POL HUN ROM BUL DDR ALB MON NKO VIE LAO CBD CUB AFG ETH AGL MOZ BEN CNG SOM NIC'.split())
DEMOCRATIC_1980 = set(('USA ENG FRA GER ITA JAP CAN AST NZL HOL BEL LUX DEN NRY SWE FIN ICE IRE SWI AUS POR SPR GRE '
                       'ISR RAJ SRI VEN COL COS PRU ECU DOM JAM BAR TRI BAH MLT CYP BOT MRT PAP FIJ MLT SMA LIC').split())

# (name, sub-ideology) for leaders in power on 1 May 1980
LEADERS_1980 = {
    'SOV': ('Леонид Брежнев', 'leninism'), 'USA': ('Jimmy Carter', 'liberalism'),
    'ENG': ('Margaret Thatcher', 'conservatism'), 'FRA': ("Valéry Giscard d'Estaing", 'conservatism'),
    'GER': ('Helmut Schmidt', 'socialism'), 'DDR': ('Erich Honecker', 'leninism'),
    'ITA': ('Francesco Cossiga', 'conservatism'), 'JAP': ('Masayoshi Ōhira', 'conservatism'),
    'CHI': ('Hua Guofeng', 'marxism'), 'POL': ('Edward Gierek', 'leninism'), 'CZE': ('Gustáv Husák', 'leninism'),
    'HUN': ('János Kádár', 'leninism'), 'ROM': ('Nicolae Ceaușescu', 'stalinism'), 'BUL': ('Todor Zhivkov', 'leninism'),
    'ALB': ('Enver Hoxha', 'anti_revisionism'), 'CUB': ('Fidel Castro', 'marxism'), 'TUR': ('Süleyman Demirel', 'oligarchism'),
    'PER': ('Ruhollah Khomeini', 'despotism'), 'IRQ': ('Saddam Hussein', 'despotism'), 'SYR': ('Hafez al-Assad', 'despotism'),
    'EGY': ('Anwar Sadat', 'oligarchism'), 'ISR': ('Menachem Begin', 'conservatism'), 'LBA': ('Muammar Gaddafi', 'despotism'),
    'SAU': ('Khalid bin Abdulaziz', 'despotism'), 'RAJ': ('Indira Gandhi', 'socialism'), 'PAK': ('Muhammad Zia-ul-Haq', 'despotism'),
    'AFG': ('Babrak Karmal', 'leninism'), 'VIE': ('Lê Duẩn', 'marxism'), 'NKO': ('Kim Il-sung', 'stalinism'),
    'SPR': ('Adolfo Suárez', 'conservatism'), 'POR': ('Francisco Sá Carneiro', 'conservatism'),
    'CAN': ('Pierre Trudeau', 'liberalism'), 'AST': ('Malcolm Fraser', 'conservatism'), 'ARG': ('Jorge Videla', 'despotism'),
    'BRA': ('João Figueiredo', 'oligarchism'), 'CHL': ('Augusto Pinochet', 'despotism'), 'MEX': ('José López Portillo', 'oligarchism'),
    'ETH': ('Mengistu Haile Mariam', 'stalinism'), 'SAF': ('P. W. Botha', 'oligarchism'), 'AUS': ('Bruno Kreisky', 'socialism'),
    'SWE': ('Thorbjörn Fälldin', 'liberalism'), 'NRY': ('Odvar Nordli', 'socialism'), 'DEN': ('Anker Jørgensen', 'socialism'),
    'FIN': ('Urho Kekkonen', 'liberalism'), 'HOL': ('Dries van Agt', 'conservatism'), 'BEL': ('Wilfried Martens', 'conservatism'),
    'MON': ('Yumjaagiin Tsedenbal', 'leninism'), 'LAO': ('Kaysone Phomvihane', 'marxism'), 'CBD': ('Heng Samrin', 'marxism'),
    'AGL': ('José Eduardo dos Santos', 'marxism'), 'MOZ': ('Samora Machel', 'marxism'), 'ZIM': ('Robert Mugabe', 'oligarchism'),
    'NIC': ('Daniel Ortega', 'marxism'), 'TAI': ('Chiang Ching-kuo', 'oligarchism'), 'IND': ('Suharto', 'despotism'),
    'PHI': ('Ferdinand Marcos', 'despotism'), 'GRE': ('Georgios Rallis', 'conservatism'), 'IRE': ('Charles Haughey', 'conservatism'),
}

NAME_1980 = {  # tag: (ru, en, ru_adj, en_adj)
    'SOV': ('СССР', 'Soviet Union', 'советский', 'Soviet'),
    'GER': ('ФРГ', 'West Germany', 'западногерманский', 'West German'),
    'DDR': ('ГДР', 'East Germany', 'восточногерманский', 'East German'),
    'CZE': ('Чехословакия', 'Czechoslovakia', 'чехословацкий', 'Czechoslovak'),
    'CHI': ('КНР', "People's Republic of China", 'китайский', 'Chinese'),
    'DRC': ('Заир', 'Zaire', 'заирский', 'Zairean'),
    'BRM': ('Бирма', 'Burma', 'бирманский', 'Burmese'),
    'CBD': ('Кампучия', 'Kampuchea', 'кампучийский', 'Kampuchean'),
    'SRI': ('Шри-Ланка', 'Sri Lanka', 'ланкийский', 'Sri Lankan'),
    'BFA': ('Верхняя Вольта', 'Upper Volta', 'вольтийский', 'Voltaic'),
    'BEN': ('Бенин', 'Benin', 'бенинский', 'Beninese'),
    'YEM': ('Йемен', 'Yemen', 'йеменский', 'Yemeni'),
    'SWA': ('Свазиленд', 'Swaziland', 'свазилендский', 'Swazi'),
}


def read(path):
    with open(path, encoding='utf-8-sig', errors='replace') as f:
        return f.read()


def write(path, text, bom=False):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8-sig' if bom else 'utf-8', newline='\n') as f:
        f.write(text)


def num(s, default=0.0):
    try:
        return float(s)
    except (TypeError, ValueError):
        return default


# --------------------------------------------------------------------------
# States
# --------------------------------------------------------------------------
def convert_states(md_archive):
    states = {}
    for path in sorted(glob.glob(os.path.join(md_archive, 'history', 'states', '*.txt'))):
        blk = pdx.parse(read(path))
        st = pdx.get(blk, 'state')
        if not isinstance(st, list):
            continue
        sid = int(pdx.get(st, 'id'))
        hist = pdx.get(st, 'history', [])
        owner = pdx.get(hist, 'owner')
        cores = [v for v in pdx.get_all(hist, 'add_core_of') if isinstance(v, str)]
        claims = [v for v in pdx.get_all(hist, 'add_claim_by') if isinstance(v, str)]
        vps = []
        for v in pdx.get_all(hist, 'victory_points'):
            vals = pdx.values(v) if isinstance(v, list) else []
            if len(vals) >= 2:
                vps.append((int(vals[0]), num(vals[1])))
        blds = {}
        prov_blds = collections.defaultdict(dict)
        for b in pdx.get_all(hist, 'buildings'):
            for k, _, v in b:
                if k is None:
                    continue
                if isinstance(v, list) and k.isdigit():
                    for kk, _, vv in v:
                        if kk in PROVINCE_BUILDINGS and isinstance(vv, str):
                            prov_blds[int(k)][kk] = int(num(vv))
                elif isinstance(v, str):
                    if k == 'offices':
                        blds['industrial_complex'] = blds.get('industrial_complex', 0) + int(num(v))
                    elif k in STATE_BUILDINGS and k not in PROVINCE_BUILDINGS:
                        blds[k] = blds.get(k, 0) + int(num(v))
        res = {}
        r = pdx.get(st, 'resources')
        if isinstance(r, list):
            for k, _, v in r:
                if k in RESOURCES and num(v) > 0:
                    res[k] = num(v)
        provinces = [int(p) for p in pdx.values(pdx.get(st, 'provinces', []))]
        states[sid] = dict(
            id=sid, file=os.path.basename(path), owner=owner, cores=cores, claims=claims, vps=vps,
            blds=blds, prov_blds=prov_blds, res=res, provinces=provinces,
            manpower=int(num(pdx.get(st, 'manpower'), 1000)),
            category=pdx.get(st, 'state_category', 'state_01'),
            impassable=pdx.get(st, 'impassable') == 'yes',
            local_supplies=pdx.get(st, 'local_supplies'),
            bmlf=pdx.get(st, 'buildings_max_level_factor'),
        )
    # ---- remap to 1980
    for s in states.values():
        o = s['owner']
        new = OWNER_1980.get(o, o)
        if s['id'] in DDR_STATES:
            new = 'DDR'
        if s['id'] in MILITARY_BASE_OWNER:
            new = MILITARY_BASE_OWNER[s['id']]
        s['owner'] = new
        if new not in s['cores'] and s['category'] != 'state_military_base':
            s['cores'].append(new)
    # Yugoslav cores: every republic keeps its own core, SFRY (SER) gets cores everywhere,
    # cores are removed again by the break-up events.
    for tag, ids in YUGO_STATES.items():
        for sid in ids:
            s = states[sid]
            s['owner'] = 'SER'
            s['cores'] = [c for c in s['cores'] if c not in ('SER', 'BOS', 'RSK', 'HZG', 'VOJ', 'CRO', 'SLV', 'KOS', 'MNT', 'FYR')]
            s['cores'] += sorted({tag, 'SER'})
            if sid in RSK_STATES:
                s['cores'].append('RSK')
            if sid == 1052:
                s['cores'].append('HZG')
            if sid in (130, 998):
                s['cores'].append('VOJ')
            s['claims'] = []
    return states


def write_state(s, outdir):
    cat = CATEGORY.get(s['category'])
    if cat is None:
        n = int(s['category'].split('_')[1]) if s['category'].startswith('state_') else 1
        cat = 'metropolis' if n <= 12 else 'megalopolis'
    slots = SLOTS[cat]
    blds = dict(s['blds'])
    # respect shared slots (civ + mil + dockyards)
    shared = ['industrial_complex', 'arms_factory', 'dockyard', 'synthetic_refinery', 'fuel_silo', 'nuclear_reactor']
    used = 0
    for b in shared:
        if b in blds:
            blds[b] = max(0, min(blds[b], slots - used))
            used += blds[b]
            if blds[b] == 0:
                del blds[b]
    if 'infrastructure' in blds:
        blds['infrastructure'] = max(1, min(5, blds['infrastructure']))
    for b in ('air_base',):
        if b in blds:
            blds[b] = min(10, blds[b])
    for b in ('anti_air_building', 'radar_station'):
        if b in blds:
            blds[b] = min(5, blds[b])
    if s['owner'] == 'SER' and s['id'] in sum(YUGO_STATES.values(), []):
        blds['infrastructure'] = max(blds.get('infrastructure', 1), 3)
    provs = set(s['provinces'])
    L = ['state = {', f'\tid = {s["id"]}', f'\tname = "STATE_{s["id"]}"', f'\tmanpower = {max(1, s["manpower"])}',
         f'\tstate_category = {cat}']
    if s['impassable']:
        L.append('\timpassable = yes')
    if s['res']:
        L.append('\tresources = {')
        for k, v in sorted(s['res'].items()):
            L.append(f'\t\t{k} = {v:g}')
        L.append('\t}')
    L.append('\thistory = {')
    L.append(f'\t\towner = {s["owner"]}')
    for p, v in s['vps']:
        if p in provs:
            L.append(f'\t\tvictory_points = {{ {p} {v:g} }}')
    if blds or s['prov_blds']:
        L.append('\t\tbuildings = {')
        for k, v in blds.items():
            L.append(f'\t\t\t{k} = {v}')
        for p, d in s['prov_blds'].items():
            if p in provs and d:
                L.append(f'\t\t\t{p} = {{ ' + ' '.join(f'{k} = {min(v, 10)}' for k, v in d.items()) + ' }')
        L.append('\t\t}')
    for c in dict.fromkeys(s['cores']):
        L.append(f'\t\tadd_core_of = {c}')
    for c in dict.fromkeys(s['claims']):
        if c != s['owner'] and c not in s['cores']:
            L.append(f'\t\tadd_claim_by = {c}')
    L.append('\t}')
    L.append('\tprovinces = {\n\t\t' + ' '.join(map(str, s['provinces'])) + '\n\t}')
    if s['local_supplies'] is not None:
        L.append(f'\tlocal_supplies = {s["local_supplies"]}')
    if s['bmlf'] is not None:
        L.append(f'\tbuildings_max_level_factor = {s["bmlf"]}')
    L.append('}')
    write(os.path.join(outdir, 'history', 'states', f'{s["id"]}-{os.path.splitext(s["file"])[0].split("-", 1)[-1]}.txt'),
          '\n'.join(L) + '\n')


# --------------------------------------------------------------------------
# Map
# --------------------------------------------------------------------------
def build_map(md_archive, out):
    src = os.path.join(md_archive, 'map')
    dst = os.path.join(out, 'map')
    os.makedirs(dst, exist_ok=True)
    for name in os.listdir(src):
        p = os.path.join(src, name)
        if os.path.isdir(p) or name.endswith('.png'):
            continue
        if name == 'definition.csv':
            with open(p, encoding='latin-1') as f:
                lines = f.read().split('\n')
            fixed = []
            for line in lines:
                parts = line.split(';')
                if len(parts) > 6 and parts[6] == 'supercity':   # Millennium-only terrain
                    parts[6] = 'urban'
                fixed.append(';'.join(parts))
            with open(os.path.join(dst, name), 'w', encoding='latin-1', newline='') as f:
                f.write('\n'.join(fixed))
        elif name == 'buildings.txt':
            with open(p, encoding='latin-1') as f:
                keep = [l for l in f if len(l.split(';')) > 1 and l.split(';')[1] in MAP_BUILDING_TYPES]
            with open(os.path.join(dst, name), 'w', encoding='latin-1', newline='') as f:
                f.writelines(keep)
        else:
            shutil.copy2(p, os.path.join(dst, name))
    # strategic regions: drop Millennium-only static modifiers / naval terrains
    os.makedirs(os.path.join(dst, 'strategicregions'), exist_ok=True)
    for p in glob.glob(os.path.join(src, 'strategicregions', '*.txt')):
        t = read(p)
        t = re.sub(r'\n\s*static_modifiers\s*=\s*\{[^{}]*(\{[^{}]*\}[^{}]*)*\}', '', t)
        t = re.sub(r'\n\s*naval_terrain\s*=\s*(ocean|water_littoral)\b', '', t)
        write(os.path.join(dst, 'strategicregions', os.path.basename(p)), t)
    os.makedirs(os.path.join(dst, 'supplyareas'), exist_ok=True)
    for p in glob.glob(os.path.join(src, 'supplyareas', '*.txt')):
        shutil.copy2(p, os.path.join(dst, 'supplyareas', os.path.basename(p)))
    shutil.copytree(os.path.join(src, 'terrain'), os.path.join(dst, 'terrain'), dirs_exist_ok=True)


# --------------------------------------------------------------------------
# Tags, countries, localisation
# --------------------------------------------------------------------------
def load_md_tags(md_repo):
    tags = collections.OrderedDict()
    for line in read(os.path.join(md_repo, 'common', 'country_tags', '00_countries.txt')).splitlines():
        m = re.match(r'\s*([A-Z][A-Z0-9]{2})\s*=\s*"([^"]+)"', line)
        if m:
            tags[m.group(1)] = m.group(2)
    return tags


def parse_colors(md_repo):
    """tag -> (color 'r g b', color_ui 'r g b') read with regexes (rgb/hsv blocks)."""
    colors = {}
    text = re.sub(r'#[^\n]*', '', read(os.path.join(md_repo, 'common', 'countries', 'colors.txt')))
    for m in re.finditer(r'\b([A-Z][A-Z0-9]{2})\s*=\s*\{(.*?)\n\}', text, re.S):
        body = m.group(2)
        c = re.search(r'\bcolor\s*=\s*rgb\s*\{\s*([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*\}', body)
        u = re.search(r'\bcolor_ui\s*=\s*rgb\s*\{\s*([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*\}', body)
        if c:
            colors[m.group(1)] = (' '.join(c.groups()), ' '.join(u.groups()) if u else ' '.join(c.groups()))
    return colors


def load_yml(path):
    d = collections.OrderedDict()
    if not os.path.exists(path):
        return d
    for line in read(path).splitlines():
        m = re.match(r'\s*([A-Za-z0-9_.\-]+):\d*\s*"(.*)"\s*(#.*)?$', line)
        if m:
            d[m.group(1)] = m.group(2)
    return d


def yml(lang, entries):
    out = [f'l_{lang}:']
    for k, v in entries.items():
        v = v.replace('"', '\\"') if '\\"' not in v else v
        out.append(f' {k}:0 "{v}"')
    return '\n'.join(out) + '\n'


def build_countries(md_repo, out, owners):
    tags = load_md_tags(md_repo)
    tags['DDR'] = 'countries/East Germany.txt'
    colors = parse_colors(md_repo)
    lines = ['# Country tags: Millennium Dawn tag set (CC BY-SA 4.0) + DDR for the 1980 scenario']
    for tag in tags:
        lines.append(f'{tag} = "countries/BC_{tag}.txt"')
    write(os.path.join(out, 'common', 'country_tags', '00_countries.txt'), '\n'.join(lines) + '\n')
    col_out = []
    for tag, rel in tags.items():
        src = os.path.join(md_repo, 'common', rel)
        gc, gc2, color = 'eastern_european_gfx', 'eastern_european_2d', None
        if os.path.exists(src):
            b = pdx.parse(read(src))
            gc = GFX_CULTURE.get(pdx.get(b, 'graphical_culture', gc), pdx.get(b, 'graphical_culture', gc))
            gc2 = pdx.get(b, 'graphical_culture_2d', gc2)
            c = pdx.get(b, 'color')
            if isinstance(c, list):
                color = ' '.join(pdx.values(c)[:3])
        if tag == 'DDR':
            gc, gc2, color = 'western_european_gfx', 'western_european_2d', '120 40 40'
        if tag in balkan_content.COUNTRY_COLORS:
            color = balkan_content.COUNTRY_COLORS[tag]
        if color is None:
            color = '128 128 128'
        color = ' '.join(str(max(0, min(255, int(float(c))))) for c in color.split()[:3])
        write(os.path.join(out, 'common', 'countries', f'BC_{tag}.txt'),
              f'graphical_culture = {gc}\ngraphical_culture_2d = {gc2}\ncolor = {{ {color} }}\n')
        rgb = color.split()
        ui = colors[tag][1].split() if tag in colors and tag not in balkan_content.COUNTRY_COLORS else rgb
        ui = [str(max(0, min(255, int(float(c))))) for c in ui]
        col_out.append(f'{tag} = {{\n\tcolor = rgb {{ {" ".join(rgb)} }}\n\tcolor_ui = rgb {{ {" ".join(ui)} }}\n}}')
    for k, v in colors.items():   # dynamic civil-war tags (D01...) keep their colours
        if k not in tags:
            col_out.append(f'{k} = {{\n\tcolor = rgb {{ {v[0]} }}\n\tcolor_ui = rgb {{ {v[1]} }}\n}}')
    write(os.path.join(out, 'common', 'countries', 'colors.txt'), '\n'.join(col_out) + '\n')
    # an empty 01_countries.txt overrides any vanilla secondary tag file (avoids duplicate tags)
    write(os.path.join(out, 'common', 'country_tags', '01_countries.txt'), '\n')
    return tags


def country_names(md_repo, tags):
    loc = {}
    for lang in ('english', 'russian'):
        md = load_yml(os.path.join(md_repo, 'localisation', lang, f'countries_l_{lang}.yml'))
        d = collections.OrderedDict()
        for tag in tags:
            base = md.get(f'{tag}_neutrality') or md.get(f'{tag}_democratic') or md.get(tag) or tag
            adj = md.get(f'{tag}_neutrality_ADJ') or md.get(f'{tag}_ADJ') or base
            if tag in NAME_1980:
                ru, en, ru_adj, en_adj = NAME_1980[tag]
                base, adj = (ru, ru_adj) if lang == 'russian' else (en, en_adj)
            if tag == 'DDR' and tag not in NAME_1980:
                base = adj = 'East Germany'
            d[tag] = base
            d[f'{tag}_DEF'] = base
            d[f'{tag}_ADJ'] = adj
            for ide in IDEOLOGIES:
                d[f'{tag}_{ide}'] = base
                d[f'{tag}_{ide}_DEF'] = base
                d[f'{tag}_{ide}_ADJ'] = adj
        d.update(balkan_content.country_name_overrides(lang))
        loc[lang] = d
    return loc


def build_localisation(md_repo, out, tags):
    names = country_names(md_repo, tags)
    for lang in ('english', 'russian'):
        rep = os.path.join(out, 'localisation', lang, 'replace')
        for fname in (f'state_names_l_{lang}.yml', f'victory_points_l_{lang}.yml',
                      f'strategic_region_names_l_{lang}.yml'):
            d = load_yml(os.path.join(md_repo, 'localisation', lang, fname))
            write(os.path.join(rep, 'bc_' + fname), yml(lang, d), bom=True)
        write(os.path.join(rep, f'bc_countries_l_{lang}.yml'), yml(lang, names[lang]), bom=True)


# --------------------------------------------------------------------------
# Country history + OOB
# --------------------------------------------------------------------------
BASE_TECH = ['infantry_weapons', 'infantry_weapons1', 'infantry_weapons2', 'tech_support', 'tech_engineers',
             'tech_recon', 'tech_mountaineers', 'gw_artillery', 'interwar_artillery', 'interwar_antiair',
             'interwar_antitank', 'support_weapons', 'motorised_infantry', 'basic_train', 'gwtank',
             'basic_light_tank_chassis', 'early_fighter', 'early_bomber', 'electronic_mechanical_engineering',
             'radio', 'basic_machine_tools', 'construction1', 'fuel_silos', 'early_destroyer', 'early_submarine',
             'early_light_cruiser', 'trench_warfare', 'fleet_in_being']
ADVANCED_TECH = ['infantry_weapons', 'improved_infantry_weapons', 'support_weapons2', 'artillery1', 'artillery2',
                 'antitank1', 'antiair1', 'tech_military_police', 'paratroopers', 'marines', 'mechanised_infantry',
                 'basic_medium_tank_chassis', 'improved_light_tank_chassis', 'fighter1', 'cas1', 'tactical_bomber1',
                 'improved_machine_tools', 'construction2', 'mechanical_computing', 'improved_radio', 'radio_detection',
                 'synth_oil_experiments', 'basic_destroyer', 'basic_light_cruiser', 'basic_submarine',
                 'grand_battle_plan', 'superior_firepower', 'mobile_warfare', 'mass_assault']
MAJORS = set('USA SOV ENG FRA GER CHI JAP ITA'.split())
DEVELOPED = MAJORS | set('DDR CZE POL HUN ROM BUL SER SWE SWI CAN AST HOL BEL ISR SPR TUR RAJ BRA ARG KOR TAI'.split())


def build_history(md_archive, out, states, tags):
    owned = collections.defaultdict(list)
    for s in states.values():
        owned[s['owner']].append(s)
    md_capitals = {}
    for p in glob.glob(os.path.join(md_archive, 'history', 'countries', '*.txt')):
        tag = os.path.basename(p)[:3]
        m = re.search(r'^\s*capital\s*=\s*(\d+)', read(p), re.M)
        if m:
            md_capitals[tag] = int(m.group(1))
    capitals = {}
    for tag, sts in owned.items():
        cap = md_capitals.get(tag)
        if tag == 'DDR':
            cap = 45
        if tag == 'GER':
            cap = 966  # Bonn
        if cap not in [s['id'] for s in sts]:
            cap = max(sts, key=lambda s: (sum(v for _, v in s['vps']), s['manpower']))['id']
        capitals[tag] = cap
    balkan = balkan_content.HISTORY
    for tag in sorted(set(owned) | set(balkan)):
        if tag not in tags:
            raise SystemExit(f'owner tag {tag} not defined')
        if tag in balkan:
            body = balkan[tag]
            cap = capitals.get(tag, balkan_content.CAPITALS[tag])
            text = f'capital = {balkan_content.CAPITALS.get(tag, cap)}\n' + body
        else:
            cap = capitals[tag]
            ruling = 'communism' if tag in COMMUNIST_1980 else 'democratic' if tag in DEMOCRATIC_1980 else 'neutrality'
            pops = {'communism': dict(democratic=5, fascism=2, communism=80, neutrality=13),
                    'democratic': dict(democratic=65, fascism=3, communism=10, neutrality=22),
                    'neutrality': dict(democratic=15, fascism=8, communism=12, neutrality=65)}[ruling]
            tech = BASE_TECH + (ADVANCED_TECH if tag in DEVELOPED else [])
            L = [f'capital = {cap}', f'oob = "{tag}_1980"',
                 f'set_research_slots = {4 if tag in MAJORS else 3 if tag in DEVELOPED else 2}',
                 'set_technology = {'] + [f'\t{t} = 1' for t in dict.fromkeys(tech)] + ['}',
                 'set_politics = {', f'\truling_party = {ruling}', '\tlast_election = "1978.1.1"',
                 '\telection_frequency = 48', f'\telections_allowed = {"yes" if ruling == "democratic" else "no"}', '}',
                 'set_popularities = { ' + ' '.join(f'{k} = {v}' for k, v in pops.items()) + ' }',
                 f'set_stability = 0.6', f'set_war_support = {0.4 if tag in MAJORS else 0.25}']
            if tag in LEADERS_1980:
                name, ide = LEADERS_1980[tag]
                L += ['create_country_leader = {', f'\tname = "{name}"', '\tdesc = ""',
                      f'\tideology = {ide}', '\ttraits = { }', '}']
            text = '\n'.join(L) + '\n'
        write(os.path.join(out, 'history', 'countries', f'{tag} - BC.txt'), text)
        if tag in owned:
            write_oob(out, tag, capitals.get(tag), states, owned[tag])
    return capitals, owned


def capital_province(state):
    if state['vps']:
        return max(state['vps'], key=lambda x: x[1])[0]
    return state['provinces'][0]


def write_oob(out, tag, cap, states, sts):
    if tag in balkan_content.OOB:
        text = balkan_content.OOB[tag]
    else:
        manpower = sum(s['manpower'] for s in sts)
        n = max(1, min(24, manpower // 3_000_000 + (6 if tag in MAJORS else 0)))
        prov = capital_province(states[cap])
        L = ['division_template = {', '\tname = "Infantry Division"', '\tregiments = {',
             '\t\tinfantry = { x = 0 y = 0 }', '\t\tinfantry = { x = 0 y = 1 }', '\t\tinfantry = { x = 0 y = 2 }',
             '\t\tinfantry = { x = 1 y = 0 }', '\t\tinfantry = { x = 1 y = 1 }', '\t\tinfantry = { x = 1 y = 2 }',
             '\t}', '\tsupport = {', '\t\tengineer = { x = 0 y = 0 }', '\t\tartillery = { x = 0 y = 1 }', '\t}', '}',
             'units = {']
        for i in range(n):
            L += ['\tdivision = {', f'\t\tname = "{i + 1}. Infantry Division"',
                  f'\t\tlocation = {prov}', '\t\tdivision_template = "Infantry Division"',
                  '\t\tstart_experience_factor = 0.3', '\t}']
        L += ['}', 'instant_effect = {',
              f'\tadd_equipment_to_stockpile = {{ type = infantry_equipment_1 amount = {400 * n} producer = {tag} }}',
              f'\tadd_equipment_to_stockpile = {{ type = artillery_equipment_1 amount = {50 * n} producer = {tag} }}',
              f'\tadd_equipment_to_stockpile = {{ type = support_equipment_1 amount = {40 * n} producer = {tag} }}', '}']
        text = '\n'.join(L) + '\n'
    write(os.path.join(out, 'history', 'units', f'{tag}_1980.txt'), text)


# --------------------------------------------------------------------------
# Flags
# --------------------------------------------------------------------------
def build_flags(md_repo, old_mod, out, tags_needed):
    from PIL import Image
    fl = os.path.join(out, 'gfx', 'flags')
    for d in ('', 'medium', 'small'):
        os.makedirs(os.path.join(fl, d), exist_ok=True)
    md_flags = os.path.join(md_repo, 'gfx', 'flags')

    def save_all(img, name):
        img = img.convert('RGBA')
        img.resize((82, 52), Image.LANCZOS).save(os.path.join(fl, name + '.tga'))
        img.resize((41, 26), Image.LANCZOS).save(os.path.join(fl, 'medium', name + '.tga'))
        img.resize((10, 7), Image.LANCZOS).save(os.path.join(fl, 'small', name + '.tga'))

    special = {'SOV': 'SOV_USSR', 'CZE': 'CZE_SLO_czechoslovakia'}
    missing = []
    for tag in sorted(tags_needed):
        if tag in balkan_content.BALKAN_TAGS:
            continue
        for ide in [''] + IDEOLOGIES:
            name = tag + ('_' + ide if ide else '')
            candidates = []
            if tag in special:
                candidates.append(special[tag])
            candidates += [name, f'{tag}_neutrality', f'{tag}_democratic', f'{tag}_communism', tag]
            src = next((os.path.join(md_flags, c + '.tga') for c in candidates
                        if os.path.exists(os.path.join(md_flags, c + '.tga'))), None)
            if src is None:
                missing.append(name)
                continue
            save_all(Image.open(src), name)
    # DDR flag (drawn): black-red-gold with a simplified golden emblem
    from PIL import ImageDraw
    img = Image.new('RGBA', (820, 520))
    d = ImageDraw.Draw(img)
    for i, c in enumerate([(0, 0, 0), (221, 0, 0), (255, 206, 0)]):
        d.rectangle([0, i * 173, 820, (i + 1) * 174], fill=c + (255,))
    d.ellipse([300, 150, 520, 370], fill=(255, 206, 0, 255), outline=(0, 0, 0, 255), width=6)
    d.rectangle([395, 190, 425, 330], fill=(0, 0, 0, 255))
    d.polygon([(340, 230), (480, 230), (470, 250), (350, 250)], fill=(0, 0, 0, 255))
    for ide in [''] + IDEOLOGIES:
        save_all(img, 'DDR' + ('_' + ide if ide else ''))
    # Balkan flags from the previous mod version (MAC -> FYR, SRP -> RSK)
    rename = {'MAC': 'FYR', 'SRP': 'RSK'}
    for sub in ('', 'medium', 'small'):
        for p in glob.glob(os.path.join(old_mod, 'Balkan_Collapse', 'gfx', 'flags', sub, '*.tga')):
            base = os.path.basename(p)
            tag = base[:3]
            if tag not in ('SER', 'CRO', 'SLV', 'BOS', 'MNT', 'KOS', 'MAC', 'SRP'):
                continue
            new = rename.get(tag, tag) + base[3:]
            shutil.copy2(p, os.path.join(fl, sub, new))
    # SFRY flag for communist Serbia, FRY flag for neutral Serbia (Millennium Dawn art)
    for name, srcname in (('SER_communism', 'SER_YUG_communism'), ('SER_neutrality', 'SER_FRY')):
        p = os.path.join(md_flags, srcname + '.tga')
        if os.path.exists(p):
            save_all(Image.open(p), name)
    return missing


# --------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--md-archive', required=True)
    ap.add_argument('--md-repo', required=True)
    ap.add_argument('--old-mod', required=True)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    out = os.path.join(a.out, 'Balkan_Collapse')
    if os.path.exists(out):
        shutil.rmtree(out)
    os.makedirs(out)
    states = convert_states(a.md_archive)
    for s in states.values():
        write_state(s, out)
    build_map(a.md_archive, out)
    tags = build_countries(a.md_repo, out, None)
    build_localisation(a.md_repo, out, tags)
    capitals, owned = build_history(a.md_archive, out, states, tags)
    missing = build_flags(a.md_repo, a.old_mod, out, set(owned) | set(balkan_content.BALKAN_TAGS))
    if missing:
        print('flags without Millennium art:', len(missing), missing[:20])
    balkan_content.build(out, a.old_mod, states, capitals)
    write(os.path.join(a.out, 'Balkan_Collapse.mod'), balkan_content.descriptor(path='mod/Balkan_Collapse'))
    print('owners in 1980:', len(owned))
    print('done ->', out)


if __name__ == '__main__':
    main()
