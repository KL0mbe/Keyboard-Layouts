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


TARGETS = (set(), {"shift"}, {"option"}, {"shift", "option"})


def clean_str(string):
    return (
        string.replace("—", "-")
        .replace("–", "-")
        .replace(".", "")
        .replace(" ", "")
        .lower()
        .strip()
    )  # strip gets rid of \n
