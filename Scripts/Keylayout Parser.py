from cleanAppleKeyLayoutNames import *
from babel import Locale, localedata
import xml.etree.ElementTree as ET
import pycountry as pc
import csv

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
keyCombos = {}

with open("../logs/layouts.csv", "w", newline="") as f:
    writer = csv.writer(f, lineterminator="\n")
    writer.writerow(
        [
            "platform",
            "language",
            "country",
            "layout",
            "status",
            "klo",
            "klid",
            "apple_id",
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
        finalAppleID = matches[name][0]

        # get the base keys
        def extract_keys(index=baseIndex, modifiers_set=frozenset()):
            for key in root.find(f"keyMapSet[@id='{mapSet}']/keyMap[@index='{index}']"):
                virtualCode = int(key.get("code"))
                if virtualCode in config.NUMPAD_CODES:
                    continue
                output = key.get("output")
                actionElement = None
                if not output:
                    action = key.get("action")
                    if not action:
                        continue

                    for act in root.findall("actions/action"):
                        if action == act.get("id"):
                            actionElement = act.find("when[@state='none']")

                    if actionElement is None:
                        continue

                    actionKey = actionElement.get("output")
                    if not actionKey:
                        continue

                    output = actionKey

                if index == baseIndex:
                    baseKey[virtualCode] = output
                characters[output] = config.get_unicode_char_data(output)
                keyCombos[(finalAppleID, virtualCode, modifiers_set)] = {
                    "output": output,
                    "base_key": baseKey.get(virtualCode),
                    "key_code": (
                        virtualCode if virtualCode == 10 or virtualCode == 50 else None
                    ),
                }

        extract_keys()

        for modifier, targets in modifiersMap.items():
            if targets == set():
                continue
            extract_keys(modifier, frozenset(targets))

        # Set country and language
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

        # platform,lang,country,layout,klo,klid,apple,status
        writer.writerow(
            [
                "macOS",
                langAlpha,
                nativeCountry if country is not None else "X",
                layout,
                "active",
                klo,
                None,
                finalAppleID,
            ]
        )

# it was because of "english" countries I named it eCountries. that's where it came from
with open("../Logs/countries.csv", "w", newline="", encoding="utf-8") as eCountries:
    writer = csv.writer(eCountries, lineterminator="\n")
    writer.writerow(["country", "native_name", "iso_3166"])
    for native_name, targets in countryNames.items():
        writer.writerow([targets["country"], native_name, targets["iso"]])

with open("../Logs/languages.csv", "w", newline="", encoding="utf-8") as eLanguages:
    writer = csv.writer(eLanguages, lineterminator="\n")
    writer.writerow(["name", "native_name", "iso_639"])
    for isoCode, names in languages.items():
        writer.writerow([names["name"], names["native_name"], isoCode])

with open("../Logs/characters.csv", "w", newline="", encoding="utf-8") as eCharacters:
    writer = csv.writer(eCharacters, lineterminator="\n")
    writer.writerow(["character", "code_point", "unicode_name"])
    for char, value in characters.items():
        writer.writerow([char, value["code_point"], value["unicode_name"]])

with open("../Logs/combos.csv", "w", newline="", encoding="utf-8") as eCombos:
    writer = csv.writer(eCombos, lineterminator="\n")
    writer.writerow(
        [
            "output",
            "base_key",
            "keyboard_apple_id",
            "key_code",
            "opt_alt",
            "shift",
            "ctrl",
            "altGR",
        ]
    )
    setCount = 0
    for key, value in keyCombos.items():
        mods = key[2]
        if value["base_key"] is not None:
            writer.writerow(
                # change to bools for modifiers
                [
                    value["output"],
                    value["base_key"],
                    key[0],
                    value["key_code"],
                    "option" in mods,
                    "shift" in mods,
                    False,
                    False,
                ]
            )

with open("../Logs/noMatchNames.txt", "w") as noMatch:
    for name in unMatches:
        noMatch.write(f"keyLayout {name} had no match in the list of appleIDs\n")
