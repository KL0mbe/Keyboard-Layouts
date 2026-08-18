from pathlib import Path

path = Path("/Users/klombe/Downloads/Projects/Keyboard Layouts/Apple Keyboard Layouts")

destination = Path("/Users/klombe/Downloads/Projects/Keyboard Layouts/layoutNames.txt")
with open(destination, "a", encoding="utf-8") as dest:
    for file in Path(path).glob("*.keylayout"):
        dest.write(f"{file.name}\n")
        print(file.name)
    dest.close()

