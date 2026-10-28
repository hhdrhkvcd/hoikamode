# -*- coding: utf-8 -*-
"""Balkan Collapse content: Yugoslav countries, focus trees, events, ideas, bookmark."""
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import md_arsenal  # noqa: E402
import world_2026  # noqa: E402

BALKAN_TAGS = ['SER', 'CRO', 'SLV', 'BOS', 'RSK', 'MNT', 'KOS', 'FYR']
# tags of the countries that existed only during the wars (1991-1995)
WAR_TAGS = ['RKS', 'HZG']
HISTORIC_TAGS = BALKAN_TAGS + WAR_TAGS
CAPITALS = {'SER': 131, 'CRO': 126, 'SLV': 124, 'BOS': 128, 'RSK': 1054, 'MNT': 134, 'KOS': 133, 'FYR': 136,
            'RKS': 127, 'HZG': 1052}
COUNTRY_COLORS = {'SER': '160 35 40', 'CRO': '60 100 190', 'SLV': '80 160 90', 'BOS': '230 200 60',
                  'RSK': '130 60 75', 'MNT': '200 120 50', 'KOS': '70 140 210', 'FYR': '225 95 40',
                  'RKS': '95 55 130', 'HZG': '205 95 45',
                  'SRF': '150 40 45', 'NUG': '35 115 60'}
YUGO_STATE_IDS = [124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 998, 1051, 1052, 1053, 1054]

# --------------------------------------------------------------------------
# Leaders (2026) and history
# --------------------------------------------------------------------------
# The special projects that the modern armies need (Millennium Dawn)
MD_PROJECTS = ['sp_armoured_vehicle_project', 'sp_awacs_project', 'sp_aircraft_project', 'sp_space_program',
               'sp_microchip_production', 'sp_helicopter_project', 'sp_missile_project', 'sp_naval_vessel_project']


def md_technology(slots=3, blocks=None):
    """The modern starting technology of the armies (the Millennium Dawn tree)."""
    L = [f'set_research_slots = {slots}']
    L += [f'complete_special_project = sp:{p}' for p in MD_PROJECTS]
    for cond, names in (blocks if blocks is not None else md_arsenal.TECH_BLOCKS):
        body = '\n'.join(f'\t{n} = 1' for n in names)
        if cond:
            L.append(f'if = {{\n\tlimit = {{ {cond} }}\n\tset_technology = {{\n{body}\n\t}}\n}}')
        else:
            L.append(f'set_technology = {{\n{body}\n}}')
    return '\n'.join(L) + '\n'


def md_variants():
    """Equipment variants of the Yugoslav army: M-84, BOV, Zastava, Orao, Kotor, ..."""
    L = []
    for cond, text in md_arsenal.EQUIPMENT_VARIANTS:
        if cond:
            L.append(f'if = {{\n\tlimit = {{ {cond} }}\n{text}\n}}')
        else:
            L.append(text)
    return '\n'.join(L) + '\n'


TECH = md_technology()


def leader(name, ideology, desc, picture=None):
    pic = f'\n\tpicture = "{picture}"' if picture else ''
    return (f'create_country_leader = {{\n\tname = "{name}"{pic}\n\tdesc = "{desc}"\n'
            f'\tideology = {ideology}\n\ttraits = {{ }}\n}}\n')


def politics(ruling, pops, elections='yes'):
    p = ' '.join(f'{k} = {v}' for k, v in pops.items())
    return (f'set_politics = {{\n\truling_party = {ruling}\n\tlast_election = "1980.1.1"\n\telection_frequency = 48\n'
            f'\telections_allowed = {elections}\n}}\nset_popularities = {{ {p} }}\n')


HISTORY = {
    'SER': ('oob = "SER_1980"\n'
            'if = { limit = { has_dlc = "By Blood Alone" } set_air_oob = "SER_1980_air" }\n'
            'if = { limit = { has_dlc = "Man the Guns" } set_naval_oob = "SER_1980_naval" }\n'
            + TECH + md_variants() + politics('communism', dict(democratic=6, fascism=2, communism=80, neutrality=12), 'no') +
           'set_stability = 0.7\nset_war_support = 0.3\nset_country_flag = SER_tito_alive\n'
           'add_ideas = { BC_tito_cult BC_jna BC_debt_crisis }\n' +
           leader('Josip Broz Tito', 'marxism', 'SER_TITO_DESC', 'joska_broz.dds')),
    'CRO': TECH + politics('democratic', dict(democratic=60, fascism=8, communism=10, neutrality=22)) +
           'set_stability = 0.55\nset_war_support = 0.5\n' + leader('Andrej Plenković', 'conservatism', 'CRO_LEADER_DESC', 'CRO_Andrej_Plenkovic.dds'),
    'SLV': TECH + politics('democratic', dict(democratic=68, fascism=4, communism=8, neutrality=20)) +
           'set_stability = 0.65\nset_war_support = 0.3\n' + leader('Janez Janša', 'conservatism', 'SLV_LEADER_DESC', 'janez_jansa.dds'),
    'BOS': TECH + politics('democratic', dict(democratic=55, fascism=5, communism=10, neutrality=30)) +
           'set_stability = 0.4\nset_war_support = 0.5\n' + leader('Borjana Krišto', 'conservatism', 'BOS_LEADER_DESC'),
    'RSK': TECH + politics('neutrality', dict(democratic=25, fascism=10, communism=10, neutrality=55), 'yes') +
           'set_stability = 0.5\nset_war_support = 0.6\n' + leader('Milorad Dodik', 'oligarchism', 'RSK_LEADER_DESC'),
    'MNT': TECH + politics('democratic', dict(democratic=58, fascism=4, communism=8, neutrality=30)) +
           'set_stability = 0.6\nset_war_support = 0.2\n' + leader('Milojko Spajić', 'liberalism', 'MNT_LEADER_DESC'),
    'KOS': TECH + politics('democratic', dict(democratic=62, fascism=6, communism=4, neutrality=28)) +
           'set_stability = 0.45\nset_war_support = 0.45\n' + leader('Albin Kurti', 'socialism', 'KOS_LEADER_DESC', 'albin_kurti.dds'),
    'FYR': TECH + politics('democratic', dict(democratic=57, fascism=5, communism=8, neutrality=30)) +
           'set_stability = 0.55\nset_war_support = 0.25\n' + leader('Hristijan Mickoski', 'conservatism', 'FYR_LEADER_DESC'),
}

# Province with the main victory point of each Yugoslav state (used for unit placement)
STATE_VP = {124: 9627, 125: 9596, 126: 11581, 127: 3924, 128: 11899, 129: 11741, 130: 3617, 131: 11586, 132: 11887,
            133: 9890, 134: 9809, 135: 3882, 136: 11857, 998: 11787, 1051: 6614, 1052: 9894, 1053: 13934, 1054: 9588}


# The brigades of the modern Yugoslav People's Army (Millennium Dawn battalions)
MD_TEMPLATES = {
    'Motorised': ('Motorizovana brigada', [('Mot_Inf_Bat', 3), ('Mech_Inf_Bat', 1), ('Arty_Bat', 2)],
                  [('L_Engi_Comp', 1), ('SP_AA_Battery', 1)]),
    'Tank': ('Tenkovska brigada', [('armor_Bat', 2), ('Arm_Inf_Bat', 1), ('Mech_Inf_Bat', 2), ('SP_Arty_Bat', 2)],
             [('H_Engi_Comp', 1), ('SP_AA_Battery', 1)]),
    'Mechanised': ('Mehanizovana brigada', [('armor_Bat', 1), ('Mech_Inf_Bat', 3), ('SP_Arty_Bat', 2)],
                   [('H_Engi_Comp', 1), ('SP_AA_Battery', 1)]),
    'Infantry': ('Pesadijska brigada', [('L_Inf_Bat', 2), ('Militia_Bat', 1), ('Arty_Bat', 1)],
                 [('L_Engi_Comp', 1), ('Weapons_company', 1)]),
}

# The modern arsenal of every army: rifles, artillery, optics, vehicles
MD_STOCKPILE = [('infantry_weapons_4', 500), ('artillery_equipment', 60), ('util_vehicle_2', 40),
                ('Anti_tank_2', 20), ('AA_Equipment', 10)]


def md_division_templates():
    """The division templates of the modern armies."""
    L = []
    templates = list(MD_TEMPLATES.items())
    # the names that the vanilla AI plans refer to
    templates += [('Infantry', ('Infantry Division', MD_TEMPLATES['Infantry'][1], MD_TEMPLATES['Infantry'][2])),
                  ('Armour', ('Armour Division', MD_TEMPLATES['Tank'][1], MD_TEMPLATES['Tank'][2]))]
    for key, (name, regs, sup) in templates:
        L.append('division_template = {')
        L.append(f'\tname = "{name}"')
        L.append('\tregiments = {')
        i = 0
        for bat, n in regs:
            for _ in range(n):
                L.append(f'\t\t{bat} = {{ x = {i // 3} y = {i % 3} }}')
                i += 1
        L.append('\t}')
        L.append('\tsupport = {')
        j = 0
        for comp, n in sup:
            for _ in range(n):
                L.append(f'\t\t{comp} = {{ x = {j // 3} y = {j % 3} }}')
                j += 1
        L.append('\t}')
        L.append('}')
    return '\n'.join(L)


def oob(tag, placements, mix=('Motorised', 'Tank', 'Mechanised'), equipment_mult=1, air=None):
    """Order of battle of a modern army (the style of Millennium Dawn)."""
    L = [md_division_templates(), 'units = {']
    for i, prov in enumerate(placements):
        name = MD_TEMPLATES[mix[i % len(mix)]][0]
        L += ['\tdivision = {', f'\t\tname = "{i + 1}. {name}"', f'\t\tlocation = {prov}',
              f'\t\tdivision_template = "{name}"', '\t\tstart_experience_factor = 0.3', '\t}']
    n = max(1, len(placements) * equipment_mult)
    L += ['}', 'instant_effect = {']
    for eq, amount in MD_STOCKPILE:
        L.append(f'\tadd_equipment_to_stockpile = {{ type = {eq} amount = {amount * n} producer = {tag} }}')
    L.append('}')
    if air:
        prov, planes = air
        L += ['air_wings = {', f'\t{prov} = {{']
        for i, (eq, variant, amount) in enumerate(planes):
            L.append(f'\t\t{eq} = {{ owner = "{tag}" creator = "{tag}" amount = {amount} }}')
            L.append(f'\t\tname = "{i + 1}. Air Regiment"')
            L.append('\t\tstart_experience_factor = 0.3')
        L += ['\t}', '}']
    return '\n'.join(L) + '\n'




def air_oob(tag, wings):
    """The air force: the wings of the modern air force (the "By Blood Alone" aircraft)."""
    L = ['instant_effect = {']
    for prov, name, planes in wings:
        for eq, variant, amount in planes:
            L.append(f'\tadd_equipment_to_stockpile = {{ type = {eq} variant_name = "{variant}" '
                     f'amount = {amount} producer = {tag} }}')
    L += ['}', 'air_wings = {']
    for prov, name, planes in wings:
        L.append(f'\t{prov} = {{')
        for eq, variant, amount in planes:
            L.append(f'\t\t{eq} = {{ owner = "{tag}" creator = "{tag}" amount = {amount} '
                     f'version_name = "{variant}" }}')
            L.append(f'\t\tname = "{name}"')
            L.append('\t\tstart_experience_factor = 0.4')
        L.append('\t}')
    L += ['}']
    return '\n'.join(L) + '\n'


def naval_oob(tag, fleet, base, ships):
    """The navy: the fleet of the modern navy (the "Man the Guns" ships)."""
    L = ['units = {', '\tfleet = {', f'\t\tname = "{fleet}"', f'\t\tnaval_base = {base}',
         '\t\ttask_force = {', f'\t\t\tname = "{fleet}"', f'\t\t\tlocation = {base}']
    for name, definition, hull, variant in ships:
        L.append(f'\t\t\tship = {{ name = "{name}" definition = {definition} start_experience_factor = 0.25 '
                 f'equipment = {{ {hull} = {{ amount = 1 owner = {tag} version_name = "{variant}" }} }} }}')
    L += ['\t\t}', '\t}', '}']
    return '\n'.join(L) + '\n'


OOB = {
    'SER': oob('SER', [STATE_VP[s] for s in YUGO_STATE_IDS] + [11586, 11586, 3617, 11581, 11899, 11857],
               equipment_mult=2),
}

# The Yugoslav Air Force: the J-22 Orao, the G-2 Galeb and the G-4 Super Galeb
AIR_OOB = {
    'SER_1980_air': air_oob('SER', [
        (11586, '204. Lovacka avijacijska eskadrila',
         [('small_plane_strike_airframe_1', 'J-22 Orao', 24)]),
        (11887, '252. Lovacko-bombarderska avijacijska eskadrila',
         [('small_plane_strike_airframe_1', 'G-2 Galeb', 12)]),
        (11581, '306. Mornaricka avijacijska eskadrila',
         [('small_plane_strike_airframe_1', 'J-21 Jastreb', 12)]),
        (3617, '204. Lovacka avijacijska eskadrila Kurjaci sa Usca',
         [('small_plane_strike_airframe_2', 'G-4 Super Galeb', 8)]),
    ]),
}

# The Yugoslav Navy: the Kotor class corvettes and the Heroj class submarines
NAVAL_OOB = {
    'SER_1980_naval': naval_oob('SER', 'Jugoslavenska ratna mornarica', 11581, [
        ('Beograd', 'corvette', 'corvette_hull_2', 'Kotor Class'),
        ('Pula', 'corvette', 'corvette_hull_2', 'Kotor Class'),
        ('Heroj', 'attack_submarine', 'attack_submarine_hull_1', 'Heroj Class'),
    ]),
}
EXTRA_OOB = {
    'CRO_1991': oob('CRO', [11581, 11581, 3924, 3924, 11581], ('Motorised', 'Infantry')),
    'SLV_1991': oob('SLV', [9627, 9627, 9596], ('Infantry', 'Motorised')),
    'FYR_1991': oob('FYR', [11857, 3882], ('Infantry', 'Motorised')),
    'RSK_1992': oob('RSK', [9588, 9588, 11741, 13934], ('Motorised', 'Tank')),
    'BOS_1992': oob('BOS', [11899, 11899, 6614, 9894], ('Infantry', 'Motorised')),
    'MNT_2006': oob('MNT', [9809], ('Infantry',)),
    'KOS_2008': oob('KOS', [9890], ('Infantry',)),
    'RKS_1991': oob('RKS', [3924, 3924, 11564], ('Infantry', 'Motorised')),
    'HZG_1992': oob('HZG', [9894, 9894], ('Infantry',)),
}

# --------------------------------------------------------------------------
# Focus helpers
# --------------------------------------------------------------------------
def civ(n=1):
    return ('random_owned_controlled_state = { limit = { is_core_of = ROOT } '
            f'add_extra_state_shared_building_slots = {n} add_building_construction = {{ type = industrial_complex level = {n} instant_build = yes }} }}')


def mil(n=1):
    return ('random_owned_controlled_state = { limit = { is_core_of = ROOT } '
            f'add_extra_state_shared_building_slots = {n} add_building_construction = {{ type = arms_factory level = {n} instant_build = yes }} }}')


def dock(n=1):
    return ('random_owned_controlled_state = { limit = { is_core_of = ROOT is_coastal = yes } '
            f'add_extra_state_shared_building_slots = {n} add_building_construction = {{ type = dockyard level = {n} instant_build = yes }} }}')


def infra():
    return ('every_owned_state = { limit = { is_core_of = ROOT } '
            'add_building_construction = { type = infrastructure level = 1 instant_build = yes } }')


def refinery():
    return ('random_owned_controlled_state = { limit = { is_core_of = ROOT } '
            'add_extra_state_shared_building_slots = 1 add_building_construction = { type = synthetic_refinery level = 1 instant_build = yes } }')


def airbase():
    return ('capital_scope = { add_building_construction = { type = air_base level = 2 instant_build = yes } }')


# The research categories of the vanilla game are replaced by the Millennium Dawn ones
TECH_BONUS = {
    'land_doctrine': ('land_doctrine', 'combined_arms'),
    'infantry_weapons': ('infantry', 'infantry_weapons_1'),
    'electronics': ('engineering', 'computing_1'),
    'industry': ('industry', 'construction1'),
    'artillery': ('artillery', 'tech_arty_0'),
    'air_doctrine': ('fixed_wing', 'early_fighter'),
    'support_weapons': ('infantry', 'support_weapons'),
    'armor': ('armor', 'Early_APC'),
    'naval': ('naval', 'corvette_hull_1'),
}


def bonus(cat, name):
    category, tech = TECH_BONUS.get(cat, (cat, cat))
    return f'add_tech_bonus = {{ name = {tech} bonus = 0.5 uses = 1 category = {category} }}'


def wargoal(tag):
    return f'if = {{ limit = {{ country_exists = {tag} NOT = {{ tag = {tag} }} }} create_wargoal = {{ type = annex_everything target = {tag} }} }}'


def claims(ids):
    return ' '.join(f'add_state_claim = {i}' for i in ids)


def union_offer(tag, event):
    return f'if = {{ limit = {{ country_exists = {tag} NOT = {{ is_in_faction_with = {tag} }} }} {tag} = {{ country_event = {{ id = {event} days = 1 }} }} }}'


def unify_offer(tag):
    return f'if = {{ limit = {{ country_exists = {tag} is_in_faction_with = {tag} }} {tag} = {{ country_event = {{ id = bc_union.2 days = 1 }} }} }}'


OTHERS = ['CRO', 'SLV', 'BOS', 'RSK', 'MNT', 'KOS', 'FYR']


class Tree:
    def __init__(self, tag, tree_id):
        self.tag, self.id, self.focuses = tag, tree_id, []

    def f(self, fid, icon, x, y, ru, ru_desc, en, pre=(), mx=(), cost=7, avail=None, reward='', bypass=None, ai=None):
        self.focuses.append(dict(id=fid, icon=icon, x=x, y=y, ru=ru, ru_desc=ru_desc, en=en, pre=pre, mx=mx,
                                 cost=cost, avail=avail, reward=reward, bypass=bypass, ai=ai))

    def render(self):
        L = ['focus_tree = {', f'\tid = {self.id}', '\tcountry = {', '\t\tfactor = 0',
             f'\t\tmodifier = {{ add = 20 tag = {self.tag} original_tag = {self.tag} }}', '\t}', '\tdefault = no',
             '\tcontinuous_focus_position = { x = 50 y = 1400 }']
        for f in self.focuses:
            L += ['\tfocus = {', f'\t\tid = {f["id"]}', f'\t\ticon = {f["icon"]}', f'\t\tx = {f["x"]}', f'\t\ty = {f["y"]}',
                  f'\t\tcost = {f["cost"]}']
            for group in f['pre']:
                group = [group] if isinstance(group, str) else group
                L.append('\t\tprerequisite = { ' + ' '.join(f'focus = {g}' for g in group) + ' }')
            if f['mx']:
                L.append('\t\tmutually_exclusive = { ' + ' '.join(f'focus = {g}' for g in f['mx']) + ' }')
            if f['avail']:
                L.append(f'\t\tavailable = {{ {f["avail"]} }}')
            if f['bypass']:
                L.append(f'\t\tbypass = {{ {f["bypass"]} }}')
            L.append('\t\tsearch_filters = { FOCUS_FILTER_POLITICAL }')
            L.append(f'\t\tai_will_do = {{ factor = {f["ai"] or 1} }}')
            L.append(f'\t\tcompletion_reward = {{ {f["reward"]} }}')
            L.append('\t}')
        L.append('}')
        return '\n'.join(L) + '\n'


# --------------------------------------------------------------------------
# SERBIA / YUGOSLAVIA
# --------------------------------------------------------------------------
def serbia_tree():
    t = Tree('SER', 'SER_1980_tree')
    F = t.f
    after_breakup = 'has_country_flag = SER_first_breakup_wave'
    F('SER_tito_legacy', 'GFX_goal_generic_national_unity', 11, 0, 'Наследие Тито',
      'Иосип Броз Тито умер 4 мая 1980 года. Федерация держится на его авторитете, и теперь страна должна найти новый путь.',
      "Tito's Legacy", avail='has_country_flag = SER_tito_dead', reward='add_political_power = 100 add_stability = 0.05')
    # ---------------- politics
    F('SER_collective_presidency', 'GFX_goal_generic_political_pressure', 6, 1, 'Коллективное президентство',
      'Президиум СФРЮ с ротацией председателя каждый год. Власть распределяется между республиками.',
      'Collective Presidency', pre=['SER_tito_legacy'], reward='add_political_power = 75 add_stability = 0.03')
    F('SER_1974_constitution', 'GFX_focus_generic_court', 4, 2, 'Конституция 1974 года',
      'Конституция 1974 года дала республикам и автономным краям огромные права. Пересмотреть её или сохранить?',
      'The 1974 Constitution', pre=['SER_collective_presidency'], reward='add_political_power = 50 add_stability = 0.02')
    F('SER_party_unity', 'GFX_focus_generic_soviet_politics', 8, 2, 'Единство СКЮ',
      'Союз коммунистов Югославии раскалывается по республиканским линиям. Нужно удержать партию вместе.',
      'Unity of the League of Communists', pre=['SER_collective_presidency'], reward='add_political_power = 60 add_popularity = { ideology = communism popularity = 0.05 }')
    F('SER_kosovo_1981', 'GFX_goal_generic_fortify_city', 2, 3, 'Протесты в Косово 1981',
      'Весной 1981 года студенты Приштины вышли на улицы. Белград отвечает введением чрезвычайного положения.',
      'The 1981 Kosovo Protests', pre=['SER_1974_constitution'], reward='add_war_support = 0.03 add_stability = -0.02 army_experience = 10')
    F('SER_memorandum', 'GFX_goal_generic_propaganda', 4, 3, 'Меморандум САНУ',
      'Меморандум Сербской академии наук 1986 года стал манифестом сербского национального движения.',
      'The SANU Memorandum', pre=['SER_1974_constitution'], reward='add_war_support = 0.05 add_political_power = 50')
    F('SER_brotherhood', 'GFX_focus_generic_balkan_diplomacy', 8, 3, 'Братство и единство',
      'Главный лозунг Тито. Пока его повторяют все республики, Югославия жива.',
      'Brotherhood and Unity', pre=['SER_party_unity'], reward='add_stability = 0.05 remove_ideas = BC_ethnic_tensions')
    F('SER_gazimestan', 'GFX_goal_generic_major_alliance', 4, 4, 'Речь на Газиместане',
      '28 июня 1989 года, шестисотлетие Косовской битвы. Сотни тысяч людей на поле у Приштины.',
      'The Gazimestan Speech', pre=['SER_memorandum', 'SER_kosovo_1981'], reward='add_war_support = 0.05 add_political_power = 75')
    F('SER_federal_dialogue', 'GFX_goal_generic_improve_relations', 8, 4, 'Федеральный диалог',
      'Последняя попытка договориться: встречи лидеров шести республик в 1991 году.',
      'The Federal Dialogue', pre=['SER_brotherhood'], reward='add_political_power = 75 add_stability = 0.03')
    F('SER_multiparty', 'GFX_focus_generic_universal_suffrage', 6, 4, 'Многопартийные выборы 1990',
      'Монополия СКЮ закончилась. В республиках проходят первые свободные выборы.',
      'The 1990 Multi-party Elections', pre=['SER_1974_constitution', 'SER_party_unity'],
      reward='add_popularity = { ideology = democratic popularity = 0.08 } add_political_power = 50')
    # path choice (after the break-up has begun)
    F('SER_path_force', 'GFX_goal_generic_major_war', 3, 5, 'Путь силы',
      'Республики ушли сами — значит, вернём их силой. ЮНА ещё остаётся одной из крупнейших армий Европы.',
      'The Path of Force', pre=['SER_gazimestan'], mx=['SER_path_federation', 'SER_path_europe'], avail=after_breakup,
      reward='add_war_support = 0.1 army_experience = 25 add_ideas = BC_war_footing', ai=3)
    F('SER_path_federation', 'GFX_focus_generic_balkans_focus', 6, 5, 'Новая федерация',
      'Югославия должна возродиться как добровольный союз равных народов.',
      'A New Federation', pre=['SER_multiparty'], mx=['SER_path_force', 'SER_path_europe'], avail=after_breakup,
      reward='add_political_power = 100 add_stability = 0.05', ai=2)
    F('SER_path_europe', 'GFX_goal_support_democracy', 9, 5, 'Европейская Сербия',
      'Сначала — Европа. Объединиться с соседями можно и внутри общего европейского дома.',
      'European Serbia', pre=['SER_federal_dialogue'], mx=['SER_path_force', 'SER_path_federation'], avail=after_breakup,
      reward='set_politics = { ruling_party = democratic elections_allowed = yes } add_popularity = { ideology = democratic popularity = 0.15 } add_stability = 0.05', ai=1)
    # force branch
    F('SER_jna_mobilization', 'GFX_goal_generic_allies_build_infantry', 2, 6, 'Мобилизация ЮНА',
      'Призыв резервистов и переброска бригад к границам бывших республик.', 'Mobilise the JNA',
      pre=['SER_path_force'], reward='add_manpower = 60000 army_experience = 20 add_war_support = 0.05')
    F('SER_claim_croatia', 'GFX_focus_generic_annex_country', 1, 7, 'Вернуть Хорватию',
      'Славония и Далмация — часть общей страны. Готовим военную операцию.', 'Reclaim Croatia',
      pre=['SER_jna_mobilization'], reward=claims([126, 127]) + ' ' + wargoal('CRO'))
    F('SER_claim_bosnia', 'GFX_focus_YUG_divide_bosnia', 3, 7, 'Вернуть Боснию',
      'Босния и Герцеговина — сердце Югославии. Без неё союз невозможен.', 'Reclaim Bosnia',
      pre=['SER_jna_mobilization'], reward=claims([128, 129, 1051, 1052, 1053, 1054]) + ' ' + wargoal('BOS') + ' ' + wargoal('RSK'))
    F('SER_claim_slovenia', 'GFX_focus_generic_annex_country_2', 1, 8, 'Вернуть Словению',
      'Десятидневная война была лишь началом.', 'Reclaim Slovenia',
      pre=['SER_claim_croatia'], reward=claims([124, 125]) + ' ' + wargoal('SLV'))
    F('SER_claim_south', 'GFX_goal_generic_demand_territory', 3, 8, 'Юг федерации',
      'Черногория, Косово и Македония должны вернуться под власть Белграда.', 'The Southern Republics',
      pre=['SER_claim_bosnia'], reward=claims([133, 134, 135, 136]) + ' ' + wargoal('MNT') + ' ' + wargoal('KOS') + ' ' + wargoal('FYR'))
    F('SER_force_victory', 'GFX_goal_generic_occupy_states_ongoing_war', 2, 9, 'Югославия железом',
      'Федерация восстановлена силой оружия. Теперь её нужно удержать.', 'Yugoslavia by Iron',
      pre=['SER_claim_slovenia', 'SER_claim_south'], reward='add_war_support = 0.05 army_experience = 30 add_political_power = 100')
    # federation branch
    F('SER_balkan_summit', 'GFX_focus_generic_balkan_diplomacy', 6, 6, 'Балканский саммит',
      'Белград приглашает все бывшие республики в «Югославское содружество».', 'The Balkan Summit',
      pre=['SER_path_federation'],
      reward='if = { limit = { is_in_faction = no } create_faction = "Югославское содружество" } ' + ' '.join(union_offer(x, 'bc_union.1') for x in OTHERS))
    F('SER_common_market', 'GFX_goal_generic_positive_trade_relations', 5, 7, 'Общий рынок',
      'Единая таможня и общий динар — первый шаг к единому государству.', 'A Common Market',
      pre=['SER_balkan_summit'], reward=civ(2) + ' add_political_power = 50')
    F('SER_federal_army', 'GFX_goal_generic_military_sphere', 7, 7, 'Объединённое командование',
      'Армии членов содружества переходят под общее командование.', 'Joint Command',
      pre=['SER_balkan_summit'], reward='army_experience = 25 ' + bonus('land_doctrine', 'SER_federal_army'))
    F('SER_union_treaty', 'GFX_focus_generic_treaty', 6, 8, 'Новый союзный договор',
      'Каждой республике предлагается войти в обновлённую федерацию.', 'The New Union Treaty',
      pre=['SER_common_market', 'SER_federal_army'], reward=' '.join(unify_offer(x) for x in OTHERS) + ' add_stability = 0.05')
    F('SER_federal_parliament', 'GFX_goal_generic_national_unity', 6, 9, 'Союзная скупщина',
      'Новая Скупщина собирается в Белграде с депутатами от всех народов.', 'The Federal Assembly',
      pre=['SER_union_treaty'], reward='add_political_power = 120 add_stability = 0.08')
    # europe branch
    F('SER_eu_candidate', 'GFX_goal_generic_trade', 9, 6, 'Кандидат в ЕС',
      'Переговоры о вступлении в Европейский союз открывают дорогу инвестициям.', 'EU Candidate',
      pre=['SER_path_europe'], reward='add_ideas = BC_eu_candidate ' + civ(2) + ' remove_ideas = BC_sanctions')
    F('SER_reconciliation', 'GFX_goal_generic_improve_relations', 10, 7, 'Региональное примирение',
      'Признать прошлое и протянуть руку соседям.', 'Regional Reconciliation',
      pre=['SER_eu_candidate'], reward='add_stability = 0.08 remove_ideas = BC_ethnic_tensions add_political_power = 50')
    F('SER_open_balkan', 'GFX_focus_generic_little_entente', 9, 8, 'Открытые Балканы',
      'Свободное передвижение людей и товаров. Соседям предлагается вступить в союз.', 'Open Balkan',
      pre=['SER_eu_candidate'],
      reward='if = { limit = { is_in_faction = no } create_faction = "Открытые Балканы" } ' + ' '.join(union_offer(x, 'bc_union.1') for x in OTHERS))
    F('SER_confederation', 'GFX_focus_generic_diplomatic_treaty', 9, 9, 'Демократическая конфедерация',
      'Добровольное объединение демократических республик Западных Балкан.', 'A Democratic Confederation',
      pre=['SER_open_balkan', 'SER_reconciliation'], reward=' '.join(unify_offer(x) for x in OTHERS) + ' add_stability = 0.05')
    # final
    F('SER_restore_yugoslavia', 'GFX_focus_generic_self_management', 6, 10, 'Восстановить Югославию',
      'Все земли южных славян снова под одним флагом. Югославия возрождена!', 'Restore Yugoslavia',
      pre=[['SER_force_victory', 'SER_federal_parliament', 'SER_confederation']],
      avail=' '.join(f'owns_state = {s}' for s in YUGO_STATE_IDS), cost=10,
      reward='set_cosmetic_tag = SER_YUGOSLAVIA set_country_flag = SER_yugoslavia_restored ' + ' '.join(f'{s} = {{ add_core_of = ROOT }}' for s in YUGO_STATE_IDS) +
             ' add_stability = 0.15 add_political_power = 200 remove_ideas = BC_ethnic_tensions add_ideas = BC_yugoslav_rebirth')
    F('SER_balkan_hegemon', 'GFX_goal_generic_major_alliance', 6, 11, 'Балканский гегемон',
      'Возрождённая Югославия снова голос Балкан в мире.', 'Balkan Hegemon',
      pre=['SER_restore_yugoslavia'], reward='add_political_power = 150 ' + claims([137, 138]) + ' add_research_slot = 1')
    # ---------------- economy
    F('SER_debt_crisis', 'GFX_goal_generic_consumer_goods', 14, 1, 'Долговой кризис',
      'Внешний долг Югославии превысил 20 миллиардов долларов. Нужны жёсткие меры.', 'The Debt Crisis',
      pre=['SER_tito_legacy'], reward='add_political_power = 50')
    F('SER_imf_loans', 'GFX_focus_generic_american_investments', 13, 2, 'Кредиты МВФ',
      'Деньги Запада дадут передышку, но потребуют реформ.', 'IMF Loans',
      pre=['SER_debt_crisis'], reward=civ(1) + ' add_stability = -0.02')
    F('SER_self_management', 'GFX_focus_generic_self_management', 15, 2, 'Рабочее самоуправление',
      'Югославская модель социализма: заводы принадлежат трудовым коллективам.', 'Workers\' Self-management',
      pre=['SER_debt_crisis'], reward='add_stability = 0.04 ' + civ(1))
    F('SER_zastava', 'GFX_goal_generic_construct_civ_factory', 12, 3, 'Завод «Застава»',
      'Автозавод в Крагуеваце выпускает «Юго» — даже на экспорт в США.', 'The Zastava Works',
      pre=['SER_imf_loans'], reward=civ(2))
    F('SER_nis', 'GFX_goal_generic_oil_refinery', 14, 3, 'НИС: нефть Паннонии',
      'Нефтяная индустрия Сербии развивает месторождения Воеводины и НПЗ в Панчеве.', 'NIS: Pannonian Oil',
      pre=['SER_imf_loans', 'SER_self_management'], reward=refinery() + ' 130 = { add_resource = { type = oil amount = 8 } }')
    F('SER_djerdap', 'GFX_focus_generic_hydroelectric_energy', 16, 3, 'ГЭС «Джердап»',
      'Гидроэлектростанция на Дунае у Железных ворот — гордость югославской инженерии.', 'Đerdap Hydro Plant',
      pre=['SER_self_management'], reward=civ(1) + ' add_stability = 0.02')
    F('SER_markovic', 'GFX_goal_generic_production', 13, 4, 'Реформы Марковича',
      'Программа Анте Марковича 1989 года: конвертируемый динар и рыночные реформы.', "Marković's Reforms",
      pre=['SER_zastava', 'SER_nis'], reward='remove_ideas = BC_debt_crisis add_stability = 0.03 ' + civ(1))
    F('SER_new_dinar', 'GFX_focus_generic_reorient_production', 15, 4, 'Новый динар',
      'Гиперинфляция 1993 года научила: деньги должны быть крепкими.', 'The New Dinar',
      pre=['SER_nis', 'SER_djerdap'], reward='add_political_power = 75 add_stability = 0.05')
    F('SER_corridor_10', 'GFX_goal_generic_construct_infrastructure', 13, 5, 'Коридор X',
      'Автомагистраль и железная дорога Загреб — Белград — Ниш — Скопье.', 'Pan-European Corridor X',
      pre=['SER_markovic'], reward=infra())
    F('SER_mining', 'GFX_focus_generic_mining_industry', 15, 5, 'Медь Бора и уголь Колубары',
      'Горнодобывающая промышленность — основа тяжёлой индустрии.', 'Bor Copper and Kolubara Coal',
      pre=['SER_new_dinar'], reward='132 = { add_resource = { type = steel amount = 6 } } 131 = { add_resource = { type = aluminium amount = 4 } }')
    F('SER_industrial_base', 'GFX_goal_generic_construct_civilian', 14, 6, 'Промышленная база',
      'Новые заводы в Нише, Крагуеваце и Нови-Саде.', 'Industrial Base',
      pre=['SER_corridor_10', 'SER_mining'], reward=civ(2) + ' ' + bonus('industry', 'SER_industry'))
    F('SER_it_sector', 'GFX_focus_generic_university_1', 13, 7, 'IT-сектор Белграда и Нови-Сада',
      'Программисты Сербии работают на весь мир.', 'Belgrade & Novi Sad IT Sector',
      pre=['SER_industrial_base'], reward='add_research_slot = 1 ' + bonus('electronics', 'SER_it'))
    F('SER_foreign_investment', 'GFX_focus_generic_concessions', 15, 7, 'Иностранные инвестиции',
      'Китай, ЕС и Россия соревнуются за сербский рынок.', 'Foreign Investment',
      pre=['SER_industrial_base'], reward=civ(2) + ' ' + mil(1))
    F('SER_economic_miracle', 'GFX_focus_generic_industry_3', 14, 8, 'Балканский тигр',
      'Экономика растёт быстрее, чем у соседей.', 'Balkan Tiger',
      pre=['SER_it_sector', 'SER_foreign_investment'], reward=civ(3) + ' add_stability = 0.05')
    # ---------------- army
    F('SER_total_defense', 'GFX_goal_generic_army_doctrines', 20, 1, 'Всенародная оборона',
      'Доктрина 1969 года: каждый гражданин — солдат, каждая гора — крепость.', 'Total National Defence',
      pre=['SER_tito_legacy'], reward='army_experience = 20 ' + bonus('land_doctrine', 'SER_doctrine'))
    F('SER_territorial_defense', 'GFX_focus_generic_home_defense', 19, 2, 'Территориальная оборона',
      'Республиканские силы ТО — резерв, который может обернуться против Белграда.', 'Territorial Defence',
      pre=['SER_total_defense'], reward='add_manpower = 40000 add_war_support = 0.03')
    F('SER_air_force', 'GFX_goal_generic_build_airforce', 21, 2, 'ВВС Югославии',
      'МиГ-21 и отечественные «Ораo» и «Галеб» на аэродроме Батайница.', 'Yugoslav Air Force',
      pre=['SER_total_defense'], reward='air_experience = 25 ' + airbase())
    F('SER_zastava_arms', 'GFX_goal_generic_small_arms', 18, 3, '«Застава Оружие»',
      'Автоматы М70 из Крагуеваца — оружие половины Балкан.', 'Zastava Arms',
      pre=['SER_territorial_defense'], reward=mil(2) + ' ' + bonus('infantry_weapons', 'SER_m70'))
    F('SER_mountain_brigades', 'GFX_focus_SMB_mountain_guns', 20, 3, 'Горные бригады',
      'Динарское нагорье требует особой подготовки.', 'Mountain Brigades',
      pre=['SER_territorial_defense', 'SER_air_force'], reward='army_experience = 15 add_ideas = BC_mountain_warfare')
    F('SER_soko', 'GFX_focus_YUG_ikarus', 22, 3, 'Авиазавод «Соко»',
      'Мостарский завод «Соко» строил штурмовики J-22 «Орао».', 'SOKO Aircraft Works',
      pre=['SER_air_force'], reward=mil(1) + ' ' + bonus('air_doctrine', 'SER_soko'))
    F('SER_military_industry', 'GFX_goal_generic_construct_mil_factory', 19, 4, 'Военная промышленность',
      'Заводы в Чачке, Ужице и Велика-Плане.', 'Military Industry',
      pre=['SER_zastava_arms', 'SER_mountain_brigades'], reward=mil(2))
    F('SER_air_defense', 'GFX_focus_generic_air_defense', 21, 4, 'ПВО 1999 года',
      'Опыт бомбардировок НАТО: рассредоточение и маскировка.', 'Air Defence of 1999',
      pre=['SER_mountain_brigades', 'SER_soko'], reward='every_owned_state = { limit = { is_core_of = ROOT } add_building_construction = { type = anti_air_building level = 1 instant_build = yes } }')
    F('SER_red_berets', 'GFX_goal_generic_special_forces', 20, 5, '«Красные береты»',
      'Части специального назначения.', 'The Red Berets',
      pre=['SER_military_industry', 'SER_air_defense'], reward='army_experience = 25 ' + bonus('land_doctrine', 'SER_special'))
    F('SER_m84', 'GFX_goal_generic_army_tanks', 19, 6, 'Танк М-84',
      'Югославская версия Т-72 с отечественной электроникой.', 'The M-84 Tank',
      pre=['SER_red_berets'], reward=bonus('artillery', 'SER_m84') + ' ' + mil(1))
    F('SER_professional_army', 'GFX_focus_generic_military_academy', 21, 6, 'Профессиональная армия',
      'Отказ от призыва в пользу контрактных бригад.', 'Professional Army',
      pre=['SER_red_berets'], reward='army_experience = 30 add_ideas = BC_professional_army')
    F('SER_army_2026', 'GFX_goal_generic_position_armies', 20, 7, 'Армия Сербии 2026',
      'Современная армия: дроны, ПВО и мобильные бригады.', 'The Serbian Army 2026',
      pre=['SER_m84', 'SER_professional_army'], reward='army_experience = 40 add_war_support = 0.05 ' + mil(2))
    return t


# --------------------------------------------------------------------------
# Other republics: shared skeleton + national specifics
# --------------------------------------------------------------------------
def republic_tree(tag, spec):
    t = Tree(tag, f'{tag}_tree')
    F = t.f
    p = tag + '_'
    F(p + 'independence', spec['root_icon'], 6, 0, spec['root'][0], spec['root'][1], spec['root'][2],
      reward='add_political_power = 100 add_stability = 0.05 set_country_flag = BALKANS_INDEPENDENT')
    # politics
    F(p + 'government', 'GFX_focus_generic_improve_the_administration', 3, 1, spec['gov'][0], spec['gov'][1], spec['gov'][2],
      pre=[p + 'independence'], reward='add_political_power = 75 add_stability = 0.04')
    F(p + 'constitution', 'GFX_focus_generic_court', 2, 2, 'Новая конституция', 'Основной закон молодого государства.',
      'A New Constitution', pre=[p + 'government'], reward='add_stability = 0.05 add_political_power = 50')
    F(p + 'national_identity', 'GFX_goal_generic_propaganda', 4, 2, spec['identity'][0], spec['identity'][1], spec['identity'][2],
      pre=[p + 'government'], reward='add_war_support = 0.05 add_political_power = 50')
    F(p + 'west', 'GFX_goal_support_democracy', 1, 3, 'Курс на ЕС и НАТО',
      'Будущее — в Брюсселе. Союз с Белградом невозможен.', 'Towards the EU and NATO',
      pre=[p + 'constitution'], mx=[p + 'yugo'], reward='set_country_flag = BC_western add_ideas = BC_eu_candidate add_stability = 0.05',
      ai=spec.get('ai_west', 2))
    F(p + 'yugo', 'GFX_focus_generic_balkan_diplomacy', 3, 3, 'Югославское сотрудничество',
      'Общий язык, общая история, общий рынок. Может быть, снова вместе?', 'Yugoslav Cooperation',
      pre=[p + 'constitution', p + 'national_identity'], mx=[p + 'west'],
      reward='set_country_flag = BC_yugoslav_friendly add_political_power = 75', ai=spec.get('ai_yugo', 1))
    F(p + 'west_2', 'GFX_goal_generic_trade', 1, 4, spec['west2'][0], spec['west2'][1], spec['west2'][2],
      pre=[p + 'west'], reward=civ(2) + ' add_stability = 0.03')
    F(p + 'yugo_2', 'GFX_goal_generic_improve_relations', 3, 4, spec['yugo2'][0], spec['yugo2'][1], spec['yugo2'][2],
      pre=[p + 'yugo'], reward=spec['yugo2_reward'])
    F(p + 'national_goal', spec['goal_icon'], 2, 5, spec['goal'][0], spec['goal'][1], spec['goal'][2],
      pre=[[p + 'west_2', p + 'yugo_2']], reward=spec['goal_reward'], cost=10)
    # economy
    F(p + 'economy', 'GFX_goal_generic_production', 7, 1, spec['eco'][0], spec['eco'][1], spec['eco'][2],
      pre=[p + 'independence'], reward=civ(1) + ' add_political_power = 25')
    F(p + 'eco_1', spec['eco1_icon'], 6, 2, spec['eco1'][0], spec['eco1'][1], spec['eco1'][2],
      pre=[p + 'economy'], reward=spec['eco1_reward'])
    F(p + 'eco_2', spec['eco2_icon'], 8, 2, spec['eco2'][0], spec['eco2'][1], spec['eco2'][2],
      pre=[p + 'economy'], reward=spec['eco2_reward'])
    F(p + 'infrastructure', 'GFX_goal_generic_construct_infrastructure', 7, 3, 'Дороги и железные дороги',
      'Восстановление разрушенной войной инфраструктуры.', 'Roads and Railways',
      pre=[p + 'eco_1', p + 'eco_2'], reward=infra())
    F(p + 'growth', 'GFX_focus_generic_industry_2', 7, 4, 'Экономический рост', 'Инвестиции, экспорт и новые рабочие места.',
      'Economic Growth', pre=[p + 'infrastructure'], reward=civ(2) + ' ' + bonus('industry', p + 'growth'))
    F(p + 'research', 'GFX_focus_generic_university_1', 7, 5, 'Университеты и наука', 'Утечка мозгов должна прекратиться.',
      'Universities and Science', pre=[p + 'growth'], reward='add_research_slot = 1')
    # army
    F(p + 'army', spec['army_icon'], 11, 1, spec['army'][0], spec['army'][1], spec['army'][2],
      pre=[p + 'independence'], reward='army_experience = 20 add_manpower = 15000')
    F(p + 'army_1', 'GFX_goal_generic_small_arms', 10, 2, 'Вооружение армии', 'Закупки оружия и собственное производство.',
      'Arming the Army', pre=[p + 'army'], reward=mil(1) + ' ' + bonus('infantry_weapons', p + 'arms'))
    F(p + 'army_2', spec['army2_icon'], 12, 2, spec['army2'][0], spec['army2'][1], spec['army2'][2],
      pre=[p + 'army'], reward=spec['army2_reward'])
    F(p + 'army_3', 'GFX_goal_generic_army_doctrines', 11, 3, 'Военная доктрина', 'Уроки войн 1990-х.', 'Military Doctrine',
      pre=[p + 'army_1', p + 'army_2'], reward='army_experience = 25 ' + bonus('land_doctrine', p + 'doctrine'))
    F(p + 'army_4', 'GFX_goal_generic_construct_mil_factory', 11, 4, 'Оборонная промышленность', 'Своё оружие — своя независимость.',
      'Defence Industry', pre=[p + 'army_3'], reward=mil(2))
    F(p + 'army_goal', spec['army_goal_icon'], 11, 5, spec['army_goal'][0], spec['army_goal'][1], spec['army_goal'][2],
      pre=[p + 'army_4'], reward=spec['army_goal_reward'], cost=10)
    return t


def offer_to_serbia():
    return 'if = { limit = { country_exists = SER } SER = { country_event = { id = bc_union.3 days = 1 } } }'


REPUBLICS = {
    'CRO': dict(
        root_icon='GFX_focus_YUG_banovina_of_croatia',
        root=('Независимая Хорватия', '25 июня 1991 года Сабор провозгласил независимость Республики Хорватия.', 'Independent Croatia'),
        gov=('Правительство Пленковича', 'Андрей Пленкович возглавляет правительство Хорватии в 2026 году.', 'The Plenković Government'),
        identity=('Наследие Туджмана', 'Франьо Туджман — первый президент и символ независимости.', "Tuđman's Legacy"),
        west2=('Евро и Шенген', 'С 2023 года Хорватия в еврозоне и Шенгене.', 'The Euro and Schengen'),
        yugo2=('Диалог с Белградом', 'Хорватия готова обсуждать общее будущее с Сербией.', 'Dialogue with Belgrade'),
        yugo2_reward='add_political_power = 50 ' + offer_to_serbia(),
        goal=('Герцег-Босна', 'Хорваты Герцеговины должны жить в одном государстве с Хорватией.', 'Herzeg-Bosnia'),
        goal_icon='GFX_goal_generic_demand_territory', goal_reward=claims([1052]) + ' ' + wargoal('BOS') + ' add_war_support = 0.05',
        eco=('Адриатическая экономика', 'Порты, туризм и судостроение.', 'The Adriatic Economy'),
        eco1=('Туризм Далмации', 'Дубровник, Сплит, Хвар — миллионы туристов каждое лето.', 'Dalmatian Tourism'),
        eco1_icon='GFX_focus_generic_adriatic_sea_focus', eco1_reward=civ(2),
        eco2=('Верфи Риеки и Сплита', 'Судостроение — традиция Адриатики.', 'Rijeka and Split Shipyards'),
        eco2_icon='GFX_goal_generic_construct_naval_dockyard', eco2_reward=dock(2),
        army=('Хорватское войско', 'Из бригад Национальной гвардии рождается армия.', 'The Croatian Army'),
        army_icon='GFX_focus_generic_military_mission',
        army2=('Операция «Буря»', 'Август 1995 года: стремительное наступление на Книн.', 'Operation Storm'),
        army2_icon='GFX_goal_generic_major_war', army2_reward='army_experience = 30 add_war_support = 0.08',
        army_goal=('Флот Адриатики', 'Военно-морские силы Хорватии охраняют побережье.', 'The Adriatic Navy'),
        army_goal_icon='GFX_goal_generic_build_navy', army_goal_reward=dock(1) + ' navy_experience = 30',
        ai_west=4),
    'SLV': dict(
        root_icon='GFX_goal_generic_national_unity',
        root=('Независимая Словения', 'Плебисцит 23 декабря 1990 года: 88% за независимость.', 'Independent Slovenia'),
        gov=('Правительство Янши', 'Янез Янша возглавляет правительство Словении в 2026 году.', 'The Janša Government'),
        identity=('Десятидневная война', 'Победа 1991 года стала основой словенской государственности.', 'The Ten-Day War'),
        west2=('Еврозона', 'Словения — первая из бывших югославских республик в ЕС (2004) и еврозоне (2007).', 'The Eurozone'),
        yugo2=('Югоностальгия', 'Многие словенцы вспоминают общую страну с теплотой.', 'Yugonostalgia'),
        yugo2_reward='add_political_power = 50 ' + offer_to_serbia(),
        goal=('Альпийская Швейцария', 'Богатая, стабильная и нейтральная страна в Альпах.', 'Alpine Switzerland'),
        goal_icon='GFX_focus_generic_scandinavia_flags', goal_reward='add_stability = 0.1 ' + civ(2),
        eco=('Экспортная экономика', 'Gorenje, Krka, Revoz — словенские бренды по всей Европе.', 'An Export Economy'),
        eco1=('Порт Копер', 'Единственный порт Словении — ворота Центральной Европы к морю.', 'The Port of Koper'),
        eco1_icon='GFX_focus_generic_merchant_fleet', eco1_reward=civ(1) + ' ' + dock(1),
        eco2=('АЭС Кршко', 'Атомная станция, общая со Хорватией.', 'Krško Nuclear Plant'),
        eco2_icon='GFX_focus_generic_energy', eco2_reward=civ(2),
        army=('Словенская армия', 'Территориальная оборона становится армией.', 'The Slovenian Army'),
        army_icon='GFX_focus_generic_home_defense',
        army2=('Горные стрелки', 'Юлийские Альпы — естественная крепость.', 'Mountain Rifles'),
        army2_icon='GFX_focus_SMB_mountain_guns', army2_reward='add_ideas = BC_mountain_warfare army_experience = 15',
        army_goal=('Союзник НАТО', 'С 2004 года Словения — член НАТО.', 'NATO Ally'),
        army_goal_icon='GFX_goal_generic_alliance', army_goal_reward='army_experience = 25 add_war_support = 0.05 ' + bonus('land_doctrine', 'SLV_nato'),
        ai_west=5),
    'BOS': dict(
        root_icon='GFX_focus_YUG_safeguard_bosnia',
        root=('Независимая Босния', 'Референдум 29 февраля — 1 марта 1992 года. 3 марта — независимость.', 'Independent Bosnia'),
        gov=('Совет министров Кришто', 'Борьяна Кришто — председатель Совета министров БиГ в 2026 году.', 'The Krišto Council of Ministers'),
        identity=('Осада Сараево', '1425 дней осады. Город выстоял.', 'The Siege of Sarajevo'),
        west2=('Статус кандидата в ЕС', 'Босния и Герцеговина получила статус кандидата в 2022 году.', 'EU Candidate Status'),
        yugo2=('Мост в Мостаре', 'Восстановленный Старый мост — символ примирения.', 'The Mostar Bridge'),
        yugo2_reward='add_stability = 0.08 ' + offer_to_serbia(),
        goal=('Единая Босния', 'Конец разделённой страны: Республика Сербская должна вернуться.', 'A United Bosnia'),
        goal_icon='GFX_focus_generic_annex_country', goal_reward=claims([129, 1053, 1054]) + ' ' + wargoal('RSK'),
        eco=('Восстановление после Дейтона', 'Страна поднимается из руин войны.', 'Post-Dayton Reconstruction'),
        eco1=('Алюминий Мостара', 'Алюминиевый комбинат и бокситы Герцеговины.', 'Mostar Aluminium'),
        eco1_icon='GFX_focus_generic_aluminum', eco1_reward='128 = { add_resource = { type = aluminium amount = 6 } } ' + civ(1),
        eco2=('Энергетика Тузлы', 'Угольные электростанции снабжают половину Балкан.', 'Tuzla Power'),
        eco2_icon='GFX_focus_generic_energy', eco2_reward=civ(2),
        army=('Армия Республики БиГ', 'Из отрядов обороны Сараево рождается армия.', 'Army of the Republic of BiH'),
        army_icon='GFX_goal_generic_allies_build_infantry',
        army2=('Оборона Горажде', 'Анклавы держатся вопреки всему.', 'The Defence of Goražde'),
        army2_icon='GFX_goal_generic_defence', army2_reward='army_experience = 20 add_ideas = BC_mountain_warfare',
        army_goal=('Вооружённые силы БиГ', 'Единая армия трёх народов.', 'Armed Forces of BiH'),
        army_goal_icon='GFX_goal_generic_national_unity', army_goal_reward='army_experience = 30 add_stability = 0.05',
        ai_west=3),
    'RSK': dict(
        root_icon='GFX_focus_YUG_divide_bosnia',
        root=('Республика Сербская', '9 января 1992 года боснийские сербы провозгласили свою республику.', 'Republika Srpska'),
        gov=('Президент Каран', 'Синиша Каран — президент Республики Сербской в 2026 году.', 'President Karan'),
        identity=('Баня-Лука — столица', 'Город на Врбасе становится центром сербов Боснии.', 'Banja Luka the Capital'),
        west2=('Дейтонский статус', 'Энтитет внутри БиГ с широкой автономией.', 'The Dayton Status'),
        yugo2=('Единство с Сербией', 'Особые связи с Белградом: общие паспорта, общий язык, общая армия?', 'Unity with Serbia'),
        yugo2_reward='add_political_power = 50 ' + offer_to_serbia(),
        goal=('Референдум о независимости', 'Республика Сербская решает свою судьбу сама.', 'Independence Referendum'),
        goal_icon='GFX_focus_generic_universal_suffrage', goal_reward='add_stability = 0.08 add_war_support = 0.05 ' + claims([1053]),
        eco=('Экономика энтитета', 'Энергетика и сельское хозяйство.', 'The Entity Economy'),
        eco1=('ГЭС на Дрине', 'Гидроэнергетика Вишеграда и Зворника.', 'Drina Hydro Power'),
        eco1_icon='GFX_focus_generic_hydroelectric_energy', eco1_reward=civ(1),
        eco2=('Нефтепереработка Брода', 'НПЗ в Броде принадлежит российским инвесторам.', 'The Brod Refinery'),
        eco2_icon='GFX_goal_generic_oil_refinery', eco2_reward=refinery(),
        army=('Армия Республики Сербской', 'ВРС — наследник частей ЮНА в Боснии.', 'Army of Republika Srpska'),
        army_icon='GFX_goal_generic_allies_build_infantry',
        army2=('Дринский корпус', 'Оборона восточной Боснии.', 'The Drina Corps'),
        army2_icon='GFX_goal_generic_defence', army2_reward='army_experience = 25 add_manpower = 15000',
        army_goal=('Полиция Республики Сербской', 'Жандармерия как ядро будущей армии.', 'Republika Srpska Police'),
        army_goal_icon='GFX_focus_SWI_federal_police', army_goal_reward='army_experience = 20 add_stability = 0.05',
        ai_west=0, ai_yugo=5),
    'MNT': dict(
        root_icon='GFX_goal_generic_national_unity',
        root=('Независимая Черногория', '21 мая 2006 года — референдум, 3 июня — независимость.', 'Independent Montenegro'),
        gov=('Правительство Спаича', 'Милойко Спаич — премьер-министр Черногории в 2026 году.', 'The Spajić Government'),
        identity=('Наследие Петровичей', 'Черногорская государственность старше югославской.', 'The Petrović Legacy'),
        west2=('Лидер переговоров с ЕС', 'Черногория ближе всех к вступлению в ЕС.', 'EU Front-runner'),
        yugo2=('Сербско-черногорское единство', 'Половина страны считает себя сербами.', 'Serbo-Montenegrin Unity'),
        yugo2_reward='add_political_power = 50 ' + offer_to_serbia(),
        goal=('Жемчужина Адриатики', 'Бока Которская и Будва — курорты мирового уровня.', 'Pearl of the Adriatic'),
        goal_icon='GFX_focus_generic_adriatic_sea_focus', goal_reward=civ(2) + ' add_stability = 0.05',
        eco=('Экономика туризма', 'Море и горы — главный капитал страны.', 'The Tourism Economy'),
        eco1=('Порт Бар', 'Морские ворота и железная дорога Белград — Бар.', 'The Port of Bar'),
        eco1_icon='GFX_focus_generic_merchant_fleet', eco1_reward=dock(1) + ' ' + civ(1),
        eco2=('Алюминиевый комбинат', 'KAP в Подгорице.', 'The Podgorica Aluminium Plant'),
        eco2_icon='GFX_focus_generic_aluminum', eco2_reward='134 = { add_resource = { type = aluminium amount = 5 } }',
        army=('Армия Черногории', 'Небольшая, но горная армия.', 'The Montenegrin Army'),
        army_icon='GFX_focus_generic_military_mission',
        army2=('Горная война', 'Каждое ущелье — крепость.', 'Mountain Warfare'),
        army2_icon='GFX_focus_GRE_a_land_of_mountains', army2_reward='add_ideas = BC_mountain_warfare',
        army_goal=('Член НАТО', 'С 2017 года Черногория в НАТО.', 'NATO Member'),
        army_goal_icon='GFX_goal_generic_alliance', army_goal_reward='army_experience = 20 add_war_support = 0.05',
        ai_west=3, ai_yugo=2),
    'KOS': dict(
        root_icon='GFX_goal_generic_national_unity',
        root=('Республика Косово', '17 февраля 2008 года Скупщина Косово провозгласила независимость. Статус остаётся спорным.', 'Republic of Kosovo'),
        gov=('Правительство Курти', 'Альбин Курти — премьер-министр Косово в 2026 году.', 'The Kurti Government'),
        identity=('Наследие Ругова', 'Ибрагим Ругова и мирное сопротивление 1990-х.', "Rugova's Legacy"),
        west2=('Международное признание', 'Больше стран признают Косово.', 'International Recognition'),
        yugo2=('Брюссельское соглашение', 'Нормализация отношений с Сербией.', 'The Brussels Agreement'),
        yugo2_reward='add_stability = 0.08 add_political_power = 50',
        goal=('Мечта о Великой Албании', 'Объединение с Албанией — старая мечта многих косоваров.', 'Dream of Greater Albania'),
        goal_icon='GFX_focus_generic_befriend_albania',
        goal_reward='if = { limit = { country_exists = ALB } ALB = { country_event = { id = bc_union.4 days = 1 } } }',
        eco=('Экономика Косово', 'Денежные переводы диаспоры и евро без еврозоны.', 'The Kosovo Economy'),
        eco1=('Шахты Трепчи', 'Свинец, цинк и серебро.', 'The Trepča Mines'),
        eco1_icon='GFX_focus_generic_mining_industry', eco1_reward='133 = { add_resource = { type = steel amount = 4 } }',
        eco2=('Уголь и энергетика', 'Электростанции «Косово А» и «Косово Б».', 'Coal and Power'),
        eco2_icon='GFX_focus_generic_energy', eco2_reward=civ(2),
        army=('Силы безопасности Косово', 'ФСК превращаются в армию.', 'Kosovo Security Force'),
        army_icon='GFX_goal_generic_allies_build_infantry',
        army2=('Наследие АОК', 'Ветераны Армии освобождения Косово.', 'The KLA Legacy'),
        army2_icon='GFX_goal_generic_special_forces', army2_reward='army_experience = 20 add_war_support = 0.05',
        army_goal=('Армия Косово', 'Полноценные вооружённые силы к 2028 году.', 'The Kosovo Army'),
        army_goal_icon='GFX_goal_generic_position_armies', army_goal_reward='army_experience = 25 add_manpower = 10000',
        ai_west=4, ai_yugo=0),
    'FYR': dict(
        root_icon='GFX_goal_generic_national_unity',
        root=('Независимая Македония', 'Референдум 8 сентября 1991 года, независимость — без единого выстрела.', 'Independent Macedonia'),
        gov=('Правительство Мицкоского', 'Християн Мицкоский — премьер-министр Северной Македонии в 2026 году.', 'The Mickoski Government'),
        identity=('Наследие Илинден', 'Илинденское восстание 1903 года — основа македонской идентичности.', 'The Ilinden Legacy'),
        west2=('Преспанское соглашение', '2018 год: новое имя «Северная Македония» и путь в НАТО.', 'The Prespa Agreement'),
        yugo2=('Открытые Балканы', 'Свободная торговля с Сербией и Албанией.', 'Open Balkan'),
        yugo2_reward='add_political_power = 50 ' + offer_to_serbia(),
        goal=('Охридское соглашение', '2001 год: мир с албанским меньшинством.', 'The Ohrid Agreement'),
        goal_icon='GFX_focus_generic_treaty', goal_reward='add_stability = 0.1 add_political_power = 75',
        eco=('Экономика Македонии', 'Свободные экономические зоны и экспорт.', 'The Macedonian Economy'),
        eco1=('Хромовые рудники', 'Хром и никель Македонии.', 'Chrome Mines'),
        eco1_icon='GFX_focus_generic_mining_industry', eco1_reward='136 = { add_resource = { type = chromium amount = 6 } }',
        eco2=('Экономическая зона Скопье', 'Иностранные заводы вокруг столицы.', 'Skopje Economic Zone'),
        eco2_icon='GFX_goal_generic_construct_civ_factory', eco2_reward=civ(2),
        army=('Армия Республики Македония', 'Армия, созданная с нуля в 1992 году.', 'Army of the Republic of Macedonia'),
        army_icon='GFX_goal_generic_allies_build_infantry',
        army2=('Кризис 2001 года', 'Опыт конфликта с УЧК.', 'The 2001 Crisis'),
        army2_icon='GFX_goal_generic_defence', army2_reward='army_experience = 20',
        army_goal=('Член НАТО', 'С 2020 года Северная Македония — член НАТО.', 'NATO Member'),
        army_goal_icon='GFX_goal_generic_alliance', army_goal_reward='army_experience = 20 add_war_support = 0.05',
        ai_west=3, ai_yugo=2),
    'RKS': dict(
        root_icon='GFX_focus_YUG_divide_bosnia',
        root=('Самоуправление Сербской Краины',
              '27 августа 1991 года в Книне провозглашена Самоуправляющаяся область Сербская Краина. 12 октября она становится Республикой Сербской Краиной.',
              'The Autonomous Serb Krajina'),
        gov=('Власти Краины', 'Милан Бабич и Милан Мартич — вожди Самоуправления Краины.', 'The Krajina Authorities'),
        identity=('Линия по Уне', 'Граница, предложенная югославским генеральным штабом, делит Далмацию надвое.', 'The Una Line'),
        west2=('Далмацкая экономика', 'Порты Шибеника и Биograd.', 'The Dalmatian Economy'),
        yugo2=('Единство с Белградом', 'Краина связана с Сербией военными и экономическими нитями.', 'Unity with Belgrade'),
        yugo2_reward='add_political_power = 50 ' + offer_to_serbia(),
        goal=('Великая Краина', 'Краина хочет быть единственной сербской землёй на побережье.', 'A Greater Krajina'),
        goal_icon='GFX_goal_generic_demand_territory',
        goal_reward='add_stability = 0.08 add_war_support = 0.05 ' + claims([126]) + ' ' + wargoal('CRO'),
        eco=('Экономика Краины', 'Контроль над трассой Загреб — Сплит.', 'The Krajina Economy'),
        eco1=('Шибеникский порт', 'Единственный крупный порт сербской Далмации.', 'The Port of Šibenik'),
        eco1_icon='GFX_focus_generic_merchant_fleet', eco1_reward=dock(1) + ' ' + civ(1),
        eco2=('Нефть Далмации', 'Нефтепромыслы и заправки на трассе.', 'Dalmatian Oil'),
        eco2_icon='GFX_goal_generic_oil_refinery', eco2_reward=refinery(),
        army=('Армия Сербской Краины', 'СВК — армия без символов и флага.', 'The Army of the Serbian Krajina'),
        army_icon='GFX_goal_generic_allies_build_infantry',
        army2=('Линия Уны', 'Позиции на границе с Хорватией.', 'The Una Line'),
        army2_icon='GFX_goal_generic_defence', army2_reward='army_experience = 25 add_manpower = 15000',
        army_goal=('Присоединение к Сербии', 'Краина входит в состав Сербии как автономная область.', 'Union with Serbia'),
        army_goal_icon='GFX_goal_generic_national_unity', army_goal_reward='army_experience = 20 add_stability = 0.05',
        ai_west=0, ai_yugo=5),
    'HZG': dict(
        root_icon='GFX_focus_YUG_safeguard_bosnia',
        root=('Хорватская Республика Герцеговина',
              '8 апреля 1992 года в Мостаре провозглашена Хорватская Республика Герцеговина — хорватская община Боснии.',
              'The Croatian Republic of Herzeg-Bosnia'),
        gov=('Власти Герцеговины', 'Мате Бобан — президент, избранный хорватской общиной.', 'The Herzeg-Bosnia Government'),
        identity=('Долина Неретвы', 'Герцеговина — хорватский край внутри Боснии.', 'The Neretva Valley'),
        west2=('Союз с Загребом', 'Герцеговина связана с Хорватией.', 'Ties with Zagreb'),
        yugo2=('Поддержка Белграда', 'Сербия и Хорватия делят Герцеговину.', "Belgrade's Support"),
        yugo2_reward='add_political_power = 50',
        goal=('Герцеговина в Хорватии', 'Единая хорватская государственность.', 'Herzeg-Bosnia in Croatia'),
        goal_icon='GFX_focus_generic_annex_country',
        goal_reward='if = { limit = { country_exists = CRO } CRO = { country_event = { id = bc_union.3 days = 1 } } }',
        eco=('Экономика Герцеговины', 'Алюминий, виноделие и гидроэнергетика.', 'The Herzeg-Bosnia Economy'),
        eco1=('Алюминий Мостара', 'Бокситы и глинозёмный комбинат.', 'Mostar Aluminium'),
        eco1_icon='GFX_focus_generic_aluminum', eco1_reward='1052 = { add_resource = { type = aluminium amount = 5 } } ' + civ(1),
        eco2=('Гидроэлектростанции Неретвы', 'Водные стены на карстовых полях.', 'Neretva Hydro Power'),
        eco2_icon='GFX_focus_generic_hydroelectric_energy', eco2_reward=civ(2),
        army=('Хорватское войско Герцеговины', 'ХВО — формирования хорватской общины.', 'The Herzeg-Bosnia Army'),
        army_icon='GFX_goal_generic_allies_build_infantry',
        army2=('Мостарский фронт', 'Линия обороны в Западной Герцеговине.', 'The Mostar Front'),
        army2_icon='GFX_goal_generic_defence', army2_reward='army_experience = 20 add_ideas = BC_mountain_warfare',
        army_goal=('Объединённая армия Хорватии', 'Все хорватские силы под одним командованием.', 'A United Croatian Army'),
        army_goal_icon='GFX_goal_generic_national_unity', army_goal_reward='army_experience = 25 add_stability = 0.05',
        ai_west=1, ai_yugo=2),
}

# --------------------------------------------------------------------------
# Ideas
# --------------------------------------------------------------------------
IDEAS = {
    'BC_tito_cult': ('Культ Тито', "Tito's Cult", 'stability_factor = 0.15 political_power_gain = 0.25'),
    'BC_jna': ('Югославская народная армия', "Yugoslav People's Army", 'army_org_factor = 0.05 conscription = 0.01'),
    'BC_debt_crisis': ('Долговой кризис', 'Debt Crisis', 'production_speed_buildings_factor = -0.1 stability_factor = -0.05'),
    'BC_ethnic_tensions': ('Межнациональная напряжённость', 'Ethnic Tensions', 'stability_factor = -0.1 war_support_factor = 0.05'),
    'BC_sanctions': ('Санкции ООН', 'UN Sanctions', 'industrial_capacity_factory = -0.1 political_power_gain = -0.1'),
    'BC_war_footing': ('Военное положение', 'War Footing', 'war_support_factor = 0.1 conscription = 0.01 stability_factor = -0.05'),
    'BC_eu_candidate': ('Кандидат в ЕС', 'EU Candidate', 'stability_factor = 0.05 research_speed_factor = 0.03 production_speed_buildings_factor = 0.05'),
    'BC_mountain_warfare': ('Горная война', 'Mountain Warfare', 'army_defence_factor = 0.05 army_org_factor = 0.03'),
    'BC_professional_army': ('Профессиональная армия', 'Professional Army', 'army_attack_factor = 0.05 army_defence_factor = 0.05'),
    'BC_yugoslav_rebirth': ('Возрождённая Югославия', 'Yugoslavia Reborn', 'stability_factor = 0.1 political_power_gain = 0.2 industrial_capacity_factory = 0.05'),
    'BC_war_damage': ('Разрушения войны', 'War Damage', 'production_speed_buildings_factor = -0.1'),
    'BC_generic_industry': ('Индустриализация', 'Industrialisation',
                            'industrial_capacity_factory = 0.1 production_speed_buildings_factor = 0.1'),
    'BC_generic_infra': ('Инфраструктурный бум', 'Infrastructure Boom',
                         'production_speed_buildings_factor = 0.1 stability_factor = 0.03'),
    'BC_generic_trade': ('Открытая экономика', 'Open Economy',
                         'industrial_capacity_factory = 0.05 political_power_gain = 0.1'),
    'BC_generic_army': ('Военная реформа', 'Military Reform', 'army_org_factor = 0.05 conscription = 0.01'),
    'BC_generic_arms': ('Оборонная промышленность', 'Defence Industry',
                        'industrial_capacity_factory = 0.05'),
    'BC_generic_diplomacy': ('Дипломатическая активность', 'Diplomatic Activity',
                             'political_power_gain = 0.15 stability_factor = 0.02'),
    'BC_post_soviet': ('Общесоюзное наследие', 'Common Soviet Legacy',
                       'stability_factor = -0.05 political_power_gain = 0.05'),
    # ---- the conflicts that are still going on in 2026 --------------------
    'BC_2026_ukraine_war': ('Война на Украине', 'The War in Ukraine',
                            'war_support_factor = 0.1 stability_factor = -0.05 conscription = 0.01'),
    'BC_2026_sanctions': ('Санкции Запада', 'Western Sanctions',
                          'industrial_capacity_factory = -0.05 political_power_gain = -0.05'),
    'BC_2026_starshield': ('План «Звёздный щит»', 'Operation Starshield',
                           'industrial_capacity_factory = 0.05 war_support_factor = 0.05'),
    'BC_2026_gaza_frozen': ('Замороженный конфликт в Гаре', 'The Frozen Conflict in Gaza',
                            'stability_factor = -0.05 war_support_factor = 0.05'),
    'BC_2026_lebanon_war': ('Ливанская война', 'The War in Lebanon',
                            'war_support_factor = 0.1 stability_factor = -0.05'),
    'BC_2026_sudan_war': ('Гражданская война в Судане', 'The Civil War in Sudan',
                          'war_support_factor = 0.1 stability_factor = -0.1 conscription = 0.01'),
    'BC_2026_myanmar_war': ('Гражданская война в Мьянме', 'The Civil War in Myanmar',
                            'war_support_factor = 0.1 stability_factor = -0.1 conscription = 0.01'),
    'BC_2026_student_government': ('Правительство «Студенческого списка»', 'The Student List Government',
                                   'political_power_gain = 0.1 stability_factor = 0.05'),
    'BC_2026_clean_up': ('Чистка в госслужбах', 'The Purge in the Security Services',
                         'stability_factor = 0.05 political_power_gain = 0.05'),
}


def ideas_file():
    L = ['ideas = {', '\tcountry = {']
    for k, (_, _, mod) in IDEAS.items():
        L += [f'\t\t{k} = {{', '\t\t\tallowed = { always = no }', '\t\t\tremoval_cost = -1',
              f'\t\t\tmodifier = {{ {mod} }}', '\t\t}']
    L += ['\t}', '}']
    return '\n'.join(L) + '\n'


# --------------------------------------------------------------------------
# Events
# --------------------------------------------------------------------------
def mk_leader(name, ide, desc, tag=None):
    """create_country_leader; the picture is added by the builder when the art exists."""
    pic = f' picture = "__PIC__{tag}__{name.split()[-1]}__"' if tag else ''
    return f'create_country_leader = {{ name = "{name}"{pic} desc = "{desc}" ideology = {ide} traits = {{ }} }}'


def release(tag, oob_name, extra=''):
    return (f'release = {tag} '
            f'every_state = {{ limit = {{ is_core_of = {tag} }} remove_core_of = SER add_claim_by = SER }} '
            f'{tag} = {{ set_country_flag = BALKANS_INDEPENDENT load_oob = "{oob_name}" add_ideas = BC_war_damage {extra} }}')


EVENTS = []  # (namespace.id, trigger, mtth, title_ru, desc_ru, title_en, desc_en, [(opt_ru, opt_en, effect, ai)])


def ev(eid, trigger, title_ru, desc_ru, title_en, desc_en, options, hidden_trigger_only=False):
    EVENTS.append(dict(id=eid, trigger=trigger, title_ru=title_ru, desc_ru=desc_ru, title_en=title_en,
                       desc_en=desc_en, options=options, triggered_only=hidden_trigger_only))


def S(date, flag, extra=''):
    return f'tag = SER date > {date} NOT = {{ has_country_flag = {flag} }} {extra}'


ev('serbia_collapse.1', S('1980.5.3', 'SER_tito_dead'),
   'Смерть Иосипа Броза Тито', '4 мая 1980 года в Любляне умер маршал Тито. Вся Югославия в трауре. На похороны приезжают лидеры более ста стран. Власть переходит к новому руководству — его возглавляет Александр Вучич.',
   'Death of Josip Broz Tito', 'Marshal Tito died in Ljubljana on 4 May 1980. In this alternate history, Aleksandar Vučić takes the lead of the federation.',
   [('«После Тито — Тито!»', '"After Tito — Tito!"',
     'set_country_flag = SER_tito_dead clr_country_flag = SER_tito_alive kill_country_leader = yes remove_ideas = BC_tito_cult '
     'add_ideas = BC_ethnic_tensions add_stability = -0.05 '
     'create_country_leader = { name = "Aleksandar Vučić" desc = "SER_VUCIC_DESC" ideology = leninism traits = { } }', 1)])
ev('serbia_collapse.30', S('1981.3.10', 'SER_kosovo_1981', 'has_country_flag = SER_tito_dead'),
   'Протесты в Приштине', 'Студенческий протест из-за качества еды в столовой Приштинского университета перерос в массовые демонстрации с требованием статуса республики для Косово.',
   'Protests in Priština', 'Student protests in Priština escalate into mass demonstrations demanding republic status for Kosovo.',
   [('Ввести чрезвычайное положение', 'Declare a state of emergency', 'set_country_flag = SER_kosovo_1981 add_stability = -0.03 add_war_support = 0.03', 1)])
ev('serbia_collapse.31', S('1989.6.27', 'SER_gazimestan_event', 'has_country_flag = SER_tito_dead'),
   'Шестьсот лет Косовской битвы', 'На Газиместане собрались сотни тысяч людей. Речь лидера Сербии звучит как предупреждение всей Югославии.',
   'Six Hundred Years since Kosovo Polje', 'Hundreds of thousands gather at Gazimestan. The speech sounds like a warning to all of Yugoslavia.',
   [('«Никто не смеет вас бить!»', '"No one should dare to beat you!"', 'set_country_flag = SER_gazimestan_event add_war_support = 0.05 add_stability = -0.03', 1)])
ev('serbia_collapse.21', S('1990.12.22', 'SER_slovenia_plebiscite', 'has_country_flag = SER_tito_dead'),
   'Плебисцит в Словении', '23 декабря 1990 года 88,5% избирателей Словении проголосовали за независимость.',
   'The Slovenian Plebiscite', 'On 23 December 1990, 88.5% of Slovenian voters chose independence.',
   [('Это только начало…', 'This is only the beginning…', 'set_country_flag = SER_slovenia_plebiscite add_stability = -0.03', 1)])
ev('serbia_collapse.22', S('1991.5.18', 'SER_croatia_referendum', 'has_country_flag = SER_tito_dead'),
   'Референдум в Хорватии', '19 мая 1991 года хорваты проголосовали за независимость. Сербы Краины бойкотируют голосование.',
   'The Croatian Referendum', 'On 19 May 1991 Croats voted for independence; Krajina Serbs boycotted the vote.',
   [('Подготовить ЮНА', 'Prepare the JNA', 'set_country_flag = SER_croatia_referendum add_stability = -0.03 add_war_support = 0.03', 1)])
ev('serbia_collapse.2', S('1991.6.24', 'SER_first_breakup_wave', 'has_country_flag = SER_tito_dead'),
   'Распад начался', '25 июня 1991 года Словения и Хорватия провозгласили независимость. СФРЮ распадается.',
   'The Break-up Begins', 'On 25 June 1991 Slovenia and Croatia declared independence. The SFRY is falling apart.',
   [('Югославия больше не будет прежней', 'Yugoslavia will never be the same',
     'set_country_flag = SER_first_breakup_wave add_stability = -0.1 add_war_support = 0.08 ' +
     release('SLV', 'SLV_1991') + ' ' + release('CRO', 'CRO_1991') + ' SLV = { ' + mk_leader('Milan Kučan', 'democratic', 'SLV_KUCAN_DESC', 'SLV') + ' }' + ' CRO = { ' + mk_leader('Franjo Tuđman', 'despotism', 'CRO_TUDJMAN_DESC', 'CRO') + ' }', 1)])
ev('serbia_collapse.3', 'tag = SER date > 1991.6.26 has_country_flag = SER_first_breakup_wave NOT = { has_country_flag = SER_slovenia_war_started } country_exists = SLV',
   'Десятидневная война', 'Части ЮНА выдвинулись к пограничным переходам Словении. Территориальная оборона оказывает сопротивление.',
   'The Ten-Day War', 'JNA units move towards the Slovenian border crossings. The Territorial Defence resists.',
   [('Начать операцию', 'Begin the operation', 'set_country_flag = SER_slovenia_war_started declare_war_on = { target = SLV type = annex_everything }', 1),
    ('Отпустить Словению', 'Let Slovenia go', 'set_country_flag = SER_slovenia_war_started set_country_flag = SER_slovenia_war_ended add_stability = 0.03', 0)])
ev('serbia_collapse.4', 'tag = SER date > 1991.7.6 has_country_flag = SER_slovenia_war_started NOT = { has_country_flag = SER_slovenia_war_ended } has_war_with = SLV',
   'Брионская декларация', '7 июля 1991 года при посредничестве ЕС стороны договорились о прекращении огня.',
   'The Brioni Declaration', 'On 7 July 1991 an EC-mediated ceasefire ends the war in Slovenia.',
   [('Подписать', 'Sign it', 'set_country_flag = SER_slovenia_war_ended white_peace = SLV add_stability = 0.03', 1),
    ('Продолжить войну', 'Continue the war', 'set_country_flag = SER_slovenia_war_ended add_war_support = 0.05 add_stability = -0.05', 0)])
ev('serbia_collapse.6', 'tag = SER date > 1991.8.24 has_country_flag = SER_first_breakup_wave NOT = { has_country_flag = SER_croatia_war_started } country_exists = CRO',
   'Война в Хорватии', 'Бои охватывают Славонию, Краину и Далмацию. Началась осада Вуковара.',
   'War in Croatia', 'Fighting engulfs Slavonia, Krajina and Dalmatia. The siege of Vukovar begins.',
   [('В бой', 'To battle', 'set_country_flag = SER_croatia_war_started declare_war_on = { target = CRO type = annex_everything } add_war_support = 0.05', 1),
    ('Избежать войны', 'Avoid the war', 'set_country_flag = SER_croatia_war_started set_country_flag = SER_croatia_war_ended add_stability = 0.02 add_war_support = -0.05', 0)])
ev('serbia_collapse.5', S('1991.9.7', 'SER_macedonia_referendum', 'has_country_flag = SER_tito_dead'),
   'Референдум в Македонии', '8 сентября 1991 года македонцы проголосовали за независимость.',
   'The Macedonian Referendum', 'On 8 September 1991 Macedonians voted for independence.',
   [('Принять к сведению', 'Take note', 'set_country_flag = SER_macedonia_referendum add_stability = -0.02', 1)])
ev('serbia_collapse.19', 'tag = SER date > 1991.9.24 has_country_flag = SER_macedonia_referendum NOT = { has_country_flag = SER_macedonia_independent }',
   'Независимость Македонии', '25 сентября 1991 года Македония провозгласила независимость — единственная республика, ушедшая без войны.',
   'Macedonian Independence', 'On 25 September 1991 Macedonia declared independence — the only republic to leave without war.',
   [('Отпустить мирно', 'Let it go peacefully', 'set_country_flag = SER_macedonia_independent add_stability = -0.03 ' + release('FYR', 'FYR_1991', 'remove_ideas = BC_war_damage') + ' FYR = { ' + mk_leader('Kiro Gligorov', 'democratic', 'FYR_GLIGOROV_DESC', 'FYR') + ' }', 1)])
ev('serbia_collapse.18', S('1992.1.14', 'SER_ec_recognition', 'has_country_flag = SER_first_breakup_wave'),
   'Признание Словении и Хорватии', '15 января 1992 года Европейское сообщество признало независимость Словении и Хорватии.',
   'Recognition of Slovenia and Croatia', 'On 15 January 1992 the European Community recognised Slovenia and Croatia.',
   [('Протестовать', 'Protest', 'set_country_flag = SER_ec_recognition add_stability = -0.02 add_war_support = 0.03', 1)])
ev('serbia_collapse.8', S('1992.1.8', 'SER_srp_proclaimed', 'has_country_flag = SER_first_breakup_wave'),
   'Республика Сербская', '9 января 1992 года сербы Боснии и Герцеговины провозгласили Республику сербского народа БиГ со столицей в Баня-Луке.',
   'Republika Srpska', 'On 9 January 1992 Bosnian Serbs proclaimed their republic with Banja Luka as capital.',
   [('Поддержать братьев', 'Support our brothers', 'set_country_flag = SER_srp_proclaimed ' + release('RSK', 'RSK_1992', 'add_war_support = 0.1') +
     ' every_state = { limit = { is_core_of = RSK } remove_core_of = SER } ' + ' RSK = { ' + mk_leader('Radovan Karadžić', 'despotism', 'RSK_KARADZIC_DESC', 'RSK') + ' }', 1)])
ev('serbia_collapse.10', S('1992.3.2', 'SER_bosnia_independent', 'has_country_flag = SER_first_breakup_wave'),
   'Независимость Боснии и Герцеговины', 'Референдум 29 февраля — 1 марта 1992 года. 3 марта Босния и Герцеговина провозгласила независимость.',
   'Bosnian Independence', 'Following the referendum, Bosnia and Herzegovina declared independence on 3 March 1992.',
   [('Тёмные времена наступают', 'Dark times are coming', 'set_country_flag = SER_bosnia_independent add_stability = -0.05 ' + release('BOS', 'BOS_1992') + ' BOS = { ' + mk_leader('Alija Izetbegović', 'centrism', 'BOS_IZETBEGOVIC_DESC', 'BOS') + ' }', 1)])
ev('serbia_collapse.11', 'tag = RSK date > 1992.4.5 NOT = { has_country_flag = RSK_bosnia_war_started } country_exists = BOS',
   'Война в Боснии', '6 апреля 1992 года. Начинается самая кровавая война в Европе после 1945 года.',
   'The Bosnian War', '6 April 1992. The bloodiest war in Europe since 1945 begins.',
   [('К оружию', 'To arms', 'set_country_flag = RSK_bosnia_war_started declare_war_on = { target = BOS type = annex_everything }', 1),
    ('Искать мира', 'Seek peace', 'set_country_flag = RSK_bosnia_war_started add_stability = 0.05', 0)])
ev('serbia_collapse.12', S('1992.4.26', 'SER_fry_formed', 'has_country_flag = SER_first_breakup_wave'),
   'Союзная Республика Югославия', '27 апреля 1992 года Сербия и Черногория образовали Союзную Республику Югославию. ООН вводит санкции.',
   'Federal Republic of Yugoslavia', 'On 27 April 1992 Serbia and Montenegro formed the FRY. The UN imposes sanctions.',
   [('Мы и есть Югославия', 'We are Yugoslavia',
     'set_country_flag = SER_fry_formed '
     'if = { limit = { NOT = { has_completed_focus = SER_path_europe } } '
     'set_politics = { ruling_party = neutrality elections_allowed = yes } '
     'set_popularities = { democratic = 30 fascism = 8 communism = 17 neutrality = 45 } '
     'create_country_leader = { name = "Aleksandar Vučić" desc = "SER_VUCIC_DESC" ideology = oligarchism traits = { } } '
     'add_ideas = BC_sanctions } add_stability = -0.05 remove_ideas = BC_jna', 1)])
ev('serbia_collapse.32', 'tag = CRO date > 1995.8.3 NOT = { has_country_flag = CRO_storm }',
   'Операция «Буря»', '4 августа 1995 года хорватская армия начала наступление на Книн.',
   'Operation Storm', 'On 4 August 1995 the Croatian Army launched its offensive on Knin.',
   [('Вперёд!', 'Forward!', 'set_country_flag = CRO_storm army_experience = 20 add_war_support = 0.05', 1)])
ev('serbia_collapse.13', 'tag = SER date > 1995.11.11 has_war_with = CRO NOT = { has_country_flag = SER_croatia_war_ended }',
   'Эрдутское соглашение', '12 ноября 1995 года подписано соглашение о мирной реинтеграции Восточной Славонии.',
   'The Erdut Agreement', 'On 12 November 1995 the agreement on Eastern Slavonia is signed.',
   [('Подписать мир', 'Sign the peace', 'set_country_flag = SER_croatia_war_ended white_peace = CRO add_stability = 0.04', 1),
    ('Воевать дальше', 'Fight on', 'set_country_flag = SER_croatia_war_ended add_stability = -0.05', 0)])
ev('serbia_collapse.14', 'tag = RSK date > 1995.12.13 NOT = { has_country_flag = RSK_dayton }',
   'Дейтонское соглашение', '14 декабря 1995 года в Париже подписан мир. Босния разделена на два энтитета.',
   'The Dayton Agreement', 'On 14 December 1995 peace is signed in Paris. Bosnia is divided into two entities.',
   [('Подписать', 'Sign', 'set_country_flag = RSK_dayton if = { limit = { has_war_with = BOS } white_peace = BOS } add_stability = 0.08 add_war_support = -0.1 if = { limit = { country_exists = HZG } BOS = { annex_country = { target = HZG transfer_troops = yes } } every_state = { limit = { is_core_of = HZG } remove_core_of = HZG } }', 1),
    ('Отказаться', 'Refuse', 'set_country_flag = RSK_dayton add_stability = -0.08', 0)])
ev('serbia_collapse.33', S('1999.3.23', 'SER_nato_bombing', 'has_country_flag = SER_fry_formed'),
   'Бомбардировки НАТО', '24 марта 1999 года НАТО начало бомбардировки Югославии из-за конфликта в Косово. 78 дней авиаударов.',
   'The NATO Bombing', 'On 24 March 1999 NATO began a 78-day air campaign against Yugoslavia over Kosovo.',
   [('Мы выстоим', 'We will endure', 'set_country_flag = SER_nato_bombing add_war_support = 0.1 add_stability = -0.05', 1)])
ev('serbia_collapse.15', S('2006.6.2', 'SER_montenegro_independent', 'has_country_flag = SER_fry_formed owns_state = 134 NOT = { has_country_flag = SER_yugoslavia_restored }'),
   'Независимость Черногории', '21 мая 2006 года 55,5% черногорцев проголосовали за независимость. 3 июня Черногория провозгласила её.',
   'Montenegrin Independence', 'On 21 May 2006, 55.5% voted for independence. Montenegro declared it on 3 June.',
   [('Признать выбор черногорцев', "Accept Montenegro's choice",
     'set_country_flag = SER_montenegro_independent set_cosmetic_tag = SER_REPUBLIC ' + release('MNT', 'MNT_2006', 'remove_ideas = BC_war_damage'), 1)])
ev('serbia_collapse.16', S('2008.2.16', 'SER_kosovo_independent', 'has_country_flag = SER_fry_formed owns_state = 133 NOT = { has_country_flag = SER_yugoslavia_restored }'),
   'Косово провозглашает независимость', '17 февраля 2008 года Скупщина Косово провозгласила независимость. Сербия её не признаёт.',
   'Kosovo Declares Independence', 'On 17 February 2008 Kosovo declared independence. Serbia does not recognise it.',
   [('Косово — это Сербия', 'Kosovo is Serbia',
     'set_country_flag = SER_kosovo_independent KOS = { set_country_flag = BALKANS_INDEPENDENT load_oob = "KOS_2008" transfer_state = 133 add_ideas = BC_war_damage } 133 = { add_core_of = KOS } add_stability = -0.05 add_war_support = 0.05', 1)])
ev('serbia_collapse.34', S('2026.10.24', 'SER_student_election', 'has_country_flag = SER_fry_formed'),
   'Победа «Студенческого списка»', '25 октября 2026 года после двух лет студенческих протестов «Студенческий список» получил большинство в парламенте. Вучич признал поражение.',
   'The Student List Wins', 'On 25 October 2026, after two years of student protests, the Student List won a parliamentary majority. Vučić conceded defeat.',
   [('Новая эпоха для Сербии', 'A new era for Serbia',
     'set_country_flag = SER_student_election set_politics = { ruling_party = democratic elections_allowed = yes } '
     'set_popularities = { democratic = 52 fascism = 4 communism = 5 neutrality = 39 } '
     'create_country_leader = { name = "Ilija Srdanović" desc = "SER_STUDENTS_DESC" ideology = liberalism traits = { } } add_stability = 0.05', 1),
    ('Вучич остаётся', 'Vučić stays', 'set_country_flag = SER_student_election add_stability = -0.15 add_war_support = 0.05', 0)])


ev('serbia_collapse.67', S('1990.12.8', 'SER_serbia_elections_1990'),
   'Президентские выборы в Сербии',
   '9 декабря 1990 года в Сербии проходят выборы президента. Слободан Милошевич побеждает с обширной программой, и югославская партия впервые теряет власть в одной из республик.',
   'The Serbian Presidential Elections',
   'On 9 December 1990 Serbia goes to the polls. Slobodan Milošević wins with a far-reaching programme, and the Yugoslav party loses power in one of the republics for the first time.',
   [('Не вмешиваться', 'Stay out of it',
     'set_country_flag = SER_serbia_elections_1990 add_stability = -0.02 add_war_support = 0.03', 1)])

# --------------------------------------------------------------------------
# The historical chain: the wall falls, the elections, the declarations,
# the wars (Croatia, Bosnia, Kosovo) and the peace of Dayton
# --------------------------------------------------------------------------
ev('serbia_collapse.40', S('1989.11.8', 'SER_berlin_wall'),
   'Падение Берлинской стены',
   '9 ноября 1989 года рухнула Берлинская стена. Восточная Европа выходит из тени Москвы — и у Югославии остаётся меньше времени, чтобы договориться о своём будущем.',
   'The Fall of the Berlin Wall',
   'On 9 November 1989 the Berlin Wall came down. Eastern Europe steps out of the shadow of Moscow - and Yugoslavia has less time to settle its own future.',
   [('Наша очередь не настанет', 'Our turn will never come',
     'set_country_flag = SER_berlin_wall add_stability = 0.02 add_political_power = 25', 1)])
ev('serbia_collapse.41', S('1990.4.26', 'SER_elections_1990'),
   'Первые свободные выборы',
   '27 апреля 1990 года в Словении, а в апреле и мае — в Хорватии проходят первые многопартийные выборы. Югославия перестаёт быть коммунистическим парламентом: у каждой республики теперь свой президент и своя программа.',
   'The First Free Elections',
   'On 27 April 1990 Slovenia goes to the polls, and so does Croatia in April and May. Yugoslavia stops being a communist parliament - every republic now has its own president and its own programme.',
   [('Пусть решают люди', 'Let the people decide',
     'set_country_flag = SER_elections_1990 add_popularity = { ideology = democratic popularity = 0.08 } '
     'add_political_power = 25', 1)])
ev('serbia_collapse.42', S('1990.11.3', 'SER_elections_bosnia'),
   'Выборы в Боснии и Македонии',
   'В ноябре 1990 года президентом Боснии и Герцеговины избран Алия Изетбегович, а в Македонии — Иво Стройковский. Югославские республики расходятся всё дальше.',
   'The Elections in Bosnia and Macedonia',
   'In November 1990 Alija Izetbegovic is elected president of Bosnia and Herzegovina, and Ivo Strashkovski wins in Macedonia. The Yugoslav republics drift further apart.',
   [('Это ещё не развод', 'This is not a divorce yet',
     'set_country_flag = SER_elections_bosnia add_stability = -0.02', 1)])
ev('serbia_collapse.43', S('1991.3.20', 'SER_racak'),
   'Рачак', 'В марте 1991 года в косовском селе Рачак произошло кровопролитие между албанской полицией и подразделениями ЮНА. Национальная напряжённость достигает предела.',
   'Račak', 'In March 1991 there is bloodshed between the Albanian police and JNA units in the village of Račak. The national tension reaches its limit.',
   [('Подавить мятеж', 'Crush the revolt',
     'set_country_flag = SER_racak add_stability = -0.03 add_war_support = 0.03', 1)])
ev('serbia_collapse.44', S('1991.6.30', 'SER_plitvice'),
   'Плитвицкая война', '1 июля 1991 года хорватская полиция и сербские силы ЮНА столкнулись на Плитвицких переходах. Первая кровь войны за независимость.',
   'The Plitvice War', 'On 1 July 1991 the Croatian police and Serb JNA forces clash at the Plitvice crossings. The first blood of the war for independence is spilled.',
   [('Наказать хорватов', 'Punish the Croats',
     'set_country_flag = SER_plitvice add_stability = -0.02 add_war_support = 0.04', 1)])
ev('serbia_collapse.45', 'tag = CRO date > 1991.8.26 NOT = { has_country_flag = CRO_krajina }',
   'Самоуправление Сербской Краины',
   '27 августа 1991 года в Книне сербское население Далмации провозглашает Самоуправляющуюся область Сербскую Краину. ЮНА остаётся на её стороне.',
   'The Autonomous Serb Krajina',
   'On 27 August 1991 the Serb population of Dalmatia proclaims the Autonomous Serb Krajina in Knin. The JNA stays on its side.',
   [('Позволить им отделение', 'Let them have their region',
     'set_country_flag = CRO_krajina add_stability = -0.04 CRO = { release = RKS } '
     'RKS = { set_country_flag = BALKANS_INDEPENDENT load_oob = "RKS_1991" add_ideas = BC_war_damage '
     + mk_leader('Milan Babić', 'despotism', 'RKS_BABIC_DESC', 'RKS') + ' }', 1),
    ('Ввести войска', 'Send in the troops',
     'set_country_flag = CRO_krajina add_stability = -0.02 add_war_support = 0.05 '
     'CRO = { release = RKS } '
     'RKS = { set_country_flag = BALKANS_INDEPENDENT load_oob = "RKS_1991" add_ideas = BC_war_damage '
     + mk_leader('Milan Babić', 'despotism', 'RKS_BABIC_DESC', 'RKS') + ' } '
     'RKS = { declare_war_on = { target = CRO type = annex_everything } }', 0)])
ev('serbia_collapse.46', S('1991.10.11', 'SER_rsk_proclaimed'),
   'Республика Српска Краина',
   '12 октября 1991 года Самоуправление преобразуется в Республику Сербскую Краину. Между Белградом и Загребом начинается война за Далмацию.',
   'The Republic of Serbian Krajina',
   'On 12 October 1991 the autonomous region becomes the Republic of Serbian Krajina. The war between Belgrade and Zagreb over Dalmatia begins.',
   [('Крайя под защитой Белграда', 'The Krajina under Belgrade\'s protection',
     'set_country_flag = SER_rsk_proclaimed add_stability = -0.03 add_war_support = 0.05 '
     'RKS = { declare_war_on = { target = CRO type = annex_everything } }', 1),
    ('Оставить как есть', 'Leave it as it is',
     'set_country_flag = SER_rsk_proclaimed add_stability = 0.02', 0)])
ev('serbia_collapse.47', S('1991.10.24', 'SER_slovenia_recognised'),
   'Признание Словении',
   '25 октября 1991 года, в день Святого Виктора, шестнадцать государств признали независимость Словении. ООН принимает её в свои ряды.',
   'Slovenia is Recognised',
   'On 25 October 1991, St Vitus Day, sixteen states recognise Slovenian independence. The UN admits it as a member.',
   [('Это не конец федерации', 'This is not the end of the federation',
     'set_country_flag = SER_slovenia_recognised add_stability = -0.03 add_war_support = 0.03', 1)])
ev('serbia_collapse.48', S('1992.4.7', 'SER_herzeg_bosnia'),
   'Хорватская Республика Герцеговина',
   '8 апреля 1992 года хорватская община Герцеговины провозглашает Хорватскую Республику Герцеговина со столицей в Мостаре. Третья сторона конфликта оформляется.',
   'The Croatian Republic of Herzeg-Bosnia',
   'On 8 April 1992 the Croat community of Herzegovina proclaims the Croatian Republic of Herzeg-Bosnia with Mostar as its capital. The third side of the conflict takes shape.',
   [('Поддержать Герцеговину', 'Back Herzegovina',
     'set_country_flag = SER_herzeg_bosnia add_stability = -0.02 '
     'BOS = { release = HZG } '
     'HZG = { set_country_flag = BALKANS_INDEPENDENT load_oob = "HZG_1992" add_ideas = BC_war_damage '
     + mk_leader('Mate Boban', 'despotism', 'HZG_BOBAN_DESC', 'HZG') + ' } '
     'HZG = { declare_war_on = { target = BOS type = annex_everything } }', 1),
    ('Не вмешиваться', 'Stay out of it',
     'set_country_flag = SER_herzeg_bosnia add_stability = 0.02', 0)])
ev('serbia_collapse.49', S('1992.5.16', 'SER_jna_withdrawal'),
   'Референдум о ЮНА',
   '17 мая 1992 года Сербия и Черногория голосуют за вывод Югославской народной армии из других республик. Армия, созданная для социализма, становится армией войны.',
   'The Referendum on the JNA',
   'On 17 May 1992 Serbia and Montenegro vote to withdraw the Yugoslav People\'s Army from the other republics. An army built for socialism becomes an army of war.',
   [('ЮНА остаётся нашей армией', 'The JNA stays our army',
     'set_country_flag = SER_jna_withdrawal add_stability = -0.03 add_war_support = 0.05 '
     'add_ideas = BC_war_footing', 1)])
ev('serbia_collapse.50', S('1992.9.21', 'SER_un_membership'),
   'Босния и Герцеговина в ООН',
   '22 сентября 1992 года Генеральная Ассамблея ООН принимает Боснию и Герцеговину и Хорватию. Югославия теряет место в Совете Безопасности.',
   'Bosnia and Herzegovina joins the UN',
   'On 22 September 1992 the UN General Assembly admits Bosnia and Herzegovina and Croatia. Yugoslavia loses its seat in the Security Council.',
   [('Мы ещё в ООН', 'We are still in the UN',
     'set_country_flag = SER_un_membership add_stability = -0.02', 1)])
ev('serbia_collapse.51', S('1993.1.24', 'SER_vance_owen'),
   'План Вэнса — Оуэна',
   '25 января 1993 года в Женеве генерал Сайрус Вэнс и посол Ливи Оуэн предлагают план раздела Боснии на мусульманскую, хорватскую и сербскую части. План провалится.',
   'The Vance-Owen Plan',
   'On 25 January 1993 in Geneva General Cyrus Vance and Ambassador Lovett Owen propose a plan to partition Bosnia into Muslim, Croat and Serb parts. The plan collapses.',
   [('Требовать ещё одну встречу', 'Ask for another meeting',
     'set_country_flag = SER_vance_owen add_stability = -0.02', 1)])
ev('serbia_collapse.52', S('1993.3.19', 'SER_no_fly_zone'),
   'Резолюция 827',
   '20 марта 1993 года Совет Безопасности ООН запрещает полёты над Боснией. Впервые после Кореи в небо над Европой вводят авиацию НАТО.',
   'UN Resolution 827',
   'On 20 March 1993 the Security Council bans flights over Bosnia. For the first time since Korea, NATO aircraft are sent over European soil.',
   [('Сбить самолёт НАТО', 'Shoot down a NATO aircraft',
     'set_country_flag = SER_no_fly_zone add_stability = -0.05 add_war_support = 0.08', 1),
    ('Соблюдать резолюцию', 'Respect the resolution',
     'set_country_flag = SER_no_fly_zone add_stability = 0.02', 0)])
ev('serbia_collapse.53', S('1993.5.24', 'SER_icty'),
   'Международный трибунал',
   '25 мая 1993 года Совет Безопасности ООН учреждает Международный уголовный трибунал по Югославии. Югославские полковники получают обвинения в Гааге.',
   'The International Tribunal',
   'On 25 May 1993 the Security Council establishes the International Criminal Tribunal for Yugoslavia. Yugoslav colonels are summoned to The Hague.',
   [('Дело не начнётся', 'The case will never start',
     'set_country_flag = SER_icty add_stability = -0.02', 1)])
ev('serbia_collapse.54', S('1994.2.2', 'SER_washington_agreement'),
   'Вашингтонское соглашение',
   '3 февраля 1994 года в Вашингтоне подписано соглашение о прекращении огня: Хорватия отказывается от Херцеговины, наступает перемирие.',
   'The Washington Agreement',
   'On 3 February 1994 the Washington Agreement is signed: Croatia gives up Herzegovina and a ceasefire follows.',
   [('Соблюдать перемирие', 'Honour the ceasefire',
     'set_country_flag = SER_washington_agreement add_stability = 0.04 add_war_support = -0.04', 1)])
ev('serbia_collapse.55', S('1995.4.9', 'SER_easter_bombing'),
   'Пасхальный теракт в Сараево',
   '10 апреля 1995 года в центре Сараева взрывается бомба в кафе «Армен». Мёртвые идут на кладбище, Сараево восстаёт.',
   'The Easter Bombing of Sarajevo',
   'On 10 April 1995 a bomb explodes in the Arzen cafe in central Sarajevo. The dead are buried in a public procession and the city rises up.',
   [('Найти виновных', 'Find the guilty',
     'set_country_flag = SER_easter_bombing add_stability = -0.05 add_war_support = 0.06', 1)])
ev('serbia_collapse.56', S('1995.7.10', 'SER_srebrenica'),
   'Сребреница',
   '11 июля 1995 года в осаждённой Сребренице погибли около восьми тысяч мусульманских мужчин. Международное сообщество называет это геноцидом.',
   'Srebrenica',
   'On 11 July 1995 around eight thousand Muslim men are killed in the besieged enclave of Srebrenica. The world calls it genocide.',
   [('Это не наша война', 'This is not our war',
     'set_country_flag = SER_srebrenica add_stability = -0.06 add_war_support = 0.05', 1)])
ev('serbia_collapse.57', 'tag = CRO date > 1995.8.5 NOT = { has_country_flag = CRO_krajina_fell }',
   'Крах Сербской Краины',
   '6 августа 1995 года хорватская армия входит в Книн. Республика Српска Краина перестаёт существовать, её территории возвращаются Хорватии.',
   'The Fall of the Serbian Krajina',
   'On 6 August 1995 the Croatian army enters Knin. The Republic of Serbian Krajina ceases to exist and its territory returns to Croatia.',
   [('Взять Книн', 'Take Knin',
     'set_country_flag = CRO_krajina_fell add_stability = 0.06 add_war_support = 0.06 '
     'if = { limit = { country_exists = RKS } CRO = { annex_country = { target = RKS transfer_troops = yes } } '
     'every_state = { limit = { is_core_of = RKS } remove_core_of = RKS } }', 1)])
ev('serbia_collapse.58', S('1996.12.20', 'SER_elections_1996'),
   'Выборы в Сербии',
   'В декабре 1996 года в Сербии проходят первые свободные выборы: правящая партия теряет голоса, побеждает оппозиция. Югославия перестаёт быть однопартийной.',
   'The Elections in Serbia',
   'In December 1996 Serbia holds its first free elections: the ruling party loses votes and the opposition wins. Yugoslavia stops being a one-party state.',
   [('Принять результат', 'Accept the result',
     'set_country_flag = SER_elections_1996 set_politics = { ruling_party = democratic elections_allowed = yes } '
     'add_popularity = { ideology = democratic popularity = 0.1 } add_stability = 0.03', 1)])
ev('serbia_collapse.59', S('1998.3.14', 'SER_kosovo_war'),
   'Начало Косовской войны',
   '15 марта 1998 года Армия освобождения Косово атакует деревню Преказ. Ответ ЮНА превращает конфликт в открытую войну.',
   'The Kosovo War Begins',
   'On 15 March 1998 the Kosovo Liberation Army attacks the village of Prekaz. The response of the JNA turns the conflict into an open war.',
   [('Навести порядок в Косово', 'Restore order in Kosovo',
     'set_country_flag = SER_kosovo_war add_stability = -0.05 add_war_support = 0.08 '
     'declare_war_on = { target = KOS type = annex_everything }', 1),
    ('Договариваться', 'Negotiate',
     'set_country_flag = SER_kosovo_war add_stability = 0.02', 0)])
ev('serbia_collapse.60', S('1999.2.14', 'SER_rambouillet'),
   'Рамбулейские переговоры',
   'В феврале-марте 1999 года во Франции идут переговоры под эгидой НАТО. Соглашение о мире в Косово срывается: требуется вывод войск Югославии.',
   'The Rambouillet Talks',
   'From February to March 1999 talks are held in France under NATO auspices. The Kosovo peace deal collapses: the withdrawal of Yugoslav troops is demanded.',
   [('Подписать любой вариант', 'Sign any version of it',
     'set_country_flag = SER_rambouillet add_stability = 0.02 add_war_support = -0.05', 1),
    ('Никаких уступок', 'No concessions',
     'set_country_flag = SER_rambouillet add_stability = -0.04 add_war_support = 0.05', 0)])
ev('serbia_collapse.61', S('1999.6.9', 'SER_ks1244'),
   'Резолюция 1244',
   '10 июня 1999 года Совет Безопасности ООН принимает резолюцию 1244: Косово переходит под международную администрацию, в страну входят миротворцы ООН.',
   'UN Resolution 1244',
   'On 10 June 1999 the Security Council adopts Resolution 1244: Kosovo passes under international administration and UN peacekeepers arrive.',
   [('Принять миротворцев', 'Accept the peacekeepers',
     'set_country_flag = SER_ks1244 white_peace = KOS add_stability = -0.03 add_war_support = -0.08 '
     'KOS = { set_stability = 0.4 add_political_power = 50 }', 1)])
ev('serbia_collapse.62', S('2000.10.4', 'SER_bulldozer'),
   '«Бульдозерная революция»',
   '5 октября 2000 года в Белграде начинаются студенческие протесты. Площадь заполняют десятки тысяч человек, и режим Miloševića падает.',
   'The Bulldozer Revolution',
   'On 5 October 2000 student protests begin in Belgrade. Tens of thousands fill the squares and Milošević\'s regime falls.',
   [('Отступить', 'Step back',
     'set_country_flag = SER_bulldozer set_politics = { ruling_party = democratic elections_allowed = yes } '
     'add_popularity = { ideology = democratic popularity = 0.15 } add_stability = 0.05', 1)])
ev('serbia_collapse.63', S('2003.2.3', 'SER_state_union'),
   'Союзная Республика Сербия и Черногория',
   '4 февраля 2003 года Сербия и Черногория подписывают соглашение: вместо Союзной Республики Югославии появляется Союзная Республика Сербия и Черногория.',
   'The State Union of Serbia and Montenegro',
   'On 4 February 2003 Serbia and Montenegro sign an agreement: the Federal Republic of Yugoslavia is replaced by the State Union of Serbia and Montenegro.',
   [('Обновить федерацию', 'Renew the federation',
     'set_country_flag = SER_state_union add_stability = 0.02 add_political_power = 50', 1)])
ev('serbia_collapse.64', S('2009.7.21', 'SER_icj_kosovo'),
   'Решение Международного суда по Косово',
   '22 июля 2009 года Международный суд в Гааге выносит консультативное заключение: одностороннее провозглашение независимости Косово не нарушает международное право.',
   'The ICJ Opinion on Kosovo',
   'On 22 July 2009 the International Court of Justice delivers its advisory opinion: the unilateral declaration of Kosovar independence does not violate international law.',
   [('Не признавать решение', 'Do not accept the ruling',
     'set_country_flag = SER_icj_kosovo add_stability = -0.03 add_war_support = 0.04', 1)])
ev('serbia_collapse.65', S('2010.7.21', 'SER_eu_application'),
   'Заявка в Европейский союз',
   '22 июля 2010 года Сербия подаёт заявку на вступление в ЕС. Брюссель отвечает: сначала диалог с Косово.',
   'The Application to the European Union',
   'On 22 July 2010 Serbia applies for EU membership. Brussels replies: first, a dialogue with Kosovo.',
   [('Подать заявку', 'Submit the application',
     'set_country_flag = SER_eu_application add_ideas = BC_eu_candidate add_stability = 0.03', 1)])
ev('serbia_collapse.66', S('2012.2.28', 'SER_eu_candidate'),
   'Кандидат в члены ЕС',
   '1 марта 2012 года Европейский совет даёт Сербии статус кандидата. Вопрос Косово по-прежнему стоит на пути к членству.',
   'EU Candidate Status',
   'On 1 March 2012 the European Council grants Serbia candidate status. The Kosovo question still blocks the way to membership.',
   [('Продолжать реформы', 'Continue the reforms',
     'set_country_flag = SER_eu_candidate add_ideas = BC_eu_candidate add_stability = 0.03 '
     'add_political_power = 50', 1)])

# triggered-only union events
ev('bc_union.1', None, 'Приглашение из Белграда', 'Белград предлагает нам вступить в союз бывших югославских республик.',
   'An Invitation from Belgrade', 'Belgrade invites us to join an alliance of former Yugoslav republics.',
   [('Вступить', 'Join', 'FROM = { add_to_faction = ROOT } add_stability = 0.03',
     'base = 30 modifier = { factor = 3 has_country_flag = BC_yugoslav_friendly } modifier = { factor = 0 has_country_flag = BC_western }'),
    ('Отказаться', 'Refuse', 'FROM = { create_wargoal = { type = annex_everything target = ROOT } }',
     'base = 50 modifier = { factor = 2 has_country_flag = BC_western }')], hidden_trigger_only=True)
ev('bc_union.2', None, 'Новый союзный договор', 'Нам предлагают войти в состав обновлённой федерации. Это будет конец нашей независимости — или начало новой Югославии.',
   'The New Union Treaty', 'We are offered to join a renewed federation.',
   [('Подписать договор', 'Sign the treaty', 'FROM = { annex_country = { target = ROOT transfer_troops = yes } }',
     'base = 40 modifier = { factor = 3 has_country_flag = BC_yugoslav_friendly } modifier = { factor = 0 has_country_flag = BC_western }'),
    ('Сохранить независимость', 'Keep our independence', 'FROM = { create_wargoal = { type = annex_everything target = ROOT } }',
     'base = 40 modifier = { factor = 2 has_country_flag = BC_western }')], hidden_trigger_only=True)
ev('bc_union.3', None, 'Предложение об объединении', '[From.GetName] предлагает объединиться с нами в одно государство.',
   'A Unification Proposal', '[From.GetName] proposes to unite with us.',
   [('Принять', 'Accept', 'annex_country = { target = FROM transfer_troops = yes } add_stability = 0.05', 'base = 80'),
    ('Отклонить', 'Decline', 'add_political_power = 25', 'base = 20')], hidden_trigger_only=True)
ev('bc_union.4', None, 'Косово просит об объединении', 'Правительство в Приштине предлагает объединить Косово с Албанией.',
   'Kosovo Asks for Union', 'The government in Priština proposes to unite Kosovo with Albania.',
   [('Великая Албания!', 'Greater Albania!', 'annex_country = { target = FROM transfer_troops = yes }', 'base = 50'),
    ('Не сейчас', 'Not now', 'add_political_power = 25', 'base = 50')], hidden_trigger_only=True)


def _load_world_2026_events():
    """The events of the new Serbian government (October 2026 and later)."""
    for e in world_2026.SERBIA_EVENTS:
        opts = []
        for o in e['options']:
            opts.append(o if len(o) == 4 else (o[0], o[1], o[2], 1))
        EVENTS.append(dict(id=e['id'], trigger=e['trigger'], title_ru=e['title_ru'],
                           desc_ru=e['desc_ru'], title_en=e['title_en'], desc_en=e['desc_en'],
                           options=opts, triggered_only=False))


_load_world_2026_events()


def events_file():
    L = ['add_namespace = serbia_collapse', 'add_namespace = bc_union', '']
    for e in EVENTS:
        L += ['country_event = {', f'\tid = {e["id"]}', f'\ttitle = {e["id"]}.t', f'\tdesc = {e["id"]}.d']
        if e['triggered_only']:
            L.append('\tis_triggered_only = yes')
        else:
            L += [f'\ttrigger = {{ {e["trigger"]} }}', '\tmean_time_to_happen = { days = 1 }', '\tfire_only_once = yes']
        for i, (ru, en, eff, ai) in enumerate(e['options']):
            ai_txt = ai if isinstance(ai, str) else f'base = {max(ai, 0) * 100 if ai else 1}'
            L += ['\toption = {', f'\t\tname = {e["id"]}.{"abcd"[i]}', f'\t\tai_chance = {{ {ai_txt} }}', f'\t\t{eff}', '\t}']
        L.append('}')
        L.append('')
    return '\n'.join(L)


# --------------------------------------------------------------------------
# Localisation
# --------------------------------------------------------------------------
def country_name_overrides(lang):
    ru = lang == 'russian'
    d = {}

    def put(tag, name, adj, ideologies=('democratic', 'communism', 'fascism', 'neutrality')):
        for ide in ideologies:
            d[f'{tag}_{ide}'] = name
            d[f'{tag}_{ide}_DEF'] = name
            d[f'{tag}_{ide}_ADJ'] = adj
    names = {
        'SER': ('Сербия', 'сербский', 'Serbia', 'Serbian'),
        'CRO': ('Хорватия', 'хорватский', 'Croatia', 'Croatian'),
        'SLV': ('Словения', 'словенский', 'Slovenia', 'Slovenian'),
        'BOS': ('Босния и Герцеговина', 'боснийский', 'Bosnia and Herzegovina', 'Bosnian'),
        'RSK': ('Республика Сербская', 'боснийско-сербский', 'Republika Srpska', 'Bosnian Serb'),
        'MNT': ('Черногория', 'черногорский', 'Montenegro', 'Montenegrin'),
        'KOS': ('Косово', 'косовский', 'Kosovo', 'Kosovar'),
        'FYR': ('Северная Македония', 'македонский', 'North Macedonia', 'Macedonian'),
        'RKS': ('Республика Српска Краина', 'краинский', 'Republic of Serbian Krajina', 'Krajina Serb'),
        'HZG': ('Хорватская Республика Герцеговина', 'герцеговинский', 'Croatian Republic of Herzeg-Bosnia', 'Herzeg-Bosnian'),
        'SRF': ('Силы быстрой поддержки', 'сил быстрой поддержки', 'Rapid Support Forces', 'RSF'),
        'NUG': ('Национальное единство', 'национального единства', 'National Unity Government', 'NUG'),
    }
    for tag, (rn, ra, en, ea) in names.items():
        n, a = (rn, ra) if ru else (en, ea)
        d[tag], d[f'{tag}_DEF'], d[f'{tag}_ADJ'] = n, n, a
        put(tag, n, a)
    if ru:
        put('SER', 'СФРЮ', 'югославский', ('communism',))
        put('SER', 'Союзная Республика Югославия', 'югославский', ('neutrality',))
        d.update({'SER_YUGOSLAVIA': 'Югославия', 'SER_YUGOSLAVIA_DEF': 'Югославия', 'SER_YUGOSLAVIA_ADJ': 'югославский',
                  'SER_REPUBLIC': 'Сербия', 'SER_REPUBLIC_DEF': 'Республика Сербия', 'SER_REPUBLIC_ADJ': 'сербский'})
    else:
        put('SER', 'SFR Yugoslavia', 'Yugoslav', ('communism',))
        put('SER', 'FR Yugoslavia', 'Yugoslav', ('neutrality',))
        d.update({'SER_YUGOSLAVIA': 'Yugoslavia', 'SER_YUGOSLAVIA_DEF': 'Yugoslavia', 'SER_YUGOSLAVIA_ADJ': 'Yugoslav',
                  'SER_REPUBLIC': 'Serbia', 'SER_REPUBLIC_DEF': 'the Republic of Serbia', 'SER_REPUBLIC_ADJ': 'Serbian'})
    for ide in ('democratic', 'communism', 'fascism', 'neutrality'):
        for cos in ('SER_YUGOSLAVIA', 'SER_REPUBLIC'):
            d[f'{cos}_{ide}'] = d[cos]
            d[f'{cos}_{ide}_DEF'] = d[f'{cos}_DEF']
            d[f'{cos}_{ide}_ADJ'] = d[f'{cos}_ADJ']
    return d


LOC_COMMON = {
    'russian': {
        'BC_1980_NAME': 'Распад Югославии — 1980',
        'BC_1980_DESC': '1 мая 1980 года. Маршал Тито при смерти. Мир разделён холодной войной: СССР и Варшавский договор против США и НАТО. Через десять лет Югославия распадётся — и её придётся собирать заново.',
        'SER_BOOKMARK_HISTORY': 'Социалистическая Федеративная Республика Югославия. После смерти Тито страну ждут долговой кризис, национализм и распад 1991 года. Соберите Югославию снова — силой, новым союзом или через Европу.',
        'SOV_BOOKMARK_HISTORY': 'Эпоха Брежнева. Советские войска в Афганистане, впереди Олимпиада-80.',
        'USA_BOOKMARK_HISTORY': 'Президент Картер, кризис с заложниками в Иране и бойкот Олимпиады.',
        'GER_BOOKMARK_HISTORY': 'Западная Германия Гельмута Шмидта — экономический двигатель Европы.',
        'DDR_BOOKMARK_HISTORY': 'ГДР Эриха Хонеккера за Берлинской стеной.',
        'ENG_BOOKMARK_HISTORY': 'Первый год Маргарет Тэтчер на Даунинг-стрит.',
        'CHI_BOOKMARK_HISTORY': 'Китай начинает реформы и открытость.',
        'SER_TITO_DESC': 'Иосип Броз Тито — маршал, партизан и создатель социалистической Югославии. Умрёт 4 мая 1980 года.',
        'SER_VUCIC_DESC': 'Александр Вучич — в этой альтернативной истории он возглавляет Югославию после смерти Тито.',
        'SER_STUDENTS_DESC': 'Илия Срданович — лидер «Студенческого списка», победившего на выборах 25 октября 2026 года.',
        'CRO_LEADER_DESC': 'Андрей Пленкович — премьер-министр Хорватии в 2026 году.',
        'SLV_LEADER_DESC': 'Янез Янша — премьер-министр Словении в 2026 году.',
        'BOS_LEADER_DESC': 'Борьяна Кришто — председатель Совета министров Боснии и Герцеговины в 2026 году.',
        'RSK_LEADER_DESC': 'Милорад Додик — президент Республики Сербской в 2026 году.',
        'RKS_BABIC_DESC': 'Милан Бабич — первый президент Республки Сербской Краины в 1991-1992 годах.',
        'HZG_BOBAN_DESC': 'Мате Бобан — президент Хорватской Республики Герцеговина.',
        'MNT_LEADER_DESC': 'Милойко Спаич — премьер-министр Черногории в 2026 году.',
        'KOS_LEADER_DESC': 'Альбин Курти — премьер-министр Косово в 2026 году.',
        'FYR_LEADER_DESC': 'Християн Мицкоский — премьер-министр Северной Македонии в 2026 году.',
        'SER_1980_tree': 'Югославия: распад и возрождение',
        'BC_1995_NAME': 'После Дейтона — 1995',
        'BC_1995_DESC': '14 декабря 1995 года. В Париже подписано Дейтонское соглашение: война в Хорватии и осада Сараева закончены, Босния разделена на два энтитета, Сербская Краина стёрта с карты. Югославия не умерла — она продолжает разваливаться. СССР прекратил существование в декабре 1991 года, и пятнадцать его республик стали отдельными государствами.',
        'BC_1995_HISTORY': 'Союзная Республика Югославия: Сербия и Черногория без Косово, под санкциями ООН, в долгой зиме. Босния разделена надвое, бывшая Краина стёрта с карты. Сможете ли вы собрать страну заново — или придётся смириться с её смертью?',
        'BC_2026_NAME': 'Сербия — 2026',
        'BC_2026_DESC': '28 октября 2026 года. Югославии не существует уже больше тридцати лет, а её народы живут по разные стороны границ, которые никто не признал окончательными. Балканы — члены ЕС и НАТО, но Белград снова мечтает о великой державе. В тот же день, когда «Студенческий список» выиграл выборы с результатом в 138 мест из 250, на планете идут четыре войны: на Украине, в Ливане, в Судане и в Мьянме.',
        'BC_2026_HISTORY': 'Республика Сербия без Косово, независимая Черногория, объединённая Босния. «Студенческий список» пришёл к власти не в результате революции, а в результате выборов — и теперь должен решить, что делать с Югославией, которая всё ещё живёт в головах её жителей. За спиной — война на Украине, израильская война в Ливане, гражданская война в Судане и горящий Мьянма. Движуха не заканчивается.',
        'OTHER_GRAND_DESC': 'Остальной мир: холодная война подходит к концу, но её тени останутся на десятилетия.',
    },
    'english': {
        'BC_1980_NAME': 'Breakup of Yugoslavia — 1980',
        'BC_1980_DESC': '1 May 1980. Marshal Tito is dying. The world is divided by the Cold War. In ten years Yugoslavia will collapse — and will have to be rebuilt.',
        'SER_BOOKMARK_HISTORY': 'The Socialist Federal Republic of Yugoslavia. After Tito: debt crisis, nationalism and the 1991 break-up. Rebuild Yugoslavia by force, a new union, or through Europe.',
        'SOV_BOOKMARK_HISTORY': 'The Brezhnev era. Soviet troops in Afghanistan, the 1980 Olympics ahead.',
        'USA_BOOKMARK_HISTORY': 'President Carter, the Iran hostage crisis and the Olympic boycott.',
        'GER_BOOKMARK_HISTORY': "Helmut Schmidt's West Germany — the economic engine of Europe.",
        'DDR_BOOKMARK_HISTORY': "Erich Honecker's GDR behind the Berlin Wall.",
        'ENG_BOOKMARK_HISTORY': "Margaret Thatcher's first year in Downing Street.",
        'CHI_BOOKMARK_HISTORY': 'China begins reform and opening up.',
        'SER_TITO_DESC': 'Josip Broz Tito — marshal, partisan and founder of socialist Yugoslavia. He dies on 4 May 1980.',
        'SER_VUCIC_DESC': 'Aleksandar Vučić — in this alternate history he leads Yugoslavia after Tito.',
        'SER_STUDENTS_DESC': 'Ilija Srdanović — leader of the Student List that won the 25 October 2026 election.',
        'CRO_LEADER_DESC': 'Andrej Plenković, Prime Minister of Croatia in 2026.',
        'SLV_LEADER_DESC': 'Janez Janša, Prime Minister of Slovenia in 2026.',
        'BOS_LEADER_DESC': 'Borjana Krišto, Chair of the Council of Ministers of Bosnia and Herzegovina in 2026.',
        'RSK_LEADER_DESC': 'Milorad Dodik, President of Republika Srpska in 2026.',
        'RKS_BABIC_DESC': 'Milan Babic, the first president of the Republic of Serbian Krajina, 1991-1992.',
        'HZG_BOBAN_DESC': 'Mate Boban, president of the Croatian Republic of Herzeg-Bosnia.',
        'MNT_LEADER_DESC': 'Milojko Spajić, Prime Minister of Montenegro in 2026.',
        'KOS_LEADER_DESC': 'Albin Kurti, Prime Minister of Kosovo in 2026.',
        'FYR_LEADER_DESC': 'Hristijan Mickoski, Prime Minister of North Macedonia in 2026.',
        'SER_1980_tree': 'Yugoslavia: Break-up and Rebirth',
        'BC_1995_NAME': 'After Dayton — 1995',
        'BC_1995_DESC': '14 December 1995. The Dayton Agreement is signed in Paris: the war in Croatia and the siege of Sarajevo are over, Bosnia is split into two entities and the Serbian Krajina has vanished from the map. Yugoslavia did not die - it keeps falling apart. The USSR ceased to exist in December 1991 and its fifteen republics are independent countries.',
        'BC_1995_HISTORY': 'The Federal Republic of Yugoslavia: Serbia and Montenegro without Kosovo, under UN sanctions, in a long winter. Bosnia is divided in two and the former Krajina is gone. Can you still put the country back together - or will you have to accept its death?',
        'BC_2026_NAME': 'Serbia — 2026',
        'BC_2026_DESC': '28 October 2026. Yugoslavia has been gone for more than thirty years and its peoples live on different sides of borders nobody ever accepted. The Balkans are in the EU and NATO, but Belgrade dreams of a great power once more. On the very day the Student List won the election with 138 of the 250 seats, four wars are being fought on this planet: in Ukraine, in Lebanon, in Sudan and in Myanmar.',
        'BC_2026_HISTORY': 'The Republic of Serbia without Kosovo, an independent Montenegro, a united Bosnia. The Student List came to power not through a revolution but through an election - and now it has to decide what to do with the Yugoslavia that still lives in the heads of its people. Behind it: the war in Ukraine, the Israeli war in Lebanon, the civil war in Sudan and burning Myanmar. The action does not stop.',
        'OTHER_GRAND_DESC': 'The rest of the world: the Cold War is coming to an end, but its shadows will remain for decades.',
    },
}


def esc(s):
    return s.replace('"', '\\"')


def all_trees():
    return [serbia_tree()] + [republic_tree(tag, spec) for tag, spec in REPUBLICS.items()]


def localisation(lang):
    ru = lang == 'russian'
    d = dict(LOC_COMMON[lang])
    for t in all_trees():
        for f in t.focuses:
            d[f['id']] = f['ru'] if ru else f['en']
            d[f['id'] + '_desc'] = f['ru_desc'] if ru else f['en'] + '.'
    for k, (rn, en, _) in IDEAS.items():
        d[k] = rn if ru else en
    for e in EVENTS:
        d[e['id'] + '.t'] = e['title_ru'] if ru else e['title_en']
        d[e['id'] + '.d'] = e['desc_ru'] if ru else e['desc_en']
        for i, (o_ru, o_en, _, _) in enumerate(e['options']):
            d[f'{e["id"]}.{"abcd"[i]}'] = o_ru if ru else o_en
    out = [f'l_{lang}:'] + [f' {k}:0 "{esc(v)}"' for k, v in d.items()]
    return '\n'.join(out) + '\n'


# --------------------------------------------------------------------------
def bookmark():
    countries = [('SER', 'communism', 'SER_BOOKMARK_HISTORY', 'BC_tito_cult BC_jna BC_debt_crisis')]
    minors = [('SOV', 'communism'), ('USA', 'democratic'), ('GER', 'democratic'), ('DDR', 'communism'),
              ('ENG', 'democratic'), ('CHI', 'communism')]
    L = ['bookmarks = {', '\tbookmark = {', '\t\tname = "BC_1980_NAME"', '\t\tdesc = "BC_1980_DESC"',
         '\t\tdate = 1980.5.1.12', '\t\tpicture = "GFX_select_date_1980"', '\t\tdefault_country = "SER"',
         '\t\tdefault = yes']
    for tag, ide, hist, ideas in countries:
        L += [f'\t\t"{tag}" = {{', f'\t\t\thistory = "{hist}"', f'\t\t\tideology = {ide}', f'\t\t\tideas = {{ {ideas} }}',
              '\t\t\tfocuses = { SER_tito_legacy SER_path_force SER_path_federation SER_path_europe SER_restore_yugoslavia }', '\t\t}']
    L.append('\t\t"---"= {')
    L.append('\t\t\thistory = "OTHER_GRAND_DESC"')
    L.append('\t\t}')
    for tag, ide in minors:
        L += [f'\t\t"{tag}" = {{', '\t\t\tminor = yes', f'\t\t\thistory = "{tag}_BOOKMARK_HISTORY"', f'\t\t\tideology = {ide}',
              '\t\t\tideas = { }', '\t\t\tfocuses = { }', '\t\t}']
    L += ['\t\teffect = {', '\t\t\trandomize_weather = 19800501']
    for tag in sorted(world_2026.MODERN_2026):
        L.append(f'\t\t\tevery_state = {{ limit = {{ is_core_of = {tag} }} remove_core_of = {tag} }}')
    L += ['\t\t}', '\t}', '}']
    return '\n'.join(L) + '\n'


GFX = """spriteTypes = {
	spriteType = {
		name = "GFX_select_date_1980"
		texturefile = "gfx/interface/bc_bookmark_1980.dds"
	}
	spriteType = {
		name = "GFX_BC_SERBIA_BACKGROUND"
		texturefile = "gfx/interface/illustrations/bc_serbia_background.dds"
	}
}
"""


def descriptor(path=None):
    L = ['name="Балканы 1980: распад Югославии"', 'version="3.4"', 'supported_version="1.*"',
         'tags={', '\t"Alternative History"', '\t"Historical"', '\t"Map"', '\t"National Focuses"', '\t"Events"', '}',
         'picture="thumbnail.png"']
    for p in ['history/states', 'history/countries', 'history/units', 'history/general', 'map/strategicregions',
              'map/supplyareas', 'common/bookmarks', 'gfx/loadingscreens',
              'common/units', 'common/units/equipment', 'common/units/equipment/upgrades',
              'common/units/names_divisions', 'common/units/names_ships', 'common/units/codenames_operatives',
              'common/technologies', 'common/special_projects', 'common/special_projects/project_tags',
              'common/special_projects/projects', 'common/doctrines', 'common/equipment_groups',
              'common/technology_tags', 'common/technology_sharing', 'common/ai_equipment',
              'common/ai_templates', 'common/countries']:
        L.append(f'replace_path="{p}"')
    if path:
        L.append(f'path="{path}"')
    return '\n'.join(L) + '\n'


def write(path, text, bom=False):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8-sig' if bom else 'utf-8', newline='\n') as f:
        f.write(text)


def build(out, old_mod, states, capitals):
    old = os.path.join(old_mod, 'Balkan_Collapse')
    for t in all_trees():
        write(os.path.join(out, 'common', 'national_focus', f'bc_{t.tag.lower()}_focus.txt'), t.render())
    write(os.path.join(out, 'common', 'ideas', 'bc_ideas.txt'), ideas_file())
    write(os.path.join(out, 'events', 'bc_yugoslavia.txt'), events_file())
    write(os.path.join(out, 'common', 'bookmarks', 'bc_1980.txt'), bookmark())
    write(os.path.join(out, 'interface', 'bc_balkan.gfx'), GFX)
    for name, text in EXTRA_OOB.items():
        write(os.path.join(out, 'history', 'units', f'{name}.txt'), text)
    for name, text in list(AIR_OOB.items()) + list(NAVAL_OOB.items()):
        write(os.path.join(out, 'history', 'units', f'{name}.txt'), text)
    for lang in ('russian', 'english'):
        write(os.path.join(out, 'localisation', lang, f'bc_balkan_l_{lang}.yml'), localisation(lang), bom=True)
    # pictures from the previous version
    os.makedirs(os.path.join(out, 'gfx', 'loadingscreens'), exist_ok=True)
    for i in range(1, 6):
        shutil.copy2(os.path.join(old, 'gfx', 'loadingscreens', f'load_{i}.dds'),
                     os.path.join(out, 'gfx', 'loadingscreens', f'load_{i}.dds'))
    os.makedirs(os.path.join(out, 'gfx', 'interface', 'illustrations'), exist_ok=True)
    shutil.copy2(os.path.join(old, 'gfx', 'loadingscreens', 'load_1.dds'), os.path.join(out, 'gfx', 'interface', 'bc_bookmark_1980.dds'))
    shutil.copy2(os.path.join(old, 'gfx', 'interface', 'illustrations', 'bc_serbia_background.dds'),
                 os.path.join(out, 'gfx', 'interface', 'illustrations', 'bc_serbia_background.dds'))
    shutil.copy2(os.path.join(old, 'thumbnail.png'), os.path.join(out, 'thumbnail.png'))
    # cosmetic flags
    fl = os.path.join(out, 'gfx', 'flags')
    for sub in ('', 'medium', 'small'):
        src = os.path.join(fl, sub, 'SER_communism.tga')
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(fl, sub, 'SER_YUGOSLAVIA.tga'))
        src = os.path.join(fl, sub, 'SER_democratic.tga')
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(fl, sub, 'SER_REPUBLIC.tga'))
    write(os.path.join(out, 'descriptor.mod'), descriptor())
