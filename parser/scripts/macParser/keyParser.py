import config


def extract_keys(root, mapSet, index, baseIndex, baseKey, modifiers_set,
                 actionIDToCombo, characters, keyCombos, finalAppleID):
    for key in root.find(f"keyMapSet[@id='{mapSet}']/keyMap[@index='{index}']"):
        output = key.get("output")
        virtualCode = int(key.get("code"))
        if virtualCode in config.NUMPAD_CODES:
            continue
        actionElement = None
        if not output:
            action = key.get("action")
            if not action:
                continue
            actionIDToCombo.setdefault(action, []).append(
                [virtualCode, modifiers_set]
            )

            for subAct in root.findall("actions/action"):
                if action == subAct.get("id"):
                    actionElement = subAct.find("when[@state='none']")

            # if actionElement is None:
            #     print(f"No ActionElement for {name, virtualCode}")

            actionOutput = actionElement.get("output")
            # Dead Keys
            if not actionOutput:
                actionState = actionElement.get("next")
                terminator = root.find(
                    f"terminators/when[@state='{actionState}']"
                )
                output = terminator.get("output")
            else:
                output = actionOutput

        if index == baseIndex:
            baseKey[virtualCode] = output
        characters[output] = config.get_unicode_char_data(output)
        keyCombos[(finalAppleID, virtualCode, modifiers_set)] = {
            "output": output,
            "base_key": baseKey.get(virtualCode),
            "key_code": virtualCode,
        }
