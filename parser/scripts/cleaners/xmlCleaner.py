import re

FORBIDDEN = re.compile(r"&#x([0-9A-Fa-f]+);")


def _strip(m):
    digit = int(m.group(1), 16)
    if digit < 0x20 or digit == 0x7F or digit in (0xFFFE, 0xFFFF):
        return ""
    return m.group(0)


def cleanLayout(file):
    raw = file.read_text(encoding="UTF-8")
    return FORBIDDEN.sub(_strip, raw)
