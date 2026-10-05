import config


def extract_modifiers(root, file):
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
            # if len(finalKeys) > 1:
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

    return modifiersMap, baseIndex, mapSet
