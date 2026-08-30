from pathlib import Path
import shutil
import xml.etree.ElementTree as ET
import csv
from babel import Locale, localedata
import config
import unicodedata
from cleanAppleKeyLayoutNames import *
import pycountry as pc

path = Path("../Cleaned Apple Keyboard layouts/Test xml override")

appleIDsDict = build_apple_id_dict()
appleIDSuffix = build_apple_id_suffix()
matches = {}
unMatches = []
kloList = []

countryNames = {}
languages = {}
en = Locale("en")

characters = {}


with open("../logs/Layouts.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(
        [
            "platform_id",
            "language_id",
            "country_id",
            "layout_id",
            "klo",
            "klid",
            "apple_id",
            "cldr",
            "status_id",
        ]
    )

    for file in path.glob("*.keylayout"):
        tree = ET.parse(file)
        root = tree.getroot()

        baseKey = {}
        modifiersMap = {}

        layoutElement = root.find("layouts/layout[@first='0']")
        if layoutElement is None:
            raise ValueError(f"No Layout with first=0 found in {file}")
        defaultModifier = layoutElement.get("modifiers")
        mapSet = layoutElement.get("mapSet")

        # get modifiers
        for keyMapSelect in root.findall(
            f"modifierMap[@id='{defaultModifier}']/keyMapSelect"
        ):
            mapIndex = keyMapSelect.get("mapIndex")
            modifiers = keyMapSelect.findall("modifier")
            finalKeys = []
            for modifier in modifiers:
                keys = set()
                for key in modifier.get("keys").split():
                    if key.endswith("?"):
                        continue
                    keys.add(config.CANON.get(key))

                if keys in config.TARGETS:
                    finalKeys.append(keys)
            if finalKeys:
                if len(finalKeys) > 1:
                    Placeholder = None
                    # KEEP for V2 No Errors for v1 so commented out
                    # print(
                    #     f"{root.get('name')} MORE THAN ONE COMBO MATCH {finalKeys} IN MAP INDEX: {mapIndex}"
                    # )
                modifiersMap[int(mapIndex)] = finalKeys[0]

        baseIndex = next(
            (key for key, value in modifiersMap.items() if value == set()), None
        )
        if baseIndex is None:
            raise ValueError(f"no Base Index found in {file}")

        # Associate layouts with their appleIDs
        name = config.clean_str(root.get("name"))
        appleID = appleIDsDict.get(name)
        isSuffix = False
        if appleID is None:
            appleID = appleIDSuffix.get(name)
            isSuffix = True
        if appleID is None:
            unMatches.append(name)
        else:
            matches[name] = (appleID, "Stem" if isSuffix is True else "Display")

        # Override mismatching name -> Ids
        def matches_override():
            matches["swedish"] = (appleIDsDict.get("swedish-legacy"), "Override")
            matches["italian"] = (appleIDsDict.get("italian-qzerty"), "Override")
            matches["spanish"] = (appleIDsDict.get("spanish-legacy"), "Override")
            matches["polish"] = (appleIDsDict.get("polish-qwertz"), "Override")

        matches_override()

        actionDict = {}
        # get the base keys
        for key in root.find(f"keyMapSet[@id='{mapSet}']/keyMap[@index='{baseIndex}']"):
            codePoint = None
            isoCode = key.get("code")
            output = key.get("output")
            if not output:
                action = key.get("action")
                if not action:
                    continue

                actionDict[action] = actionElement = root.find(
                    f'actions/action[@id="{action}"]/when[@state="none"]'
                )

                if actionElement is None:
                    continue

                actionKey = actionElement.get("output")
                if not actionKey:
                    continue

                baseKey[int(isoCode)] = actionKey
                characters[actionKey] = config.get_unicode_char_data(actionKey)
                continue

            baseKey[int(isoCode)] = output
            characters[output] = config.get_unicode_char_data(output)

        # set standard
        # add to csv
        lang = pc.languages.lookup(config.LayoutLocale.get(name).get("language"))
        langAlpha = getattr(lang, "alpha_2", None) or lang.alpha_3
        locale = Locale(langAlpha)

        dictCountry = config.LayoutLocale.get(name).get("country")
        englishCountry = None
        nativeCountry = None

        # extract languages for lang table
        languages[langAlpha] = {
            "name": lang.name,
            "native_name": locale.languages.get(langAlpha),
        }

        if dictCountry is not None:
            country = pc.countries.lookup(dictCountry)
            countryAlpha = country.alpha_2
        else:
            country = None
            countryAlpha = "X"

        # get Country Names
        if localedata.exists(langAlpha) and country is not None:
            nativeCountry = Locale(langAlpha).territories.get(
                countryAlpha, country.name
            )

        # extract countries for country table
        if countryAlpha != "X":
            englishCountry = en.territories.get(countryAlpha, country.name)
            countryNames[nativeCountry] = {
                "country": englishCountry,
                "iso": countryAlpha,
            }

        qwertyRow = "".join(baseKey.get(code, "?") for code in config.LetterRow)
        if qwertyRow in config.LetterLayouts:
            layout = qwertyRow
        else:
            layout = "other"

        baseKLO = f"m-{langAlpha}-{countryAlpha}"
        klo = baseKLO
        # V2: More stable way of iding klo
        variant = 1
        while klo in kloList:
            klo = baseKLO + f"-{variant}"
            variant += 1
        kloList.append(klo)

        finalAppleID = matches[name][0]

        # platform,lang,country,layout,klo,klid,apple,cldr,status
        writer.writerow(
            [
                "1",
                langAlpha,
                nativeCountry if country is not None else "X",
                layout,
                klo,
                None,
                finalAppleID,
                None,
                "active",
            ]
        )

with open("../Logs/countries.csv", "w", newline="", encoding="utf-8") as eCountries:
    writer = csv.writer(eCountries)
    writer.writerow(["country", "native_name", "iso_3166"])
    for native_name, value in countryNames.items():
        writer.writerow([value["country"], native_name, value["iso"]])

with open("../Logs/languages.csv", "w", newline="", encoding="utf-8") as eLanguages:
    writer = csv.writer(eLanguages)
    writer.writerow(["name", "native_name", "iso_639"])
    for isoCode, names in languages.items():
        writer.writerow([names["name"], names["native_name"], isoCode])

with open("../Logs/characters.csv", "w", newline="", encoding="utf-8") as eCharacters:
    writer = csv.writer(eCharacters)
    writer.writerow(["character", "code_point", "unicode_name"])
    for char, values in characters.items():
        writer.writerow([char, values["code_point"], values["unicode_name"]])

with open("../Logs/noMatchNames.txt", "w") as noMatch:
    for name in unMatches:
        noMatch.write(f"keyLayout {name} had no match in the list of appleIDs\n")
