from pathlib import Path
import shutil
import xml.etree.ElementTree as ET
import csv
from cleanAppleKeyLayoutNames import *
import pycountry as pc

path = Path("../Cleaned Apple Keyboard layouts/Test xml override")

appleIDsDict = build_apple_id_dict()
appleIDSuffix = build_apple_id_suffix()
matches = {}
unMatches = []

with open("Layouts.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(
        [
            "platform_id",
            "language_id",
            "country_id",
            "layout_id",
            "standard_id",
            "klo",
            "klo1",
            "klid",
            "apple_id",
            "cldr",
            "os_version",
            "status_id",
        ]
    )

    for file in path.glob("*.keylayout"):
        tree = ET.parse(file)
        root = tree.getroot()

        baseKey = {}
        index = {}

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
                index[int(mapIndex)] = finalKeys[0]

        baseIndex = next((key for key, value in index.items() if value == set()), None)
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

        actionDict = {}
        # get the base keys
        for key in root.find(f"keyMapSet[@id='{mapSet}']/keyMap[@index='{baseIndex}']"):
            code = key.get("code")
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

                baseKey[int(code)] = actionKey
                continue

            baseKey[int(code)] = output

        # set standard

        # add to csv
        # platform,lang,country,layout,standard,klo,klo1,klid,apple,cldr,os,status
        # writer.writerow(["1", pc.countries.lookup("get the country for here"), ])

        # for keyMap in root.findall("keyMapSet[@id='ANSI']/keyMap"):

with open(f"../Logs/noMatchNames.txt", "w") as noMatch:
    for name in unMatches:
        noMatch.write(f"keyLayout {name} had no match in the list of appleIDs\n")

print(matches.keys())
