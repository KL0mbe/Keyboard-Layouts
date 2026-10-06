import config


def recursive_steps(root, state, actionIdToCombo):
    for action in root.findall("actions/action"):
        for when in action:
            if when.get("next") == state:
                entry = actionIdToCombo.get(action.get("id"))
                if not entry:
                    return None
                combos = entry[0]
                if when.get("state") == "none":
                    return [combos]
                else:
                    nextStep = recursive_steps(root, when.get("state"), actionIdToCombo)
                    if nextStep is None:
                        return None
                    return  nextStep + [combos]
    return None 

def extract_dead_keys(root, characters, actionIDToCombo, compositions, finalAppleID):
    for action in root.findall("actions/action"):
        for when in action.findall("when"):
            if when.get("state") != "none" and when.get("output"):
                output = when.get("output")
                characters[output] = config.get_unicode_char_data(output)
                resolver_entry = actionIDToCombo.get(action.get("id"))
                if not resolver_entry:
                    continue
                resolver = resolver_entry[0]
                primers = recursive_steps(root, when.get("state"), actionIDToCombo)
                if not primers:
                    continue

                compositions.append(
                    [
                        when.get("output"),
                        finalAppleID,
                        primers + [resolver],
                        ]
                )
