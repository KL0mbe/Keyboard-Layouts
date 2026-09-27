from pathlib import Path
import re

FORBIDDEN = re.compile(r"&#x([0-9A-Fa-f]+);")


def _strip(m):
    digit = int(m.group(1), 16)
    if digit < 0x20 or digit == 0x7F:
        return ""
    return m.group(0)


for file in Path("../Apple Keyboard Layouts/").glob("*.keylayout"):
    raw = file.read_text(encoding="UTF-8")
    cleaned = FORBIDDEN.sub(_strip, raw)
    with open(f"../Cleaned Apple Keyboard layouts/{file.name}", "w") as layout:
        layout.write(cleaned)
        layout.close()
