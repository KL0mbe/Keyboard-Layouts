import re

import config

FORBIDDEN = re.compile(r"&#x([0-9A-Fa-f]+);")


def _strip(m):
    digit = int(m.group(1), 16)
    if digit < 0x20 or digit == 0x7F:
        return ""
    return m.group(0)


path = config.parserDir / "Apple Keyboard Layouts"
for file in path.glob("*.keylayout"):
    # Skip Logitech layouts
    if file.name.startswith("Logitech"):
        continue
    raw = file.read_text(encoding="UTF-8")
    cleaned = FORBIDDEN.sub(_strip, raw)
    with open(config.parserDir / "Cleaned Apple Keyboard layouts" / file.name, "w", encoding="utf-8") as layout:
        layout.write(cleaned)
