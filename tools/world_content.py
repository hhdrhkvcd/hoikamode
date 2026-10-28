# -*- coding: utf-8 -*-
"""World content for the "Balkans 1980" mod.

* three scenarios (bookmarks): 1 May 1980 / 1 January 1995 / 1 January 2026
* the dissolution of the USSR (26 December 1991) exactly as it happened
* leader portraits (real politicians) taken from the Millennium Dawn art
* a focus tree for every country in the game (so nothing is left without one)

Leader portraits and focus icons come from Millennium Dawn (CC BY-SA 4.0).
"""
import os
import re
import shutil

# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------


def norm(s):
    import unicodedata
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]', '', s.lower())


def find_portrait(md_leaders_dir, tag, patterns):
    """Return the file name of the first portrait in gfx/leaders/<tag> matching a pattern."""
    d = os.path.join(md_leaders_dir, tag)
    if not os.path.isdir(d):
        return None
    files = sorted(f for f in os.listdir(d) if f.lower().endswith('.dds'))
    for p in patterns:
        n = norm(p)
        for f in files:
            if n in norm(f):
                return f
    return None


# portraits of the leaders of 1980 (Millennium Dawn has only a part of them)
PORTRAITS_1980 = {
    'CUB': ['fidel_castro'],
    'NIC': ['daniel_ortega'],
    'ZIM': ['robert_mugabe'],
    'SYR': ['hafez_al_assaad', 'hafez'],
    'IRQ': ['saddam_hussein'],
    'LBA': ['muammar_al_gaddafi'],
    'ALB': ['enver_hoxha'],
}

# --------------------------------------------------------------------------
# Leaders of the scenarios
#   tag -> (name, ideology, [portrait patterns], description)
# --------------------------------------------------------------------------
SOV_LEADERS_1980 = ('Леонид Брежнев', 'leninism', ['brezhnev'], 'SOV_BREZHNEV_DESC')

LEADERS_1995 = {
    # Yugoslavia after the Dayton accords
    'SER': ('Slobodan Milošević', 'despotism', ['milosevic'], 'SER_MILOSEVIC_DESC'),
    'CRO': ('Franjo Tuđman', 'despotism', ['tudjman'], 'CRO_TUDJMAN_DESC'),
    'SLV': ('Milan Kučan', 'centrism', ['kucan'], 'SLV_KUCAN_DESC'),
    'BOS': ('Alija Izetbegović', 'centrism', ['izetbegovic'], 'BOS_IZETBEGOVIC_DESC'),
    'RSK': ('Radovan Karadžić', 'despotism', ['karadzic'], 'RSK_KARADZIC_DESC'),
    'MNT': ('Momir Bulatović', 'despotism', ['bulatovic'], 'MNT_BULATOVIC_DESC'),
    'KOS': ('Ibrahim Rugova', 'centrism', ['rugova'], 'KOS_RUGOVA_DESC'),
    'FYR': ('Kiro Gligorov', 'centrism', ['gligorov'], 'FYR_GLIGOROV_DESC'),
    # former USSR
    'SOV': ('Boris Yeltsin', 'conservatism', ['yeltsin'], 'SOV_YELTSIN_DESC'),
    'UKR': ('Leonid Kuchma', 'conservatism', ['leonid_kuchma', 'kuchma'], 'UKR_KUCHMA_DESC'),
    'BLR': ('Alexander Lukashenko', 'despotism', ['alexander_lukashenko', 'lukashenko'], 'BLR_LUKASHENKO_DESC'),
    'MLV': ('Mircea Snegur', 'centrism', ['snegur'], 'MLV_SNEGUR_DESC'),
    'GEO': ('Zviad Gamsakhurdia', 'national_socialism', ['gamsakhurdia'], 'GEO_GAMSAKHURDIA_DESC'),
    'ARM': ('Levon Ter-Petrosyan', 'liberalism', ['ter_petrosyan', 'terpetrosyan'], 'ARM_TERPETROSYAN_DESC'),
    'AZE': ('Ayaz Mutallibov', 'socialism', ['mutallibov'], 'AZE_MUTALLIBOV_DESC'),
    'KAZ': ('Nursultan Nazarbayev', 'despotism', ['nazarbayev', 'nazabayev'], 'KAZ_NAZARBAYEV_DESC'),
    'UZB': ('Islam Karimov', 'despotism', ['karimov'], 'UZB_KARIMOV_DESC'),
    'TRK': ('Saparmurat Niyazov', 'despotism', ['niyazov'], 'TRK_NIYAZOV_DESC'),
    'KYR': ('Askar Akayev', 'liberalism', ['akayev'], 'KYR_AKAYEV_DESC'),
    'TAJ': ('Emomali Rahmon', 'despotism', ['rahmon'], 'TAJ_RAHMON_DESC'),
    'EST': ('Arnold Rüütel', 'centrism', ['ruutel'], 'EST_RUUTEL_DESC'),
    'LAT': ('Anatolijs Gorbunovs', 'centrism', ['gorbunovs'], 'LAT_GORBUNOVS_DESC'),
    'LIT': ('Vytautas Landsbergis', 'centrism', ['landsbergis'], 'LIT_LANDSBERGIS_DESC'),
    # great powers
    'USA': ('Bill Clinton', 'liberalism', ['bill_clinton'], 'USA_CLINTON_DESC'),
    'ENG': ('John Major', 'conservatism', ['major'], 'ENG_MAJOR_DESC'),
    'FRA': ('François Mitterrand', 'socialism', ['mitterrand'], 'FRA_MITTERRAND_DESC'),
    'GER': ('Helmut Kohl', 'centrism', ['kohl'], 'GER_KOHL_DESC'),
    'ITA': ('Silvio Berlusconi', 'liberalism', ['berlusconi'], 'ITA_BERLUSCONI_DESC'),
    'CHN': ('Jiang Zemin', 'leninism', ['jiang'], 'CHN_JIANG_DESC'),
    'JPN': ('Tomichi Murayama', 'centrism', ['murayama'], 'JPN_MURAYAMA_DESC'),
    'ESP': ('Felipe González', 'socialism', ['gonzalez'], 'ESP_GONZALEZ_DESC'),
    'TUR': ('Tansu Çiller', 'liberalism', ['ciller'], 'TUR_CILLER_DESC'),
}

# the leaders of the Soviet republics on the day the USSR collapsed (26 December 1991)
LEADERS_1991 = dict(LEADERS_1995)
LEADERS_1991.update({
    'UKR': ('Leonid Kravchuk', 'conservatism', ['kravchuk'], 'UKR_KRAVCHUK_DESC'),
    'BLR': ('Stanislav Shushkevich', 'liberalism', ['shushkevich'], 'BLR_SHUSHKEVICH_DESC'),
})

LEADERS_2026 = {
    'SER': ('Aleksandar Vučić', 'despotism', ['vucic'], 'SER_VUCIC_DESC'),
    'CRO': ('Andrej Plenković', 'conservatism', ['plenkovic'], 'CRO_PLENKOVIC_DESC'),
    'SLV': ('Janez Janša', 'conservatism', ['jansa'], 'SLV_JANSA_DESC'),
    'BOS': ('Borjana Krišto', 'conservatism', ['kristo'], 'BOS_KRISTO_DESC'),
    'MNT': ('Milojko Spajić', 'liberalism', ['spajic'], 'MNT_SPAJIC_DESC'),
    'KOS': ('Albin Kurti', 'socialism', ['kurti'], 'KOS_KURTI_DESC'),
    'FYR': ('Hristijan Mickoski', 'conservatism', ['mickoski'], 'FYR_MICKOSKI_DESC'),
    'SOV': ('Vladimir Putin', 'despotism', ['putin'], 'SOV_PUTIN_DESC'),
    'UKR': ('Volodymyr Zelensky', 'liberalism', ['zelensky'], 'UKR_ZELENSKY_DESC'),
    'BLR': ('Alexander Lukashenko', 'despotism', ['lukashenko'], 'BLR_LUKASHENKO_DESC'),
    'MLV': ('Maia Sandu', 'liberalism', ['sandu'], 'MLV_SANDU_DESC'),
    'GEO': ('Mikheil Kavelashvili', 'centrism', ['kavelashvili'], 'GEO_KAVELASHVILI_DESC'),
    'ARM': ('Vahagn Khachaturyan', 'centrism', ['khachaturyan'], 'ARM_KHACHATURYAN_DESC'),
    'AZE': ('Ilham Aliyev', 'despotism', ['aliyev'], 'AZE_ALIYEV_DESC'),
    'KAZ': ('Kassym-Jomart Tokayev', 'centrism', ['tokayev'], 'KAZ_TOKAYEV_DESC'),
    'UZB': ('Shavkat Mirziyoyev', 'centrism', ['mirziyoyev'], 'UZB_MIRZIYOYEV_DESC'),
    'TRK': ('Serdar Berdimuhamedow', 'despotism', ['berdimuhamed'], 'TRK_BERDIMUHAMED_DESC'),
    'TAJ': ('Emomali Rahmon', 'despotism', ['rahmon'], 'TAJ_RAHMON_DESC'),
    'EST': ('Kristiina Ounasoo', 'liberalism', ['ounasoo'], 'EST_OUNASOO_DESC'),
    'LAT': ('Evika Siliņa', 'socialism', ['silina'], 'LAT_SILINA_DESC'),
    'LIT': ('Gitanas Nausėda', 'centrism', ['nauseda'], 'LIT_NAUSEDA_DESC'),
    'USA': ('Donald Trump', 'despotism', ['trump'], 'USA_TRUMP_DESC'),
    'ENG': ('Keir Starmer', 'socialism', ['starmer'], 'ENG_STARMER_DESC'),
    'FRA': ('Emmanuel Macron', 'liberalism', ['macron'], 'FRA_MACRON_DESC'),
    'GER': ('Friedrich Merz', 'conservatism', ['merz'], 'GER_MERZ_DESC'),
    'ITA': ('Giorgia Meloni', 'despotism', ['meloni'], 'ITA_MELONI_DESC'),
    'CHN': ('Xi Jinping', 'leninism', ['jinping'], 'CHN_XI_DESC'),
    'JPN': ('Sanae Takaichi', 'conservatism', ['takaichi'], 'JPN_TAKAICHI_DESC'),
    'ESP': ('Pedro Sánchez', 'socialism', ['sanchez'], 'ESP_SANCHEZ_DESC'),
    'TUR': ('Recep Tayyip Erdoğan', 'despotism', ['erdogan'], 'TUR_ERDOGAN_DESC'),
    'POL': ('Donald Tusk', 'liberalism', ['tusk'], 'POL_TUSK_DESC'),
}

# --------------------------------------------------------------------------
# Successor states of the USSR (15 republics, 26 December 1991)
#   tag -> (country name ru/en, leader key, list of MD parent tags to fold in)
# --------------------------------------------------------------------------
SOV_SUCCESSORS = {
    'UKR': ('Украина', 'Ukraine', 'UKR_KRAVCHUK_DESC'),
    'BLR': ('Беларусь', 'Belarus', 'BLR_SHUSHKEVICH_DESC'),
    'MLV': ('Молдова', 'Moldova', 'MLV_SNEGUR_DESC'),
    'GEO': ('Грузия', 'Georgia', 'GEO_GAMSAKHURDIA_DESC'),
    'ARM': ('Армения', 'Armenia', 'ARM_TERPETROSYAN_DESC'),
    'AZE': ('Азербайджан', 'Azerbaijan', 'AZE_MUTALLIBOV_DESC'),
    'KAZ': ('Казахстан', 'Kazakhstan', 'KAZ_NAZARBAYEV_DESC'),
    'KYR': ('Киргизия', 'Kyrgyzstan', 'KYR_AKAYEV_DESC'),
    'UZB': ('Узбекистан', 'Uzbekistan', 'UZB_KARIMOV_DESC'),
    'TRK': ('Туркменистан', 'Turkmenistan', 'TRK_NIYAZOV_DESC'),
    'TAJ': ('Таджикистан', 'Tajikistan', 'TAJ_RAHMON_DESC'),
    'EST': ('Эстония', 'Estonia', 'EST_RUUTEL_DESC'),
    'LAT': ('Латвия', 'Latvia', 'LAT_GORBUNOVS_DESC'),
    'LIT': ('Литва', 'Lithuania', 'LIT_LANDSBERGIS_DESC'),
}

# autonomous regions that in 2026 belong to their mother country
FOLD_2026 = {
    'CRM': 'UKR', 'DPR': 'UKR', 'LPR': 'UKR',   # Crimea and the Donbas
    'CHE': 'SOV',                              # Chechnya
    'ABK': 'GEO', 'SOO': 'GEO',                # Abkhazia, South Ossetia
    'PMR': 'MLV',                              # Transnistria
    'NKR': 'AZE',                              # Nagorno-Karabakh (under Azerbaijan since 2023)
}

# --------------------------------------------------------------------------
# Focus icons: Millennium Dawn country art (copied into the mod)
# --------------------------------------------------------------------------
ICON_FOLDERS = {
    'SER': 'serbia', 'CRO': 'croatia', 'BOS': 'Bosnia', 'RSK': 'Bosnia',
    'MNT': 'montenegro', 'FYR': 'macedonia', 'SOV': 'russia', 'UKR': 'ukraine',
    'GEO': 'georgia', 'ARM': 'armenia', 'AZE': 'azerbaijan', 'MLV': 'moldova',
    'TAJ': 'tajikistan', 'TRK': 'turkmenistan', 'ALB': 'albania',
}

# vanilla HOI4 icons that are safe to use in the generic trees
VANILLA_ICONS = [
    'GFX_focus_generic_military_academy', 'GFX_focus_generic_university_1',
    'GFX_focus_generic_industry_2', 'GFX_focus_generic_court',
    'GFX_focus_generic_improve_the_administration', 'GFX_focus_generic_construct_mil_factory',
    'GFX_focus_generic_adriatic_sea_focus', 'GFX_focus_generic_allies_build_infantry',
    'GFX_focus_generic_defence', 'GFX_goal_generic_position_armies',
    'GFX_goal_support_democracy', 'GFX_goal_generic_propaganda', 'GFX_goal_generic_trade',
    'GFX_goal_generic_production', 'GFX_goal_generic_construct_civ_factory',
    'GFX_goal_generic_construct_naval_dockyard', 'GFX_goal_generic_construct_infrastructure',
    'GFX_goal_generic_small_arms', 'GFX_goal_generic_army_doctrines',
    'GFX_goal_generic_alliance', 'GFX_goal_generic_demand_territory',
    'GFX_goal_generic_mining_industry',
]


# --------------------------------------------------------------------------
# generic focus tree for every country without a hand written one
# --------------------------------------------------------------------------
GENERIC_FOCUSES = [
    ('stability', 'GFX_focus_generic_improve_the_administration', 4, 0,
     'Порядок и стабильность', 'Укрепление государственных институтов.', 'Order and Stability'),
    ('economy', 'GFX_goal_generic_production', 4, 1,
     'Экономическая модернизация', 'Рыночные реформы и новые заводы.', 'Economic Modernisation',
     'add_ideas = BC_generic_industry'),
    ('infrastructure', 'GFX_goal_generic_construct_infrastructure', 4, 2,
     'Инфраструктура', 'Дороги, порты и энергетика.', 'Infrastructure',
     'add_ideas = BC_generic_infra'),
    ('education', 'GFX_focus_generic_university_1', 4, 3,
     'Образование и наука', 'Новые университеты и исследовательские центры.', 'Education and Science',
     'add_research_slot = 1'),
    ('diplomacy', 'GFX_goal_support_democracy', 2, 1,
     'Дипломатический курс', 'Место страны в мире.', 'Foreign Policy',
     'add_political_power = 100'),
    ('alliance', 'GFX_goal_generic_alliance', 2, 2,
     'Блок и союзники', 'Поиск союзников и военных договоров.', 'Bloc and Allies',
     'add_ideas = BC_generic_diplomacy'),
    ('expansion', 'GFX_goal_generic_demand_territory', 2, 3,
     'Территориальные требования', 'Наши соседи не готовы признать наши границы.', 'Territorial Claims',
     'add_war_support = 0.05'),
    ('military', 'GFX_focus_generic_military_academy', 6, 1,
     'Военная реформа', 'Новая армия, новые офицеры.', 'Military Reform',
     'add_ideas = BC_generic_army'),
    ('arms', 'GFX_goal_generic_construct_mil_factory', 6, 2,
     'Оборонная промышленность', 'Собственное производство вооружений.', 'Defence Industry',
     'add_ideas = BC_generic_arms'),
    ('doctrine', 'GFX_goal_generic_army_doctrines', 6, 3,
     'Военная доктрина', 'Как воевать в XXI веке.', 'Military Doctrine',
     'army_experience = 20'),
    ('industry', 'GFX_goal_generic_construct_civ_factory', 4, 4,
     'Новая индустриализация', 'Тяжёлая промышленность и экспорт.', 'New Industrialisation',
     'add_ideas = BC_generic_industry'),
    ('trade', 'GFX_goal_generic_trade', 4, 5,
     'Открытые рынки', 'Выход на мировые рынки.', 'Open Markets',
     'add_ideas = BC_generic_trade'),
]


def generic_tree(tag, tree_id):
    """A compact, country specific focus tree (used for every country without its own)."""
    L = ['focus_tree = {', f'\tid = {tree_id}', '\tcountry = {', '\t\tfactor = 0',
         f'\t\tmodifier = {{ add = 10 tag = {tag} original_tag = {tag} }}', '\t}', '\tdefault = no',
         '\tcontinuous_focus_position = { x = 50 y = 900 }']
    p = f'BC_GEN_{tag}_'
    for i, spec in enumerate(GENERIC_FOCUSES):
        fid, icon, x, y = spec[0], spec[1], spec[2], spec[3]
        ru, ru_desc, en = spec[4], spec[5], spec[6]
        reward = spec[7] if len(spec) > 7 else 'add_political_power = 50'
        pre = []
        if fid == 'economy':
            pre = [p + 'stability']
        elif fid == 'infrastructure':
            pre = [p + 'economy']
        elif fid == 'education':
            pre = [p + 'infrastructure']
        elif fid == 'industry':
            pre = [p + 'education']
        elif fid == 'trade':
            pre = [p + 'industry']
        elif fid == 'diplomacy':
            pre = [p + 'stability']
        elif fid == 'alliance':
            pre = [p + 'diplomacy']
        elif fid == 'expansion':
            pre = [p + 'diplomacy']
        elif fid == 'military':
            pre = [p + 'stability']
        elif fid == 'arms':
            pre = [p + 'military']
        elif fid == 'doctrine':
            pre = [p + 'arms']
        L += ['\tfocus = {', f'\t\tid = {p + fid}', f'\t\ticon = {icon}', f'\t\tx = {x}', f'\t\ty = {y}',
              '\t\tcost = 7']
        if pre:
            L.append('\t\tprerequisite = { ' + ' '.join('focus = ' + q for q in pre) + ' }')
        L.append('\t\tsearch_filters = { FOCUS_FILTER_POLITICAL }')
        L.append('\t\tai_will_do = { factor = 1 }')
        L.append(f'\t\tcompletion_reward = {{ {reward} }}')
        L.append('\t}')
    L.append('}')
    return '\n'.join(L) + '\n'


def generic_loc(tag, name, lang='russian'):
    """Localisation for the generic tree."""
    ru = lang == 'russian'
    d = {}
    p = f'BC_GEN_{tag}_'
    for spec in GENERIC_FOCUSES:
        fid = spec[0]
        d[p + fid] = spec[4] if ru else spec[6]
        d[p + fid + '_desc'] = spec[5] if ru else spec[6] + '.'
    d[f'BC_GEN_{tag}_tree'] = (f'{name}: \u0433\u043e\u0441\u0443\u0434\u0430\u0440\u0441\u0442\u0432\u0435\u043d\u043d\u044b\u0439 \u043a\u0443\u0440\u0441'
                               if ru else f'{name}: State Course')
    return d


# --------------------------------------------------------------------------
# Bookmark (scenario) helpers
# --------------------------------------------------------------------------
def leader_effect(tag, name, ideology, picture=None, desc=None):
    """create_country_leader block (plus the killing of the previous leader)."""
    pic = f'\n\t\tpicture = "{picture}"' if picture else ''
    return (f'{tag} = {{ '
            f'kill_country_leader = yes '
            f'create_country_leader = {{ name = "{name}"{pic} desc = "{desc or (name + " - ")}" '
            f'ideology = {ideology} traits = {{ }} }} '
            f'set_politics = {{ ruling_party = {"communism" if ideology in ("leninism", "stalinism", "marxism", "ultra_leninism", "revisionism", "anti_revisionism") else ("democratic" if ideology in ("liberalism", "conservatism", "socialism", "centrism") else "neutrality")} }} '
            f'}}')


def release_effect(tag, keep_core_of=None, add_claim=None):
    """Release a country from the current scope and clean up the old cores."""
    out = [f'release = {tag}']
    out.append(f'every_state = {{ limit = {{ is_core_of = {tag} }} remove_core_of = SER add_claim_by = SER }}')
    return ' '.join(out)


def sov_dissolve_effect(states_by_owner, leaders, md_owner_of):
    """Effect that dissolves the USSR on 26 December 1991.

    states_by_owner: {tag: [state ids]} - MD owner of every state
    md_owner_of:     {state id: original MD owner}
    """
    L = []
    for tag, (ru, en, desc) in SOV_SUCCESSORS.items():
        ids = [sid for sid, o in md_owner_of.items() if o == tag]
        if not ids:
            continue
        L.append(f'release = {tag}')
        L.append(f'every_state = {{ limit = {{ is_core_of = {tag} }} remove_core_of = SOV }}')
        L.append(f'{tag} = {{ set_country_flag = BC_SOVIET_SUCCESSOR '
                 f'set_stability = 0.45 set_war_support = 0.2 '
                 f'set_research_slots = 3 '
                 f'set_politics = {{ ruling_party = democratic last_election = "1991.12.1" election_frequency = 48 elections_allowed = yes }} '
                 f'set_popularities = {{ democratic = 55 fascism = 5 communism = 20 neutrality = 20 }} '
                 f'add_ideas = BC_post_soviet }}')
        spec = leaders.get(tag)
        if spec:
            name, ide, patterns, dkey = spec
            L.append(f'\t{tag} = {{ kill_country_leader = yes create_country_leader = {{ name = "{name}" '
                     f'desc = "{dkey}" ideology = {ide} traits = {{ }} }} }}')
    return ' '.join(L)


# --------------------------------------------------------------------------
# copying of the Millennium Dawn art
# --------------------------------------------------------------------------
def surname(name):
    """Last part of the name - used to match a portrait file to a leader."""
    parts = [p for p in re.split(r'[\s-]+', name.strip()) if p]
    return parts[-1] if parts else name


def extra_portrait_dir(root, tag):
    return os.path.join(root, 'assets', 'extra_portraits', tag)


def find_extra_portrait(root, tag, name):
    """Portrait that the user dropped into assets/extra_portraits/<TAG>/.

    The file name has to contain the surname of the leader
    (Tudjman.dds -> Franjo Tudjman). If the folder holds exactly one
    picture and the name does not match, that picture is used as well.
    """
    d = extra_portrait_dir(root, tag)
    if not os.path.isdir(d):
        return None
    files = sorted(f for f in os.listdir(d) if f.lower().endswith('.dds'))
    if not files:
        return None
    want = norm(surname(name))
    for f in files:
        if want and want in norm(f):
            return f
    if len(files) == 1:
        return files[0]
    return None


def copy_portraits(md_repo, out, leaders, extra_tags=()):
    """Copy the leader portraits into the mod. Returns {tag: file name}."""
    src_root = os.path.join(md_repo, 'gfx', 'leaders')
    result = {}
    for tag, spec in leaders.items():
        name, ide, patterns, dkey = spec
        f = find_portrait(src_root, tag, patterns)
        if f:
            dst_dir = os.path.join(out, 'gfx', 'leaders', tag)
            os.makedirs(dst_dir, exist_ok=True)
            shutil.copy2(os.path.join(src_root, tag, f), os.path.join(dst_dir, f))
            result[tag] = f
    return result


def copy_focus_icons(md_repo, out, tags):
    """Copy the Millennium Dawn country focus art. Returns {tag: [file names]}."""
    src_root = os.path.join(md_repo, 'gfx', 'interface', 'goals')
    result = {}
    for tag in tags:
        folder = ICON_FOLDERS.get(tag)
        if not folder:
            continue
        d = os.path.join(src_root, folder)
        if not os.path.isdir(d):
            continue
        files = sorted(f for f in os.listdir(d) if f.lower().endswith('.dds'))[:12]
        if not files:
            continue
        dst = os.path.join(out, 'gfx', 'interface', 'goals', f'bc_{tag}')
        os.makedirs(dst, exist_ok=True)
        for f in files:
            shutil.copy2(os.path.join(d, f), os.path.join(dst, f))
        result[tag] = files
    return result


# --------------------------------------------------------------------------
# Bookmarks (the three scenarios)
# --------------------------------------------------------------------------
BOOKMARK_PICTURES = {
    'bc_1980': ('GFX_select_date_1980', 'bc_bookmark_1980.dds'),
    'bc_1995': ('GFX_select_date_1995', 'bc_bookmark_1995.dds'),
    'bc_2026': ('GFX_select_date_2026', 'bc_bookmark_2026.dds'),
}

# which Yugoslav republics are independent in which scenario
YUGO_INDEPENDENT = {
    'bc_1980': [],
    'bc_1995': ['RSK', 'BOS', 'CRO', 'SLV', 'FYR'],
    'bc_2026': ['BOS', 'CRO', 'SLV', 'FYR', 'MNT', 'KOS'],
}
# order matters: Republika Srpska leaves first, Bosnia takes the rest
RELEASE_ORDER = ['RSK', 'BOS', 'CRO', 'SLV', 'FYR', 'MNT', 'KOS']

BAL_2026_IDEAS = 'remove_ideas = BC_tito_cult remove_ideas = BC_jna add_ideas = BC_yugoslav_rebirth'


def _leader_block(tag, spec, portraits):
    name, ide, patterns, dkey = spec
    pic = portraits.get(tag)
    pic_txt = f' picture = "{pic}"' if pic else ''
    return (f'{tag} = {{ kill_country_leader = yes '
            f'create_country_leader = {{ name = "{name}"{pic_txt} desc = "{dkey}" '
            f'ideology = {ide} traits = {{ }} }} }}')


def _dissolve_sov(md_owner_of, leaders, portraits):
    """The 26 December 1991 collapse of the USSR."""
    L = []
    for tag in SOV_SUCCESSORS:
        ids = [sid for sid, o in md_owner_of.items() if o == tag]
        if not ids:
            continue
        L.append(f'release = {tag}')
        L.append(f'every_state = {{ limit = {{ is_core_of = {tag} }} remove_core_of = SOV }}')
        L.append(f'{tag} = {{ set_country_flag = BC_SOVIET_SUCCESSOR set_stability = 0.45 set_war_support = 0.2 '
                 f'set_research_slots = 3 set_popularities = {{ democratic = 55 fascism = 5 communism = 20 neutrality = 20 }} '
                 f'add_ideas = BC_post_soviet }}')
        spec = leaders.get(tag)
        if spec:
            L.append(_leader_block(tag, spec, portraits))
    return ' '.join(L)


def _fold_autonomous(md_owner_of, mapping):
    """Autonomous republics back into their mother country (real 2026 borders)."""
    L = []
    for child, parent in mapping.items():
        ids = [sid for sid, o in md_owner_of.items() if o == child]
        if not ids:
            continue
        tr = ' '.join(f'transfer_state = {sid}' for sid in ids)
        L.append(f'{parent} = {{ {tr} }}')
        L.append(f'every_state = {{ limit = {{ is_core_of = {child} }} remove_core_of = {child} }}')
    return ' '.join(L)


def sov_dissolve(md_owner_of, leaders, portraits):
    """Public wrapper: the effect that dissolves the USSR."""
    diss = _dissolve_sov(md_owner_of, leaders, portraits)
    gov = portraits.get('SOV_GORBACHEV')
    lead = ('SOV = { kill_country_leader = yes create_country_leader = { name = "Mikhail Gorbachev"'
            + (f' picture = "{gov}"' if gov else '') +
            ' desc = "SOV_GORBACHEV_DESC" ideology = leninism traits = { } } } ')
    return lead + diss


def scenario_effects(scn, md_owner_of, leaders, portraits):
    """The effect block of one scenario."""
    L = []
    if scn != 'bc_1980':
        yugo = []
        for tag in RELEASE_ORDER:
            if tag not in YUGO_INDEPENDENT[scn]:
                continue
            yugo.append(f'release = {tag}')
            yugo.append(f'every_state = {{ limit = {{ is_core_of = {tag} }} remove_core_of = SER add_claim_by = SER }}')
            if tag == 'BOS' and scn == 'bc_2026':
                yugo.append('every_state = { limit = { is_core_of = RSK } remove_core_of = RSK }')
        if yugo:
            L.append('SER = { ' + ' '.join(yugo) + ' }')
        L.append('SOV = { ' + _dissolve_sov(md_owner_of, leaders, portraits) + ' }')
        if scn == 'bc_2026':
            L.append(_fold_autonomous(md_owner_of, FOLD_2026))
    # leaders of the scenario
    for tag in sorted(leaders):
        L.append(_leader_block(tag, leaders[tag], portraits))
    if scn in ('bc_1995', 'bc_2026'):
        L.append('SER = { set_country_flag = SER_tito_dead set_country_flag = SER_first_breakup_wave '
                 'set_country_flag = SER_fry_formed }')
    if scn == 'bc_1995':
        L.append('SER = { remove_ideas = BC_tito_cult add_ideas = BC_war_footing BC_ethnic_tensions '
                 'set_stability = 0.35 set_war_support = 0.65 '
                 'set_politics = { ruling_party = neutrality last_election = "1994.12.1" election_frequency = 48 '
                 'elections_allowed = yes } '
                 'set_popularities = { democratic = 25 fascism = 20 communism = 25 neutrality = 30 } }')
        L.append('KOS = { add_ideas = BC_ethnic_tensions }')
        L.append('RSK = { set_stability = 0.3 set_war_support = 0.6 }')
    if scn == 'bc_2026':
        L.append('SER = { ' + BAL_2026_IDEAS + ' set_stability = 0.55 set_war_support = 0.25 '
                 'set_politics = { ruling_party = neutrality last_election = "2024.1.1" election_frequency = 48 '
                 'elections_allowed = yes } '
                 'set_popularities = { democratic = 35 fascism = 10 communism = 15 neutrality = 40 } }')
        L.append('CRO = { set_stability = 0.6 }')
        L.append('SLV = { set_stability = 0.65 }')
        L.append('BOS = { set_stability = 0.45 }')
        L.append('MNT = { set_stability = 0.6 }')
        L.append('KOS = { set_stability = 0.45 }')
        L.append('FYR = { set_stability = 0.55 }')
    return ' '.join(L)


def bookmark_block(scn, date, name_key, desc_key, hist_key, ideology, focuses, effect, default=False):
    L = ['\tbookmark = {', f'\t\tname = "{name_key}"', f'\t\tdesc = "{desc_key}"', f'\t\tdate = {date}',
         f'\t\tpicture = "{BOOKMARK_PICTURES[scn][0]}"', '\t\tdefault_country = "SER"']
    if default:
        L.append('\t\tdefault = yes')
    L += ['\t\t"SER" = {', f'\t\t\thistory = "{hist_key}"', f'\t\t\tideology = {ideology}',
          '\t\t\tfocuses = { ' + ' '.join(focuses) + ' }', '\t\t}',
          '\t\t"---" = {', '\t\t\thistory = "OTHER_GRAND_DESC"', '\t\t}']
    L += ['\t\teffect = {', f'\t\t\trandomize_weather = {date.replace(".", "")}',
          f'\t\t\t{effect}', '\t\t}', '\t}']
    return '\n'.join(L) + '\n'


def bookmarks_file(scenarios):
    """scenarios: list of dicts with all fields ready for the file."""
    L = ['bookmarks = {']
    for s in scenarios:
        L.append(bookmark_block(s['id'], s['date'], s['name'], s['desc'], s['history'], s['ideology'],
                                s['focuses'], s['effect'], s.get('default', False)))
    L.append('}')
    return '\n'.join(L) + '\n'


# --------------------------------------------------------------------------
# focus art: match the Millennium Dawn country art to the topics of a tree
# --------------------------------------------------------------------------
ICON_KEYWORDS = [
    ('government', ('gov', 'parliament', 'president', 'council', 'assembly')),
    ('army', ('army', 'armed', 'militar', 'defence', 'defense', 'guard', 'airforce', 'air_force', 'navy')),
    ('diplomacy', ('diplom', 'summit', 'council', 'flag', 'european_union', 'un')),
    ('economy', ('econom', 'industr', 'trade', 'mine', 'market', 'bank')),
    ('conflict', ('war', 'battle', 'fight', 'crisis', 'conflict')),
    ('ideology', ('yugoslav', 'monarch', 'communism', 'democracy', 'nationalism', 'social', 'parti')),
]


def pick_icon_files(files, wanted):
    """Return the first file whose name contains one of the keywords."""
    low = [(f, f.lower()) for f in files]
    for key in wanted:
        for f, lf in low:
            if key in lf:
                return f
    return None


def assign_country_icons(tree, tag, files):
    """Give the focuses of a tree the country art of Millennium Dawn."""
    if not files:
        return
    used = set()
    for f in tree.focuses:
        fid = f['id'].lower()
        topic = None
        for name, keys in ICON_KEYWORDS:
            if any(k in fid for k in keys):
                topic = name
                break
        chosen = None
        if topic:
            for name, keys in ICON_KEYWORDS:
                if name != topic:
                    continue
                chosen = pick_icon_files(files, keys)
                break
        if not chosen:
            continue          # no country art for this topic: keep the thematic icon
        used.add(chosen)
        f['icon'] = f'BC_ico_{tag}_{os.path.splitext(chosen)[0]}'
