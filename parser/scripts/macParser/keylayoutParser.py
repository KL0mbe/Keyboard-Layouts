import cleaners.cleanAppleKeyLayoutNames as clean
from .layoutLocale import extract_country_language
from .identity import associate_apple_ids
from .modifiers import extract_modifiers
from .deadKeys import extract_dead_keys
from .keyParser import extract_keys
import xml.etree.ElementTree as ET
from .writers import write_files
import config
import json
import csv

appleNameDict = clean.build_apple_display_name()

countries = {}
languages = {}
characters = {}
keyCombos = {}
compositions = []
matches = {}
unMatches = []

kloList = []

with open(config.parserDir / "TISNames/loctable.json", newline="", encoding="utf-8") as f:
    loctable = json.load(f)

loctable_keys = {
    key.lower().replace(" ", "").replace("-", ""): key for key in loctable["en"].keys()
}

with open(config.logsDir / "layouts.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f, lineterminator="\n")
    writer.writerow(
        [
            "platform",
            "language",
            "country",
            "layout",
            "status",
            "english_name",
            "native_name",
            "klo",
            "klid",
            "apple_id",
        ]
    )

    path = config.parserDir / "Cleaned Apple Keyboard layouts"
    for file in path.glob("*.keylayout"):
        tree = ET.parse(file)
        root = tree.getroot()

        # get modifiers
        modifiersMap, baseIndex, mapSet = extract_modifiers(root, file)

        # Associate layouts with their appleIDs
        finalAppleID, name = associate_apple_ids(root, unMatches, matches)
        if finalAppleID is None:
            continue

        actionIDToCombo = {}
        baseKey = {}
        # get the base keys
        extract_keys(root=root, mapSet=mapSet, index=baseIndex, baseIndex=baseIndex, baseKey=baseKey,
                     modifiers_set=frozenset(), actionIDToCombo=actionIDToCombo, characters=characters,
                     keyCombos=keyCombos, finalAppleID=finalAppleID, )

        # get the modified keys
        for modifier, targets in modifiersMap.items():
            if targets == set():
                continue
            extract_keys(root=root, mapSet=mapSet, index=modifier, baseIndex=baseIndex, baseKey=baseKey,
                         modifiers_set=frozenset(targets), actionIDToCombo=actionIDToCombo, characters=characters,
                         keyCombos=keyCombos, finalAppleID=finalAppleID, )

        # extract Dead Keys
        extract_dead_keys(root, characters, actionIDToCombo, compositions, finalAppleID)

        # Set country and language
        langAlpha, countryAlpha, country, nativeCountry = extract_country_language(name, languages, countries)

        # get letter layout
        qwertyRow = "".join(baseKey.get(code, "?") for code in config.LetterRow)
        if qwertyRow in config.LetterLayouts:
            layout = qwertyRow
        else:
            layout = "other"

        # get native name
        nativeNames = loctable.get(langAlpha) or loctable.get("en")
        stem = finalAppleID.split(".")[-1]
        norm = stem.lower().replace(" ", "").replace("-", "")
        key = loctable_keys.get(norm)
        nativeDisplayName = nativeNames.get(key)

        # assemble KLO
        baseKLO = f"m-{langAlpha}-{countryAlpha}"
        klo = baseKLO
        # V2: More stable way of iding klo (so its consistent across different runs)
        variant = 1
        while klo in kloList:
            klo = baseKLO + f"-{variant}"
            variant += 1
        kloList.append(klo)

        # platform,lang,country,layout,status,english_name,display_name,klo,klid,apple
        writer.writerow(
            [
                "macOS",
                langAlpha,
                nativeCountry if country is not None else "X",
                layout,
                "active",
                appleNameDict[finalAppleID],
                nativeDisplayName,
                klo,
                None,
                finalAppleID,
            ]
        )

write_files(config.logsDir, countries, languages, characters, keyCombos, compositions, unMatches, matches)
print("Wrote all files")
