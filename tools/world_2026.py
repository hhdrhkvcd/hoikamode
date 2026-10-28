# -*- coding: utf-8 -*-
"""
The world of 28 October 2026.

The third scenario of the mod is not a snapshot of a finished book - it is the
day the mod was written.  The borders below are the real ones of late October
2026, the wars listed here are still going on, and every month new news
breaks (the front lines move, peace plans are discussed, sanctions are
renewed).  Everything in this file is factual: the state ids are Millennium
Dawn ids, the leaders are the real ones, the numbers are the numbers of the
October 2026 war reporting.
"""

# --------------------------------------------------------------------------
# Leaders (tag -> name, ideology, portrait patterns, description key)
#   The tags are the Millennium Dawn ones (PER = Iran, CHI = China, ...).
# --------------------------------------------------------------------------
LEADERS_EXTRA = {
    'BRA': ('Luiz Inácio Lula da Silva', 'socialism', ['lula'], 'BRA_LULA_DESC'),
    'PER': ('Mojtaba Khamenei', 'despotism', ['mojtaba'], 'PER_KHAMENEI_DESC'),
    'SYR': ('Ahmed al-Sharaa', 'centrism', ['sharaa'], 'SYR_SHARAA_DESC'),
    'LEB': ('Joseph Aoun', 'centrism', ['aoun'], 'LEB_AOUN_DESC'),
    'ISR': ('Benjamin Netanyahu', 'conservatism', ['netanyahu'], 'ISR_NETANYAHU_DESC'),
    'PAL': ('Mahmoud Abbas', 'centrism', ['abbas'], 'PAL_ABBAS_DESC'),
    'HAM': ('Khalil al-Hayya', 'national_socialism', ['hayya'], 'HAM_HAYYAT_DESC'),
    'HEZ': ('Naim Qassem', 'national_socialism', ['qassem'], 'HEZ_QASSEM_DESC'),
    'SUD': ('Abdel Fattah al-Burhan', 'despotism', ['burhan'], 'SUD_BURHAN_DESC'),
    'SRF': ('Muhammad Hemedti', 'despotism', ['hemedti'], 'SRF_HEMEDTI_DESC'),
    'BRM': ('Min Aung Hlaing', 'despotism', ['min_aung_hlaing'], 'BRM_MINAUNG_DESC'),
    'NUG': ('Duwa Lashi La', 'centrism', ['lashi'], 'NUG_LASHILA_DESC'),
    'HUN': ('Viktor Orbán', 'despotism', ['orban'], 'HUN_ORBAN_DESC'),
    'CZE': ('Andrej Babiš', 'centrism', ['babis'], 'CZE_BABIS_DESC'),
    'GRE': ('Kyriakos Mitsotakis', 'conservatism', ['mitsotakis'], 'GRE_MITSOTAKIS_DESC'),
    'ROM': ('Ilie Bolojan', 'centrism', ['bolojan'], 'ROM_BOLOJAN_DESC'),
    'SLO': ('Robert Fico', 'socialism', ['fico'], 'SLO_FICO_DESC'),
    'RAJ': ('Narendra Modi', 'despotism', ['modi'], 'RAJ_MODI_DESC'),
    'IND': ('Prabowo Subianto', 'despotism', ['prabowo'], 'IND_PRABOWO_DESC'),
    'PAK': ('Shehbaz Sharif', 'centrism', ['shehbaz'], 'PAK_SHARIF_DESC'),
    'SAU': ('Mohammed bin Salman', 'despotism', ['bin_salman'], 'SAU_MBS_DESC'),
    'KOR': ('Lee Jae-myung', 'liberalism', ['lee_jae'], 'KOR_LEE_DESC'),
    'TAI': ('Lai Ching-te', 'centrism', ['lai_ching'], 'TAI_LAI_DESC'),
    'NRY': ('Jonas Gahr Støre', 'centrism', ['gahr_store', 'støre'], 'NRY_STORE_DESC'),
    'FIN': ('Petteri Orpo', 'centrism', ['orpo'], 'FIN_ORPO_DESC'),
    'JAP': ('Sanae Takaichi', 'conservatism', ['takaichi'], 'JAP_TAKAICHI_DESC'),
    'CHI': ('Xi Jinping', 'leninism', ['jinping'], 'CHI_XI_DESC'),
    'SPR': ('Pedro Sánchez', 'socialism', ['sanchez'], 'SPR_SANCHEZ_DESC'),
}

# hand written leader descriptions (key -> (russian, english))
LEADER_DESCS = {
    'SER_VUCIC_DESC': (
        'Александр Вучич — премьер-министр Сербии. В сентябре 2026 года он отказался от '
        'поста президента ради кампании на досрочных выборах и признал поражение '
        '«Студенческого списка» 25 октября 2026 года.',
        'Aleksandar Vucic - prime minister of Serbia. He resigned as president in September '
        '2026 to run in the snap election and conceded defeat to the Student List on '
        '25 October 2026.'),
    'BRA_LULA_DESC': (
        'Луис Инасиу Лула да Силва — президент Бразилии, вернувшийся к власти в 2026 году '
        'после победы во втором туре над Болсонару.',
        'Luiz Inacio Lula da Silva - president of Brazil, back in power after winning the '
        '2026 runoff against Bolsonaro.'),
    'PER_KHAMENEI_DESC': (
        'Моджтаба Хамейни — верховный лидер Ирана с 8 марта 2026 года, избранный через '
        'неделю после гибели его отца Али Хамейни в ходе американско-израильской войны.',
        'Mojtaba Khamenei - Supreme Leader of Iran since 8 March 2026, elected a week after '
        'his father Ali Khamenei was killed in the US-Israeli war.'),
    'SYR_SHARAA_DESC': (
        'Ахмед аш-Шараа — президент Сирии, пришедший к власти в январе 2025 года и '
        'укрепивший позиции при поддержке Турции и арабских государств.',
        'Ahmed al-Sharaa - president of Syria, in power since January 2025 and strengthened '
        'by Turkish and Arab support.'),
    'LEB_AOUN_DESC': (
        'Жозеф Аун — президент Ливана, избранный в январе 2025 года, когда армия заняла '
        'столицу и разорвала отношения с «Хезбаллой».',
        'Joseph Aoun - president of Lebanon, elected in January 2025 when the army took the '
        'capital and broke with Hezbollah.'),
    'ISR_NETANYAHU_DESC': (
        'Беньямин Нетаньяху — премьер-министр Израиля, вернувшийся к власти в 2025 году '
        'и продолжающий войну в секторе Газа и Ливане.',
        'Benjamin Netanyahu - prime minister of Israel, back in power in 2025 and still '
        'fighting in Gaza and Lebanon.'),
    'PAL_ABBAS_DESC': (
        'Махмуд Аббас — президент Палестины и лидер ФАТ. Палестинская администрация '
        'потеряла контроль над значительной частью Западного берега.',
        'Mahmoud Abbas - president of Palestine and leader of the PA. The Palestinian '
        'administration has lost control of much of the West Bank.'),
    'HAM_HAYYAT_DESC': (
        'Халиль аль-Хайя — глава политического бюро ХАМАС с 20 июля 2026 года, '
        'бывший главный переговорщик движения и участник соглашений о перемирии.',
        'Khalil al-Hayya - head of the Hamas political bureau since 20 July 2026, the '
        'movement\'s chief negotiator and signatory of the ceasefire agreements.'),
    'HEZ_QASSEM_DESC': (
        'Наим Касем — лидер «Хезбаллы» с сентября 2024 года. 26 июня 2026 года движение '
        'отклонило израильско-ливанскую рамку урегулирования.',
        'Naim Qassem - leader of Hezbollah since September 2024. On 26 June 2026 the '
        'movement rejected the Israeli-Lebanese framework.'),
    'SUD_BURHAN_DESC': (
        'Абдель Фаттах аль-Бурхан — глава суданских вооружённых сил и президент '
        'Судана. В апреле 2026 года правительство вернулось в Хартум.',
        'Abdel Fattah al-Burhan - commander of the Sudanese armed forces and president of '
        'Sudan. In April 2026 his government returned to Khartoum.'),
    'SRF_HEMEDTI_DESC': (
        'Мухаммед Хемедти — заместитель командира Сил быстрой поддержки и глава '
        'военного совета Дарфура. 1 июля 2026 года RSF объявили о создании '
        'параллельного правительства.',
        'Muhammad Hemedti - deputy commander of the Rapid Support Forces and head of the '
        'Darfur military council. On 1 July 2026 the RSF declared a parallel government.'),
    'BRM_MINAUNG_DESC': (
        'Мин Аун Хлаинг — глава военного совета Мьянмы. После победы на выборах '
        'января 2026 года он возглавил новое правительство страны.',
        'Min Aung Hlaing - chairman of Myanmar\'s military council. After the January 2026 '
        'election he heads the country\'s new military-aligned government.'),
    'NUG_LASHILA_DESC': (
        'Дува Лаши Ла — исполняющий обязанности президента теневого правительства '
        'Мьянмы и один из лидеров созданного 30 марта 2026 года Рулевого совета '
        '«Союза федеративной демократической республики».',
        'Duwa Lashi La - acting president of Myanmar\'s shadow National Unity Government and '
        'a leader of the Steering Council for the Emergence of a Federal Democratic Union, '
        'created on 30 March 2026.'),
}

# --------------------------------------------------------------------------
# The real borders of 28 October 2026 (Millennium Dawn state ids)
#   (owner, [states], comment)
# --------------------------------------------------------------------------
BORDERS = [
    ('SOV', [669, 693, 1075, 1076, 694],
     'Crimea, East Donetsk, South and North Luhansk, Zaporizhzhia - under Russian occupation'),
    ('SRF', [224, 614, 576, 223],
     'Darfur, Northern Darfur, Northwest Sudan, North Kordofan - the Rapid Support Forces'),
    ('NUG', [499, 500, 502, 505, 930],
     'Chin, Rahmanland, Rakhine, Upper Burma, North Shan - the resistance'),
    ('ISR', [201],
     'South Lebanon - occupied by Israel since March 2026'),
    ('HEZ', [553],
     'The Bekaa valley - Hezbollah'),
]

# states that change hands during the game (front line moves)
FRONT_MOVES = {
    694: 'UKR',    # Zaporizhzhia - the Ukrainian counter attack around Oleksandrivka
    1087: 'SOV',   # Dnipropetrovsk - the Russian advance on Novopavlivka
    504: 'NUG',    # Lower Burma - the resistance pushes towards the delta
    553: 'ISR',    # the Bekaa - the Israeli occupation deepens
}

# --------------------------------------------------------------------------
# The wars that are still going on
#   (attacker, target, war type, comment)
# --------------------------------------------------------------------------
WARS = [
    ('SOV', 'UKR', 'take_state', 'the war in Ukraine, since 24 February 2022'),
    ('ISR', 'HEZ', 'take_state', 'the war in Lebanon, since 2 March 2026'),
    ('SRF', 'SUD', 'civil_war', 'the civil war in Sudan'),
    ('NUG', 'BRM', 'civil_war', 'the civil war in Myanmar'),
]

# --------------------------------------------------------------------------
# The world news.  Every month one of these breaks (see the on_action).
#   id, title, description, effect, major
# --------------------------------------------------------------------------
NEWS = [
    # ---- Ukraine ---------------------------------------------------------
    dict(id='bc_2026.ua_pokrovsk',
         major=True,
         title_ru='Фронт на Покровском направлении',
         desc_ru='Российские войска ведут штурм Покровска и Костантиновки: 26 и 22 атаки '
                 'за сутки. 27 октября 2026 года Генштаб ВСУ насчитал 196 боевых столкновений '
                 'на фронте. По оценкам аналитиков, россияне медленно продавливают оборону, '
                 'но каждый день стоит им сотни жизней.',
         title_en='The Pokrovsk front',
         desc_en='Russian forces are assaulting Pokrovsk and Kostiantynivka with 26 and 22 '
                 'attacks a day. On 27 October 2026 the Ukrainian General Staff counted 196 '
                 'combat engagements along the front. The Russians are grinding forward, '
                 'but every day costs them hundreds of lives.',
         effect='SOV = { add_war_support = 0.02 } UKR = { add_war_support = 0.03 } '
                'random = { chance = 18 UKR = { transfer_state = 694 } } '
                'random = { chance = 12 SOV = { transfer_state = 1087 } }'),
    dict(id='bc_2026.ua_border',
         major=False,
         title_ru='Приграничные бои на сумско-харьковском направлении',
         desc_ru='Россия держит узкую полосу вдоль границы в Сумской и Харьковской областях. '
                 'Украинские пограничники и десантники отвечают артобстрелами, пункты '
                 'пропуска закрыты, приграничные сёла разрушены.',
         title_en='Fighting on the Sumy and Kharkiv border',
         desc_en='Russia holds a narrow strip along the border in the Sumy and Kharkiv '
                 'oblasts. Ukrainian border guards and paratroopers answer with artillery, '
                 'the crossings are closed and the border villages are in ruins.',
         effect='UKR = { add_war_support = 0.02 } SOV = { add_war_support = 0.02 }'),
    dict(id='bc_2026.ua_sea',
         major=False,
         title_ru='Удары по судоходству в Чёрном море',
         desc_ru='За 2026 год в Чёрном море поражено 570 судов, погибли 40 моряков. '
                 'Страховщики подняли ставки, часть компаний ушла из порта Новороссийска '
                 'и Одессы. Зерно и контейнеры идут через Румынию и Грузию.',
         title_en='Strikes on Black Sea shipping',
         desc_en='In 2026 alone 570 vessels have been hit in the Black Sea and 40 sailors '
                 'have died. Insurers raised their premiums, part of the fleet left '
                 'Novorossiysk and Odesa, and grain and containers now go through Romania '
                 'and Georgia.',
         effect='SOV = { add_stability = -0.01 } UKR = { add_stability = -0.01 } '
                'random = { chance = 15 SOV = { add_war_support = 0.02 } }'),
    dict(id='bc_2026.ua_peace',
         major=True,
         title_ru='Переговоры о «Звёздном щите»',
         desc_ru='План «Звёздный щит», который обсуждают Вашингтон и Брюссель, '
                 'предусматривает поставки оружия и размораживание активов, но встречный '
                 'шаг России — прекращение ударов по энергетике — по-прежнему не сделан. '
                 'Переговоры идут в режиме «ничего не решено».',
         title_en='The Starshield talks',
         desc_en='The Starshield plan discussed in Washington and Brussels provides for '
                 'weapons deliveries and the unfreezing of assets, but Russia has still not '
                 'made its reciprocal move - the strikes on the energy grid continue. The '
                 'talks are going nowhere.',
         effect='UKR = { add_political_power = 10 } SOV = { add_political_power = -10 }'),
    # ---- Gaza ------------------------------------------------------------
    dict(id='bc_2026.gaza_strike',
         major=False,
         title_ru='Удары по Гаре',
         desc_ru='Перемирие, подписанное в октябре 2025 года, существует только на бумаге: '
                 'израильские удары идут каждый день. С момента перемирия погибло более '
                 '1500 палестинов. «Жёлтая линия» делит сектор: Израиль удерживает около '
                 '65 % территории, ХАМАС управляет оставшейся третью.',
         title_en='Strikes in Gaza',
         desc_en='The ceasefire signed in October 2025 exists only on paper: Israeli strikes '
                 'continue every day. More than 1,500 Palestinians have been killed since it '
                 'began. The Yellow Line divides the strip, with Israel holding about 65 % '
                 'of the territory and Hamas governing the rest.',
         effect='HAM = { add_war_support = 0.02 add_stability = -0.01 } '
                'PAL = { add_stability = -0.01 }'),
    dict(id='bc_2026.gaza_board',
         major=False,
         title_ru='Совет мира по Газе зашёл в тупик',
         desc_ru='Восстановление Газы застряло: Совет мира, который должен был запустить '
                 'управление сектором, не может собрать деньги и персонал. ХАМАС в июле 2026 '
                 'года распустил своё правительство, часть функций перешла к местным '
                 'администрациям.',
         title_en='The Gaza Board of Peace is stuck',
         desc_en='The reconstruction of Gaza has stalled: the Board of Peace, which was '
                 'supposed to take charge of the strip, cannot raise the money or find the '
                 'staff. Hamas dissolved its government in July 2026 and some of its '
                 'functions have passed to the local administrations.',
         effect='HAM = { add_stability = -0.02 } ISR = { add_political_power = 5 }'),
    # ---- Lebanon ---------------------------------------------------------
    dict(id='bc_2026.lebanon_front',
         major=True,
         title_ru='Ливанская война: юг под оккупацией',
         desc_ru='С 2 марта 2026 года израильские войска ведут бои с «Хезбаллой» на юге '
                 'Ливана. С начала войны погибло 4350 человек. Южный Ливан остаётся под '
                 'израильским контролем, а Бейкаа — под контролем «Хезбаллы».',
         title_en='The Lebanon war: the occupied south',
         desc_en='Since 2 March 2026 Israeli troops have been fighting Hezbollah in '
                 'southern Lebanon. 4,350 people have been killed since the war began. The '
                 'south stays under Israeli control, the Bekaa under Hezbollah.',
         effect='HEZ = { add_war_support = 0.03 add_stability = -0.01 } '
                'ISR = { add_war_support = 0.02 } LEB = { add_stability = -0.02 } '
                'random = { chance = 12 ISR = { transfer_state = 553 } }'),
    dict(id='bc_2026.lebanon_diplomacy',
         major=False,
         title_ru='Исламабадская меморандум и 26 июня',
         desc_ru='15 июня 2026 года меморандум в Исламабаде закрыл войну США и Ирана, '
                 'а 26 июня Израиль и Ливан согласовали рамку урегулирования. «Хезбалла» '
                 'отвергла её, и перемирие с апреля держится только потому, что его '
                 'поддерживают обе стороны.',
         title_en='The Islamabad memorandum and 26 June',
         desc_en='On 15 June 2026 the Islamabad memorandum ended the US-Iran war, and on '
                 '26 June Israel and Lebanon agreed a framework. Hezbollah rejected it, and '
                 'the April ceasefire survives only because both sides support it.',
         effect='HEZ = { add_political_power = 5 } LEB = { add_political_power = 5 }'),
    # ---- Syria / Iran ----------------------------------------------------
    dict(id='bc_2026.syria_strikes',
         major=False,
         title_ru='Удары по Сирии продолжаются',
         desc_ru='Новое сирийское правительство Ахмеда аш-Шараа не смогло остановить '
                 'израильские удары по южной Сирии. Дамаск отвечает дипломатически, а '
                 'население привычно сжимается в кварталах.',
         title_en='The strikes in Syria continue',
         desc_en='The new Syrian government of Ahmed al-Sharaa has not managed to stop the '
                 'Israeli strikes on southern Syria. Damascus answers with diplomacy while '
                 'the population huddles into the quarters.',
         effect='SYR = { add_stability = -0.02 }'),
    dict(id='bc_2026.iran_power',
         major=False,
         title_ru='Новый верховный лидер Ирана',
         desc_ru='Моджтаба Хамейни, избранный 8 марта 2026 года, укрепляет власть '
                 'Корпуса стражей исламской революции во главе с Ахмадом Вахиди. '
                 'После гибели Али Лариджани старая дипломатическая школа страны почти '
                 'не заметна у нового руководства.',
         title_en='The new Supreme Leader of Iran',
         desc_en='Mojtaba Khamenei, elected on 8 March 2026, strengthens the grip of the '
                 'Islamic Revolutionary Guard Corps under Ahmad Vahidi. With Ali Larijani '
                 'dead, the old diplomatic school of the country is barely visible in the '
                 'new leadership.',
         effect='PER = { add_stability = 0.02 add_war_support = 0.02 }'),
    # ---- Sudan -----------------------------------------------------------
    dict(id='bc_2026.sudan_obeid',
         major=True,
         title_ru='Судан: линия фронта в Эль-Обеиде',
         desc_ru='Силы быстрой поддержки давят на Эль-Обеид, столицу Северного Кордофана. '
                 'Это последний большой город на пути к Хартуму, и его падение сломает '
                 'фронт правительства. Параллельно RSF создали своё правительство в '
                 'Дарфуре.',
         title_en='Sudan: the front line at El Obeid',
         desc_en='The Rapid Support Forces are pushing on El Obeid, the capital of North '
                 'Kordofan. It is the last big city on the road to Khartoum and its fall '
                 'would break the government front. The RSF have meanwhile set up their '
                 'own government in Darfur.',
         effect='SUD = { add_war_support = 0.03 add_stability = -0.02 } '
                'SRF = { add_war_support = 0.03 }'),
    dict(id='bc_2026.sudan_sanctions',
         major=False,
         title_ru='Новые санкции против Судана',
         desc_ru='28 октября 2026 года Великобритания ввела санкции против 15 '
                 'командиров САФ и RSF, которых обвиняют в причастности к массовому '
                 'насилию в Эль-Фашере. Совет ООН продлил мандат миссии ещё на полгода.',
         title_en='New sanctions on Sudan',
         desc_en='On 28 October 2026 Britain sanctioned 15 SAF and RSF commanders accused of '
                 'mass atrocities in El Fasher. The UN Security Council extended the '
                 'mandate of the mission for another six months.',
         effect='SUD = { add_stability = -0.02 } SRF = { add_stability = -0.02 }'),
    # ---- Myanmar ---------------------------------------------------------
    dict(id='bc_2026.myanmar_indaw',
         major=True,
         title_ru='Мьянма: наступление на Индау',
         desc_ru='Силы сопротивления ведут наступление на Индау и Вунто, продолжая '
                 'окружать город Сагаинг. 25–26 октября 2026 года в ходе штурмов '
                 'погибли десятки солдат хунты, а части Сва раскололись и перешли на '
                 'сторону повстанцев.',
         title_en='Myanmar: the offensive on Indaw',
         desc_en='The resistance is advancing on Indaw and Wuntho, tightening the siege of '
                 'Sagaing town. On 25-26 October 2026 dozens of junta soldiers were killed '
                 'in the assaults and parts of the Swat broke and defected to the rebels.',
         effect='BRM = { add_war_support = 0.03 add_stability = -0.02 } '
                'NUG = { add_war_support = 0.03 } '
                'random = { chance = 15 NUG = { transfer_state = 504 } }'),
    dict(id='bc_2026.myanmar_china',
         major=False,
         title_ru='Пекин ищет посредников в Мьянме',
         desc_ru='Китай усилил посредническую роль: 30 марта 2026 года Национальное '
                 'единство, Парламентская федерация и пять вооружённых организаций '
                 'создали Рулевой совет. Пекин хочет, чтобы «Весна революции» не докатилась '
                 'до границ Китая.',
         title_en='Beijing looks for mediators in Myanmar',
         desc_en='China has stepped up its mediation role: on 30 March 2026 the National '
                 'Unity Government, the parliamentary body and five armed organisations '
                 'created a Steering Council. Beijing wants the Spring Revolution not to '
                 'reach the Chinese border.',
         effect='NUG = { add_political_power = 10 } BRM = { add_stability = -0.01 }'),
    # ---- the rest of the world -------------------------------------------
    dict(id='bc_2026.brazil',
         major=False,
         title_ru='Лула возвращается в Бразилию',
         desc_ru='Во втором туре президентских выборов 2026 года Луис Инасиу Лула да Силва '
                 'обошёл Жаира Болсонару. Для Балкан это сигнал: Южная Америка снова '
                 'смотрит влево, а торговые переговоры с ЕС становятся сложнее.',
         title_en='Lula is back in Brazil',
         desc_en='In the 2026 runoff Luiz Inacio Lula da Silva beat Jair Bolsonaro. For the '
                 'Balkans it is a signal: South America looks left again and the trade talks '
                 'with the EU become harder.',
         effect='BRA = { add_stability = 0.03 add_political_power = 15 }'),
    dict(id='bc_2026.un_race',
         major=False,
         title_ru='Гонка за пост генерального секретаря ООН',
         desc_ru='Кандидатуры на пост генерального секретаря ООН оспаривают друг друга: '
                 'уходящего Антониу Гутерриша сменяют в 2027 году, и борьба за кресло уже '
                 'разделила даже тех, кто ещё не объявил.',
         title_en='The race for the UN Secretary-General',
         desc_en='The candidates for the post of UN Secretary-General are fighting each '
                 'other: Antonio Guterres is to be replaced in 2027 and the race for his '
                 'chair has already split those who have not even announced.',
         effect='every_country = { add_political_power = 2 }'),
    dict(id='bc_2026.red_sea',
         major=False,
         title_ru='Красное море: атаки на суда',
         desc_ru='Хуситы продолжают атаковать суда в Красном море и Баб-эль-Мандебском '
                 'проливе. Часть контейнерных линий вернулась к мысу Доброй Надежды, '
                 'поставки в порты Египта и Судана задерживаются.',
         title_en='Red Sea: attacks on shipping',
         desc_en='The Houthis keep attacking shipping in the Red Sea and the Bab el-Mandeb '
                 'strait. Part of the container lines has gone back around the Cape of Good '
                 'Hope and the deliveries to the ports of Egypt and Sudan are delayed.',
         effect='HOU = { add_war_support = 0.02 } YEM = { add_stability = -0.01 }'),
]

# --------------------------------------------------------------------------
# Serbia in 2026: the country events of the new government
# --------------------------------------------------------------------------
SERBIA_EVENTS = [
    dict(id='bc_2026.serbia.1',
         trigger='tag = SER date > 2026.10.26 has_global_flag = BC_2026_ACTIVE',
         title_ru='Уходящий президент',
         desc_ru='После поражения на выборах Вучич подал в отставку с поста президента, '
                 'который занимал с мая 2022 года. До избрания нового президента '
                 'обязанности главы государства исполняет Ана Брнабич. Кампания в свою '
                 'пользу она уже назначила на декабрь.',
         title_en='The outgoing president',
         desc_en='After his defeat in the election Vucic resigned as president, a post he '
                 'had held since May 2022. Until a new president is elected, Ana Brnabic '
                 'acts as head of state, and she has already called the presidential '
                 'election for December.',
         options=[('Поддержать новую власть', 'Support the new government',
                   'set_country_flag = BC_2026_students add_political_power = 10 '
                   'add_stability = 0.02', 1)]),
    dict(id='bc_2026.serbia.2',
         trigger='tag = SER date > 2026.11.5 has_global_flag = BC_2026_ACTIVE',
         title_ru='Новое правительство',
         desc_ru='После двух лет протестов «Студенческий список» получил 138 из 250 мест '
                 'в парламенте. Кардиолог Илия Срданович, который вёл кампанию, '
                 'претендует на пост премьер-министра: у него нет ни партийного аппарата, '
                 'ни опыта управления страной.',
         title_en='The new government',
         desc_en='After two years of protests the Student List took 138 of the 250 seats in '
                 'parliament. The cardiologist Ilija Srdanovic, who led the campaign, is in '
                 'the running for prime minister: he has neither a party machine nor any '
                 'experience of running a country.',
         options=[('Назначить Срдановича', 'Appoint Srdanovic',
                   'kill_country_leader = yes create_country_leader = { name = "Ilija Srdanovic" '
                   'desc = "SER_SRDANOVIC_DESC" ideology = liberalism traits = { } } '
                   'add_political_power = 20 add_stability = 0.05', 1),
                  ('Оставить Вучича у руля', 'Keep Vucic at the helm',
                   'add_stability = -0.05 add_political_power = -10', 0)]),
    dict(id='bc_2026.serbia.3',
         trigger='tag = SER date > 2026.12.1 has_global_flag = BC_2026_ACTIVE',
         title_ru='Чистка в полиции и госслужбах',
         desc_ru='Новое руководство обещало разобраться с теми, кто два года помогал '
                 'свергать протесты. В полиции и аппарате безопасности начинаются '
                 'увольнения, а на площадях по-прежнему стоят палатки.',
         title_en='The purge in the police and the security services',
         desc_en='The new leadership promised to settle accounts with those who spent two '
                 'years helping to crush the protests. Dismissals have begun in the police '
                 'and the security service, and the tents are still standing in the square.',
         options=[('Поддержать реформу', 'Back the reform',
                   'add_political_power = 10 add_stability = 0.03 '
                   'add_ideas = BC_2026_clean_up', 1),
                  ('Оставить всё как есть', 'Leave everything as it is',
                   'add_stability = -0.03', 0)]),
    dict(id='bc_2026.serbia.4',
         trigger='tag = SER date > 2027.1.15 has_global_flag = BC_2026_ACTIVE',
         title_ru='Европейский вопрос',
         desc_ru='После смены власти Брюссель заговорил о «новом шансе» Сербии: '
                 'разговор о вступлении в ЕС, который не двигался четыре года, снова '
                 'начался. В Белграде этому рады не все.',
         title_en='The European question',
         desc_en='After the change of power Brussels has started talking about a "new '
                 'chance" for Serbia: the accession talks that had been stuck for four '
                 'years have begun again. Not everyone in Belgrade is glad about it.',
         options=[('Ехать в Брюссель', 'Go to Brussels',
                   'add_political_power = 15 add_stability = 0.03 add_ideas = BC_eu_candidate', 1),
                  ('Держать курс на Белград', 'Keep the course on Belgrade',
                   'add_political_power = -5 add_stability = -0.02', 0)]),
    dict(id='bc_2026.serbia.5',
         trigger='tag = SER date > 2027.3.6 has_global_flag = BC_2026_ACTIVE',
         title_ru='Годовщина трагедии в Нови-Саде',
         desc_ru='Два года назад обрушение навеса вокзала в Нови-Саде унесло жизни '
                 '16 человек и стало началом протестов. В этом году у входа к вокзалу '
                 'открыли мемориал, и тысячи людей пришли к нему снова.',
         title_en='The anniversary of the Novi Sad tragedy',
         desc_en='Two years ago the collapse of the railway station canopy in Novi Sad took '
                 'the lives of 16 people and started the protests. This year a memorial was '
                 'opened at the station and thousands came to it again.',
         options=[('Поклониться погибшим', 'Bow to the dead',
                   'add_political_power = 10 add_stability = 0.03 add_war_support = 0.02', 1)]),
]
