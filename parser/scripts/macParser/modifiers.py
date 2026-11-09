import config


def extract_modifiers(root, file):
    modifiersMap = {}
    layoutElement = root.find("layouts/layout[@first='0']")
    if layoutElement is None:
        layoutElement = root.find("layouts/layout")
    defaultModifier = layoutElement.get("modifiers")
    defaultMap = root.find(f"modifierMap[@id='{defaultModifier}']")
    defaultIndex = defaultMap.get("defaultIndex", "0")
    mapSet = layoutElement.get("mapSet")

    # get modifiers
    for target in config.TARGETS:
        for keyMapSelect in root.findall(
                f"modifierMap[@id='{defaultModifier}']/keyMapSelect"
        ):
            mapIndex = keyMapSelect.get("mapIndex")
            modifiers = keyMapSelect.findall("modifier")
            for modifier in modifiers:
                isMatch = True
                for subTarget in target:
                    found = False
                    for key in modifier.get("keys").split():
                        # remove ? before comparison
                        optionalKey = key[0:-1] if key.endswith("?") else key

                        if subTarget == config.CANON.get(optionalKey):
                            found = True

                    if not found:
                        isMatch = False

                for key in modifier.get("keys").split():
                    if key.endswith("?"):
                        continue
                    if config.CANON.get(key) not in target:
                        isMatch = False

                if isMatch:
                    modifiersMap[frozenset(target)] = int(mapIndex)
                    break

            if frozenset(target) in modifiersMap:
                break

        if frozenset(target) not in modifiersMap:
            print(f"defaultIndex used: {file.stem} {sorted(target)}")
            modifiersMap[frozenset(target)] = int(defaultIndex)

    baseIndex = modifiersMap.pop(frozenset(), None)
    if baseIndex is None:
        raise ValueError(f"no Base Index found in {file}")

    return modifiersMap, baseIndex, mapSet
