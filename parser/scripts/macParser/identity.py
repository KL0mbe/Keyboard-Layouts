import cleaners.cleanAppleKeyLayoutNames as clean
import config

appleIDsDict = clean.build_apple_id_dict()
appleIDSuffix = clean.build_apple_id_suffix()

# Override mismatching name -> appleIDs
OVERRIDES = {
    "swedish": "swedish-legacy",
    "italian": "italian-qzerty",
    "spanish": "spanish-legacy",
    "polish": "polish-qwertz",
}


def associate_apple_ids(root, unMatches, matches):
    name = config.clean_str(root.get("name"))
    if name in OVERRIDES:
        matches[name] = (appleIDsDict.get(OVERRIDES[name]), "Override")
    else:
        appleID = appleIDsDict.get(name)
        isSuffix = False
        if appleID is None:
            appleID = appleIDSuffix.get(name)
            isSuffix = True
        if appleID is None:
            unMatches.append(name)
            return None, name

        matches[name] = (appleID, "Stem" if isSuffix is True else "Display")

    finalAppleID = matches[name][0]

    return finalAppleID, name
