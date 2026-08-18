
CREATE TABLE countries(
id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
country TEXT NOT NULL UNIQUE,
iso_3166 TEXT NOT NULL UNIQUE
);

CREATE TABLE languages(
id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
name TEXT NOT NULL UNIQUE,
iso_639 TEXT NOT NULL UNIQUE
);

CREATE TABLE characters(
id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
character TEXT NOT NULL UNIQUE,
unicode TEXT NOT NULL UNIQUE,
unicode_name TEXT NOT NULL UNIQUE
);

CREATE TABLE letter_layouts(
id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
name TEXT NOT NULL UNIQUE
);

CREATE TABLE layout_standards(
id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
name TEXT NOT NULL UNIQUE
);

CREATE TABLE layout_status(
id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
status TEXT NOT NULL UNIQUE
);

CREATE TABLE platforms(
id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
name TEXT NOT NULL UNIQUE
);


CREATE TABLE character_names(
id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
name TEXT NOT NULL,
char_id INTEGER NOT NULL REFERENCES characters(id),
language_id INTEGER NOT NULL REFERENCES languages(id),
created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
modified_at TIMESTAMPTZ NOT NULL DEFAULT now(),
UNIQUE(char_id, language_id)
);

CREATE TABLE keyboard_layouts(
id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
platform_id INTEGER NOT NULL REFERENCES platforms(id),
language_id INTEGER NOT NULL REFERENCES languages(id),
country_id INTEGER NOT NULL REFERENCES countries(id),
layout_id INTEGER NOT NULL REFERENCES letter_layouts(id),
standard_id INTEGER NOT NULL REFERENCES layout_standards(id),
status_id INTEGER NOT NULL REFERENCES layout_status(id),
klo TEXT NOT NULL UNIQUE,
klo1 TEXT NOT NULL UNIQUE, -- with the letter layout in the code until i can decide which is better
klid TEXT,
apple_id TEXT,
cldr TEXT,
os_version TEXT,
created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
modified_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE key_combos(
id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
output_char_id INTEGER NOT NULL REFERENCES characters(id),
keyboard_id INTEGER NOT NULL REFERENCES keyboard_layouts(id),
base_key TEXT NOT NULL,
modify_opt_alt BOOL NOT NULL,
modify_shift BOOL NOT NULL,
modify_ctrl BOOL NOT NULL,
modify_altgr BOOL NOT NULL,
created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
modified_at TIMESTAMPTZ NOT NULL DEFAULT now(),
UNIQUE(base_key, keyboard_id, modify_opt_alt, modify_shift, modify_ctrl, modify_altgr)
);

CREATE INDEX ON key_combos(keyboard_id, output_char_id);

