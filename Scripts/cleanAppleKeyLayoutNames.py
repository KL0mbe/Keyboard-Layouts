from pathlib import Path
import config

file = Path("../TISNames/TestLayouts.tsv")


def build_apple_id_dict():
    tisNames = {}

    with open(file, "r") as f:
        for line in f:
            parts = line.split("\t")
            layoutName = config.clean_str(parts[1])
            appleId = parts[0]
            tisNames[layoutName] = appleId
    return tisNames


def build_apple_id_suffix():
    appleIds = {}
    with open(file, "r") as f:
        for line in f:
            parts = line.split("\t")
            appleId = parts[0]
            suffix = config.clean_str(appleId.split(".")[-1])
            appleIds[suffix] = appleId
    return appleIds
