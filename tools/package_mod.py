#!/usr/bin/env python3
"""Packs the built mod into a release archive.

    python3 tools/package_mod.py --build build/Balkan_Collapse --old-zip Balkan_Collapse_1980_v2.zip \
        --out Balkan_Collapse_1980_v3.zip
"""
import argparse
import os
import shutil
import zipfile

HELPERS = ['START_BALKAN.bat', 'START_BALKAN.ps1', 'RESTORE_PREVIOUS_MODS.bat', 'RESTORE_PREVIOUS_MODS.ps1']

README = """БАЛКАНЫ 1980: РАСПАД ЮГОСЛАВИИ — версия 3.0 (самостоятельный мод)

ЧТО ВНУТРИ
- ТРИ СЦЕНАРИЯ (закладки):
  1) «Распад Югославии — 1980» (старт по умолчанию): 1 мая 1980 года, маршал Тито при смерти,
     СССР ещё цел, границы мира — как в 1980 году.
  2) «После Дейтона — 1995»: Югославия распалась, Хорватия, Словения, Босния и Республика
     Сербская независимы, СССР уже прекратил существование (15 республик).
  3) «Сербия — 2026»: сегодняшние реальные границы, правители 2026 года, «Студенческий список»
     у власти в Белграде.
- Сербия (СФРЮ): Тито умирает 4 мая 1980, к власти приходит Вучич. 1991 — независимость
  Словении и Хорватии; 1992 — Республика Сербская и Босния; 1995 — Дейтон; 1999 — НАТО;
  2006 — Черногория; 2008 — Косово; 25.10.2026 — победа «Студенческого списка».
- Распад СССР 26 декабря 1991 года — по истории: Украина, Беларусь, Молдова, Грузия, Армения,
  Азербайджан, Казахстан, Киргизия, Узбекистан, Туркменистан, Таджикистан, Эстония, Латвия и
  Литва становятся отдельными государствами со своими правителями.
- Деревья фокусов: Сербия (56 фокусов, три пути сборки Югославии: сила, новая федерация, Европа)
  + Хорватия, Словения, Босния и Герцеговина, Республика Сербская, Черногория, Косово,
  Северная Македония + собственное дерево фокусов у каждой страны мира.
- Настоящие портреты правителей (Тито, Вучич, Милошевич, Изебегович, Курти, Пленкович, Янша,
  Путин, Зеленский и другие) и подходящие картинки у фокусов.
- Загрузочные экраны: 1) «Сербия 1980» — начало разрухи, 2) «Сербия», 3–5 — Белград.
- Флаги: СФРЮ, Сербия, Хорватия, Словения, Босния, Республика Сербская, Черногория, Косово,
  Северная Македония, СССР и все республики бывшего Союза.

УСТАНОВКА
1. Распакуй ZIP целиком в отдельную папку.
2. Закрой HOI4 и лаунчер, запусти START_BALKAN.bat (включит только этот мод).
   Или вручную: папку Balkan_Collapse и файл Balkan_Collapse.mod положи в
   Документы/Paradox Interactive/Hearts of Iron IV/mod/
3. ВАЖНО: перед этим удали старую папку Balkan_Collapse (версии 1.5 и 2.0) из папки mod.
4. Выключи все остальные моды (особенно Millennium Dawn) — этот мод сам меняет карту.
5. Если игра вылетит — пришли файл Документы/Paradox Interactive/Hearts of Iron IV/logs/error.log

Карта, портреты, флаги и иллюстрации фокусов © Millennium Dawn team, лицензия CC BY-SA 4.0.
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--build', required=True, help='built mod folder')
    ap.add_argument('--old-zip', help='zip with the launcher scripts')
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    stage = os.path.join(os.path.dirname(os.path.abspath(a.out)), '_stage_' + os.path.basename(a.out)[:-4])
    if os.path.exists(stage):
        shutil.rmtree(stage)
    os.makedirs(stage)
    shutil.copytree(a.build, os.path.join(stage, 'Balkan_Collapse'))
    if a.old_zip and os.path.exists(a.old_zip):
        with zipfile.ZipFile(a.old_zip) as zf:
            for n in HELPERS:
                if n in zf.namelist():
                    with open(os.path.join(stage, n), 'wb') as f:
                        f.write(zf.read(n))
    with open(os.path.join(stage, 'README_RU.txt'), 'w', encoding='utf-8') as f:
        f.write(README)
    mod = os.path.join(stage, 'Balkan_Collapse', 'descriptor.mod')
    if os.path.exists(mod):
        with open(os.path.join(stage, 'Balkan_Collapse.mod'), 'w', encoding='utf-8') as f:
            f.write(open(mod, encoding='utf-8').read())
    if os.path.exists(a.out):
        os.remove(a.out)
    with zipfile.ZipFile(a.out, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for root, _, files in os.walk(stage):
            for fn in files:
                p = os.path.join(root, fn)
                zf.write(p, os.path.relpath(p, stage))
    shutil.rmtree(stage)
    print('packaged ->', a.out, os.path.getsize(a.out) // 1024, 'KB')


if __name__ == '__main__':
    main()
