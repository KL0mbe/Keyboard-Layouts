import unicodedata

CANON = {
    "anyShift": "shift",
    "shift": "shift",
    "leftShift": "shift",
    "rightShift": "shift",
    "anyOption": "option",
    "option": "option",
    "leftOption": "option",
    "rightOption": "option",
    "anyControl": "control",
    "control": "control",
    "rightControl": "control",
    "leftControl": "control",
    "command": "command",
    "caps": "caps",
}


TARGETS = (frozenset(), {"shift"}, {"option"}, {"shift", "option"})

LetterRow = [12, 13, 14, 15, 17, 16]

LetterLayouts = {
    "qwerty": "qwerty",
    "azerty": "azerty",
    "qwertz": "qwertz",
    "fgğıod": "fgğıod",
}

LayoutLocale = {
    "danish": {"language": "danish", "country": "denmark"},
    "hungarian": {"language": "hungarian", "country": "hungary"},
    "swedish": {"language": "swedish", "country": "sweden"},
    "icelandic": {"language": "icelandic", "country": "iceland"},
    "inuttitutnunavik": {"language": "inuktitut", "country": "canada"},
    "canadian": {"language": "english", "country": "canada"},
    "slovak": {"language": "slovak", "country": "slovakia"},
    "serbian-latin": {"language": "serbian", "country": "serbia"},
    "arabic-qwerty": {"language": "arabic", "country": None},
    "turkish": {"language": "turkish", "country": "türkiye"},
    "french-numerical": {"language": "french", "country": "france"},
    "portuguese": {"language": "portuguese", "country": "portugal"},
    "swissfrench": {"language": "french", "country": "switzerland"},
    "hebrew-qwerty": {"language": "hebrew", "country": None},
    "german": {"language": "german", "country": "germany"},
    "azeri": {"language": "azerbaijani", "country": "azerbaijan"},
    "russian": {"language": "russian", "country": "russian federation"},
    "norwegianextended": {"language": "norwegian", "country": "norway"},
    "ukrainian": {"language": "ukrainian", "country": "ukraine"},
    "faroese": {"language": "faroese", "country": "faroe islands"},
    "romanian": {"language": "romanian", "country": "romania"},
    "afghanuzbek": {"language": "uzbek", "country": "afghanistan"},
    "maori": {"language": "maori", "country": "new zealand"},
    "brazilian": {"language": "portuguese", "country": "brazil"},
    "estonian": {"language": "estonian", "country": "estonia"},
    "inuktitut-nunavut": {"language": "inuktitut", "country": "canada"},
    "australian": {"language": "english", "country": "australia"},
    "finnishextended": {"language": "finnish", "country": "finland"},
    "french": {"language": "french", "country": "france"},
    "inuktitut-qwerty": {"language": "inuktitut", "country": "canada"},
    "belgian": {"language": "dutch", "country": "belgium"},
    "lithuanian": {"language": "lithuanian", "country": "lithuania"},
    "italian-pro": {"language": "italian", "country": "italy"},
    "bulgarian": {"language": "bulgarian", "country": "bulgaria"},
    "italian": {"language": "italian", "country": "italy"},
    "byelorussian": {"language": "belarusian", "country": "belarus"},
    "afghanpashto": {"language": "pushto", "country": "afghanistan"},
    "spanish": {"language": "spanish", "country": None},
    "armenian-hmqwerty": {"language": "armenian", "country": "armenia"},
    "greek": {"language": "el", "country": "greece"},
    "spanish-iso": {"language": "spanish", "country": None},
    "finnish": {"language": "finnish", "country": "finland"},
    "hebrew": {"language": "hebrew", "country": None},
    "thai": {"language": "thai", "country": "thailand"},
    "greekpolytonic": {"language": "el", "country": "greece"},
    "swissgerman": {"language": "german", "country": "switzerland"},
    "gurmukhi-qwerty": {"language": "panjabi", "country": "india"},
    "austrian": {"language": "german", "country": "austria"},
    "us": {"language": "english", "country": "united states"},
    "gurmukhi": {"language": "panjabi", "country": "india"},
    "macedonian": {"language": "macedonian", "country": "north macedonia"},
    "latvian": {"language": "latvian", "country": "latvia"},
    "usextended": {"language": "english", "country": "united states"},
    "thai-pattachote": {"language": "thai", "country": "thailand"},
    "slovenian": {"language": "slovenian", "country": "slovenia"},
    "devanagari-qwerty": {"language": "hindi", "country": "india"},
    "norwegian": {"language": "norwegian", "country": "norway"},
    "irishextended": {"language": "irish", "country": "ireland"},
    "swedish-pro": {"language": "swedish", "country": "sweden"},
    "inuktitut-nutaaq": {"language": "inuktitut", "country": "canada"},
    "canadian-csa": {"language": "french", "country": "canada"},
    "persian-isiri2901": {"language": "persian", "country": "iran"},
    "gujarati": {"language": "gujarati", "country": "india"},
    "serbian": {"language": "serbian", "country": "serbia"},
    "czech-qwerty": {"language": "czech", "country": "czech republic"},
    "dutch": {"language": "dutch", "country": "netherlands"},
    "devanagari": {"language": "hindi", "country": "india"},
    "persian": {"language": "persian", "country": "iran"},
    "northernsami": {"language": "northern sami", "country": None},
    "nepali": {"language": "ne", "country": "nepal"},
    "armenian-westernqwerty": {"language": "armenian", "country": "armenia"},
    "cherokee-nation": {"language": "cherokee", "country": "united states"},
    "bulgarian-phonetic": {"language": "bulgarian", "country": "bulgaria"},
    "cherokee-qwerty": {"language": "cherokee", "country": "united states"},
    "polish": {"language": "polish", "country": "poland"},
    "british": {"language": "english", "country": "united kingdom"},
    "irish": {"language": "irish", "country": "ireland"},
    "arabic": {"language": "arabic", "country": None},
    "vietnamese": {"language": "vietnamese", "country": "vietnam"},
    "turkish-qwerty-pc": {"language": "turkish", "country": "türkiye"},
    "czech": {"language": "czech", "country": "czech republic"},
    "turkish-qwerty": {"language": "turkish", "country": "türkiye"},
    "croatian": {"language": "croatian", "country": "croatia"},
    "welsh": {"language": "welsh", "country": "united kingdom"},
    "gujarati-qwerty": {"language": "gujarati", "country": "india"},
    "afghandari": {"language": "persian", "country": "afghanistan"},
    "russian-phonetic": {"language": "russian", "country": "russian federation"},
    "hawaiian": {"language": "hawaiian", "country": "united states"},
    "polishpro": {"language": "polish", "country": "poland"},
}


def get_unicode_char_data(char):
    if not char or len(char) > 1:
        return {"character": char, "code_point": None, "unicode_name": None}

    return {
        "character": char,
        "code_point": f"U+{ord(char):04X}",
        "unicode_name": unicodedata.name(char, None),
    }


def clean_str(string):
    return (
        string.replace("—", "-")
        .replace("–", "-")
        .replace(".", "")
        .replace(" ", "")
        .lower()
        .strip()
    )  # strip gets rid of \n
