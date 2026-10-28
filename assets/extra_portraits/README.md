# Дополнительные портреты правителей

Клади сюда портреты, которых нет в Millennium Dawn, — мод подхватит их сам при сборке.

Правило: файл кладётся в папку страны и называется фамилией правителя:

```
assets/extra_portraits/
├── SER/    Milosevic.dds, Vucic.dds, Tito.dds
├── CRO/    Tudjman.dds, Kucan.dds
├── SLV/    Kucan.dds
├── BOS/    Kristo.dds
├── MNT/    Spajic.dds, Bulatovic.dds, Dukanovic.dds
├── KOS/    Kurti.dds, Rugova.dds
├── FYR/    Mickoski.dds, Gligorov.dds
└── SOV/    Brezhnev.dds, Yeltsin.dds, Gorbachev.dds
```

Сопоставление идёт по фамилии (без учёта диакритики): `Tudjman.dds` подойдёт к
«Franjo Tuđman», `Vucic.dds` — к «Aleksandar Vučić». Если в папке страны лежит
ровно один файл, он будет использован, даже если имя не совпало.

После добавления файлов пересобери мод:

```
python3 tools/build_mod.py --md-archive <md> --md-repo <Millennium Dawn> \
    --old-mod <Balkan_Collapse_1980 (9).zip> --out build/
python3 tools/validate_mod.py build/Balkan_Collapse
python3 tools/package_mod.py --build build/Balkan_Collapse \
    --old-zip Balkan_Collapse_1980_v2.zip --out Balkan_Collapse_1980_v3.zip
```
