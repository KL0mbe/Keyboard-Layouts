import config
import json
import csv


def write_files(logsDir, countries, languages, characters, keyCombos, compositions, unMatches, matches):
    with open(logsDir / "countries.csv", "w", newline="", encoding="utf-8") as eCountries:
        writer = csv.writer(eCountries, lineterminator="\n")
        writer.writerow(["country", "native_name", "iso_3166"])
        for native_name, targets in countries.items():
            writer.writerow([targets["country"], native_name, targets["iso"]])

    with open(logsDir / "languages.csv", "w", newline="", encoding="utf-8") as eLanguages:
        writer = csv.writer(eLanguages, lineterminator="\n")
        writer.writerow(["name", "native_name", "iso_639"])
        for isoCode, names in languages.items():
            writer.writerow([names["name"], names["native_name"], isoCode])

    with open(logsDir / "characters.csv", "w", newline="", encoding="utf-8") as eCharacters:
        writer = csv.writer(eCharacters, lineterminator="\n")
        writer.writerow(["character", "code_point", "unicode_name"])
        for char, value in characters.items():
            writer.writerow([char, value["code_point"], value["unicode_name"]])

    with open(logsDir / "combos.csv", "w", newline="", encoding="utf-8") as eCombos:
        writer = csv.writer(eCombos, lineterminator="\n")
        writer.writerow(
            [
                "output",
                "base_key",
                "key_code",
                "keyboard_apple_id",
                "opt_alt",
                "shift",
                "ctrl",
                "altGR",
            ]
        )
        for key, value in keyCombos.items():
            mods = key[2]
            if value["base_key"] is not None:
                writer.writerow(
                    [
                        value["output"],
                        value["base_key"],
                        value["key_code"],
                        key[0],
                        "option" in mods,
                        "shift" in mods,
                        False,
                        False,
                    ]
                )

    with open(logsDir / "compositions.csv", "w", newline="", encoding="utf-8"
              ) as eCompositions:
        writer = csv.writer(eCompositions, lineterminator="\n")
        writer.writerow(["output_char", "apple_id", "steps"])
        for composition in compositions:
            steps = [[keyCode, sorted(mods)] for keyCode, mods in composition[2]]
            writer.writerow([composition[0], composition[1], json.dumps(steps)])

    with open(logsDir / "standardKeys.csv", "w", newline="", encoding="utf-8") as eSKeys:
        writer = csv.writer(eSKeys, lineterminator="\n")
        writer.writerow(["platform", "key_code", "enum"])
        keyCodes = {combo[1] for combo in keyCombos}
        for code in keyCodes:
            writer.writerow(["macOS", code, config.LAYOUT_DEPENDENCY.get(code)])

    with open(logsDir / "matchedNames.csv", "w", newline="", encoding="utf-8") as eMatch:
        writer = csv.writer(eMatch, lineterminator="\n")
        writer.writerow(["name", "apple_id", "source"])
        for name, value in matches.items():
            writer.writerow([name, value[0], value[1]])

    with open(logsDir / "noMatchNames.txt", "w", newline="", encoding="utf-8") as noMatch:
        for name in unMatches:
            noMatch.write(f"Keylayout: {name} had no match in the list of appleIDs\n")
