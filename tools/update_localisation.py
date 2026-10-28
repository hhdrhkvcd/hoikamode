#!/usr/bin/env python3
"""Retain existing focus translations, update scenario text and add new keys."""

import ast
import json
import re
from pathlib import Path

from import_map import localisation

ROOT = Path(__file__).resolve().parents[1]
MOD = ROOT / "Balkan_Collapse"
COUNTRIES = json.loads((ROOT / "data/balkans.json").read_text("utf-8"))["countries"]

RU = {
    "SERBIA_1980_NAME": "Югославия — 1 мая 1980",
    "SERBIA_1980_DESC": "Единая Югославия вступает в 1980-е: долги, изношенная промышленность и хрупкое единство республик. Тито умирает 4 мая. По альтернативному лору его преемником становится Александр Вучич, а распад развивается в 1991–2008 годах. Восстанови федерацию переговорами или силой. Карта и внешние границы республик взяты из присланных современных материалов.",
    "BC_2008_NAME": "Сербия — восстановление после распада",
    "BC_2008_DESC": "18 февраля 2008 года. Все восемь игровых стран уже доступны для выбора; Республика Сербская представлена отдельным игровым субъектом Боснии и Герцеговины. Не нужно ждать распада с 1980 года. Лидеры перенесены из политического состава 2026 года: это намеренная альтернативная история, а не реконструкция персоналий 2008 года.",
    "SER_BOOKMARK_1980_HISTORY": "1 мая 1980 года единая федерация находится под руководством Иосипа Броза Тито. Через три дня начинается новая эпоха. Экономические и национальные противоречия приведут к выходу республик в 1991–2008 годах. Смена Тито на Вучича — вымышленное условие сценария.",
    "BC_SER_BOOKMARK_2008_HISTORY": "После выхода Черногории и провозглашения независимости Косово Сербии предстоит восстановить промышленность и армию. Александр Вучич руководит страной по альтернативному лору. Выбери переговоры о новой федерации или военный путь.",
    "SER_TITO_DESC": "Иосип Броз Тито — югославский коммунистический лидер. Дата его смерти в сценарии — 4 мая 1980 года. Дальнейшая смена власти на Вучича является альтернативной историей.",
    "SER_LEADER_DESC": "Александр Вучич — назначенный по запросу автора преемник Тито в альтернативной хронологии. Он приходит к власти после смерти Тито, а не в 1992 году. Это не утверждение о реальной политической биографии Вучича.",
    "BOS_LEADER_DESC": "Боряна Кришто — председатель Совета министров Боснии и Герцеговины. Политик из состава руководства 2026 года перенесён в альтернативную хронологию.",
    "CRO_LEADER_DESC": "Андрей Пленкович — премьер-министр Хорватии. Политик из состава руководства 2026 года перенесён в альтернативную хронологию.",
    "MAC_LEADER_DESC": "Христиан Мицкоский — премьер-министр Северной Македонии. Политик из состава руководства 2026 года перенесён в альтернативную хронологию.",
    "MNT_LEADER_DESC": "Милойко Спаич — премьер-министр Черногории. Политик из состава руководства 2026 года перенесён в альтернативную хронологию.",
    "SLV_LEADER_DESC": "Янез Янша — премьер-министр Словении в 2026 году. Перенесён в альтернативную хронологию.",
    "KOS_LEADER_DESC": "Альбин Курти — премьер-министр Косово в 2026 году. Перенесён в альтернативную хронологию. Международный статус Косово остаётся спорным.",
    "SRP_LEADER_DESC": "Синиша Каран — политик Республики Сербской в 2026 году. В моде субъект Боснии и Герцеговины представлен отдельным игровым тегом; это не утверждение о его международной независимости.",
    "serbia_collapse.1.d": "4 мая 1980 года умер Иосип Броз Тито. По альтернативному лору мода управление переходит к Александру Вучичу. Федерация не распадается в один день: впереди экономический кризис 1980-х и выход республик в 1991–2008 годах. В действительной истории Вучич не был преемником Тито.",
    "serbia_collapse.1.a": "Вучич принимает руководство",
    "serbia_collapse.12.d": "27 апреля 1992 года Сербия и Черногория образовали Союзную Республику Югославию. Игровой тег остаётся SER, Вучич сохраняет руководство по альтернативному лору. Повторной смены лидера не происходит.",
    "serbia_collapse.14.d": "Дейтонское урегулирование завершает боснийский конфликт. В игровой модели Республика Сербская становится субъектом Боснии и Герцеговины, а Брчко передаётся Боснии. Это упрощение, а не точное воспроизведение конституционного устройства страны.",
    "SER_reunify_peacefully_desc": "Направить независимым республикам предложение о федерации. Каждое правительство может согласиться или отказаться: автоматической аннексии всех соседей нет. Переговоры можно повторять через решения, раз в 180 дней для каждой страны.",
    "SER_balkan_campaign_desc": "Подготовить военные цели против независимых республик. Во вкладке решений откроются отдельные операции: каждую войну ты начинаешь осознанно, а не все сразу. После возвращения всех двадцати областей можно провозгласить восстановление федерации.",
    "SER_restore_cores_desc": "Для завершения необходимо владеть и полностью контролировать все двадцать областей бывшей федерации на новой карте. Они получат национальный статус; последующие автоматические выходы республик будут прекращены.",
    "SER_claim_kosovo_desc": "Заявить претензии на Косово и Северное Косово. Используются области 785 и 1305 новой карты, а не одноимённые номера старой карты HOI4.",
    "BC_BALKAN_FEDERATION": "Балканская федерация",
    "BC_reunification": "Восстановление Югославии",
    "BC_reunification_desc": "Переговоры требуют согласия республик. Военные операции открываются фокусом «Балканская кампания». Восстановление возможно только при владении и контроле всех двадцати областей федерации.",
    "BC_proclaim_restoration": "Провозгласить восстановление федерации",
    "BC_proclaim_restoration_desc": "Объединить возвращённые территории, восстановить национальные области и завершить цепочку обязательных выходов республик.",
    "BC_debt_crisis": "Долговой кризис федерации",
    "BC_debt_crisis_desc": "Долги и падение доверия тормозят строительство. Заверши программу конкурентоспособной экономики или восстанови федерацию, чтобы снять этот дух.",
    "BC_fragmented_command": "Раздробленное командование",
    "BC_fragmented_command_desc": "Армейские структуры требуют реорганизации. Заверши военную программу, чтобы восстановить организацию войск.",
    "BC_reconstruction_program": "Программа восстановления",
    "BC_reconstruction_program_desc": "Согласованное развитие промышленности ускоряет строительство.",
    "BC_regional_cooperation": "Балканское сотрудничество",
    "BC_research_bonus": "Промышленная исследовательская программа",
    "bc_federation.1.t": "Предложение новой федерации",
    "bc_federation.1.d": "[FROM.GetNameDef] предлагает добровольное объединение. Принятие приведёт к включению нашей страны и армии в федерацию. Можно отказаться и сохранить независимость. Объединение откладывается, если одна из сторон вступила в войну.",
    "bc_federation.1.a": "Согласиться на объединение",
    "bc_federation.1.b": "Сохранить независимость",
    "bc_federation.2.t": "Переговоры не привели к объединению",
    "bc_federation.2.d": "[FROM.GetNameDef] отклоняет предложение федерации. Независимость страны сохранена. Переговоры можно повторить через соответствующее решение после периода ожидания.",
    "bc_federation.2.a": "Продолжить дипломатическую работу",
    "BC_generic_tree": "Национальное развитие",
}
EN = {
    "SERBIA_1980_NAME": "Yugoslavia — 1 May 1980",
    "SERBIA_1980_DESC": "An intact Yugoslavia enters the 1980s with rising debt and fragile federal institutions. Tito dies on 4 May. In this deliberately alternate timeline Aleksandar Vučić succeeds him; secession unfolds in 1991–2008. Restore the federation through negotiation or war. Republican borders use the supplied modern map.",
    "BC_2008_NAME": "Serbia — rebuilding after the collapse",
    "BC_2008_DESC": "18 February 2008. All eight Balkan tags are playable without waiting through the collapse. Republika Srpska is represented as a subject of Bosnia and Herzegovina. Leaders from the 2026 political roster are deliberately transplanted into this alternate history.",
    "SER_BOOKMARK_1980_HISTORY": "On 1 May 1980 the intact federation is led by Josip Broz Tito. His death three days later begins a new era of economic and political strain. The succession by Vučić is fictional; the secession milestones follow 1991–2008.",
    "BC_SER_BOOKMARK_2008_HISTORY": "Following Montenegro’s departure and Kosovo’s declaration of independence, Serbia must rebuild its industry and army. Vučić leads Serbia under the alternate premise. Choose negotiated federation or military reunification.",
    "SER_TITO_DESC": "Josip Broz Tito, Yugoslav communist leader, dies on 4 May 1980 in this scenario. His succession by Vučić is deliberately fictional.",
    "SER_LEADER_DESC": "Aleksandar Vučić succeeds Tito at the author’s request in this alternate timeline, not in real history. The 1992 transition no longer replaces him with another politician.",
    "BOS_LEADER_DESC": "Borjana Krišto, chair of the Council of Ministers, transplanted from the 2026 political roster into this alternate timeline.",
    "CRO_LEADER_DESC": "Andrej Plenković, prime minister, transplanted from the 2026 political roster into this alternate timeline.",
    "MAC_LEADER_DESC": "Hristijan Mickoski, prime minister, transplanted from the 2026 political roster into this alternate timeline.",
    "MNT_LEADER_DESC": "Milojko Spajić, prime minister, transplanted from the 2026 political roster into this alternate timeline.",
    "SLV_LEADER_DESC": "Janez Janša, prime minister in 2026, transplanted into this alternate timeline.",
    "KOS_LEADER_DESC": "Albin Kurti, prime minister in 2026, transplanted into this alternate timeline. Kosovo’s international status remains disputed.",
    "SRP_LEADER_DESC": "Siniša Karan, a Republika Srpska politician from the 2026 roster. This separate playable tag represents an entity within Bosnia and Herzegovina, not recognition as an independent state.",
    "serbia_collapse.1.d": "Josip Broz Tito has died on 4 May 1980. In this deliberately alternate scenario Aleksandar Vučić takes power. The federation remains intact initially, but economic and political tensions precede the secessions of 1991–2008. Vučić did not succeed Tito in real history.",
    "serbia_collapse.1.a": "Vučić assumes leadership",
    "serbia_collapse.12.d": "Serbia and Montenegro form the Federal Republic of Yugoslavia on 27 April 1992. The playable tag remains SER. Vučić continues to lead under the alternate premise; this event does not replace him again.",
    "serbia_collapse.14.d": "The Dayton settlement ends the Bosnian conflict. In this simplified game model, Republika Srpska becomes a subject of Bosnia and Herzegovina and Brčko is transferred to Bosnia. This is not an exact constitutional simulation.",
    "SER_reunify_peacefully_desc": "Offer a voluntary federation to independent republics. Each government can accept or refuse; there is no unconditional annexation. Repeat invitations through decisions after a 180-day cooldown for each country.",
    "SER_balkan_campaign_desc": "Prepare war goals and unlock separate military operations in the decisions tab. Choose when to begin each war instead of declaring all of them at once. Reclaim and control all twenty federal states to restore the federation.",
    "SER_restore_cores_desc": "Own and fully control all twenty states of the former federation on the new map. They become national cores and later mandatory secession events are stopped.",
    "SER_claim_kosovo_desc": "Claim Kosovo and Northern Kosovo: states 785 and 1305 on the supplied modern map, not the obsolete vanilla-map IDs.",
    "BC_BALKAN_FEDERATION": "Balkan Federation",
    "BC_reunification": "Reuniting Yugoslavia",
    "BC_reunification_desc": "Peaceful unification requires consent. Military operations are unlocked by the Balkan Campaign focus. Own and control all twenty federal states before proclaiming restoration.",
    "BC_proclaim_restoration": "Proclaim the restored federation",
    "BC_proclaim_restoration_desc": "Restore national cores and end mandatory secessions after reclaiming the entire federation.",
    "BC_debt_crisis": "Federal Debt Crisis",
    "BC_debt_crisis_desc": "Debt and declining confidence slow construction. Complete the competitive economy programme or restore the federation to remove this spirit.",
    "BC_fragmented_command": "Fragmented Command",
    "BC_fragmented_command_desc": "Army structures require reform. Complete the army programme to recover organisation.",
    "BC_reconstruction_program": "Reconstruction Programme",
    "BC_reconstruction_program_desc": "Coordinated industrial recovery accelerates construction.",
    "BC_regional_cooperation": "Balkan Cooperation",
    "BC_research_bonus": "Industrial Research Programme",
    "bc_federation.1.t": "An Offer of Federation",
    "bc_federation.1.d": "[FROM.GetNameDef] proposes voluntary unification. Accepting integrates our country and army into the federation. We may refuse and remain independent. Unification is postponed if either side enters a war.",
    "bc_federation.1.a": "Agree to unification",
    "bc_federation.1.b": "Preserve our independence",
    "bc_federation.2.t": "Federation Negotiations Fail",
    "bc_federation.2.d": "[FROM.GetNameDef] has refused the offer. Its independence is preserved. A new invitation can be sent through decisions after the cooldown.",
    "bc_federation.2.a": "Continue diplomatic efforts",
    "BC_generic_tree": "National Development",
}


def update():
    for language, additions in [("russian", RU), ("english", EN)]:
        path = MOD / f"localisation/{language}/balkan_collapse_l_{language}.yml"
        values = {}
        for line in path.read_text("utf-8-sig").splitlines()[1:]:
            match = re.match(r'\s+([\w.]+):\d*\s+(".*")\s*$', line)
            if match:
                values[match[1]] = ast.literal_eval(match[2])
        values.pop("SER_COLLECTIVE_DESC", None)
        values.update(additions)
        for tag, c in COUNTRIES.items():
            label = c["name_ru"] if language == "russian" else c["name_en"]
            if tag != "SER":
                values[f"BC_{tag}_BOOKMARK_HISTORY"] = (
                    f"{label}: собственная программа восстановления и независимости, 50 национальных фокусов. Руководитель — {c['leader_ru']} по альтернативному лору 2026 года."
                    if language == "russian"
                    else f"{label}: an independent recovery programme with 50 national focuses, led by {c['leader']} under the alternate 2026-roster premise."
                )
                values[f"BC_invite_{tag}"] = (
                    f"Пригласить в федерацию: {label}"
                    if language == "russian"
                    else f"Invite to the federation: {label}"
                )
                values[f"BC_invite_{tag}_desc"] = (
                    "Направить добровольное предложение об объединении. Правительство может отказать. Повторная попытка возможна через 180 дней."
                    if language == "russian"
                    else "Send a voluntary offer of unification. The recipient may refuse. Can be repeated after 180 days."
                )
                values[f"BC_campaign_{tag}"] = (
                    f"Объявить войну: {label}"
                    if language == "russian"
                    else f"Declare war: {label}"
                )
                values[f"BC_campaign_{tag}_desc"] = (
                    "Это решение немедленно объявляет войну указанной стране. Сначала подготовь армию. Субъекты участвуют на стороне своего сюзерена."
                    if language == "russian"
                    else "This decision immediately declares war on the named country. Prepare your army first. Subjects fight alongside their overlord."
                )
        for key, en, ru in [
            (
                "BC_YUGOSLAVIA",
                "Socialist Federal Republic of Yugoslavia",
                "Социалистическая Федеративная Республика Югославия",
            ),
            (
                "BC_FRY",
                "Federal Republic of Yugoslavia",
                "Союзная Республика Югославия",
            ),
            ("BC_SERBIA", "Republic of Serbia", "Республика Сербия"),
            (
                "BC_RESTORED_YUGOSLAVIA",
                "Restored Yugoslav Federation",
                "Возрождённая Югославская федерация",
            ),
        ]:
            label = ru if language == "russian" else en
            values[key] = label
            values[key + "_DEF"] = label
            values[key + "_ADJ"] = (
                "Югославский" if language == "russian" else "Yugoslav"
            )
            for ideology in ["democratic", "communism", "fascism", "neutrality"]:
                values[f"{key}_{ideology}"] = label
                values[f"{key}_{ideology}_DEF"] = label
                values[f"{key}_{ideology}_ADJ"] = values[key + "_ADJ"]
        for branch, en, ru in [
            ("civic", "Civil Reform", "Гражданские реформы"),
            ("industry", "Industrial Development", "Развитие промышленности"),
            ("defence", "Defence Programme", "Оборонная программа"),
        ]:
            for n in range(1, 6):
                key = f"BC_generic_{branch}_{n}"
                values[key] = f"{ru if language == 'russian' else en} — {n}"
                values[key + "_desc"] = (
                    "Программа развития страны на новой карте."
                    if language == "russian"
                    else "A national development programme for the modern map."
                )
        localisation(path, language, values)
    print("Updated Russian/English scenario, leader, decision and event text.")


if __name__ == "__main__":
    update()
