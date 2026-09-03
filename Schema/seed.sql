
BEGIN;

TRUNCATE countries, languages, characters, letter_layouts, key_dependencies, layout_status, platforms, standard_keys, keyboard_layouts, key_combos RESTART IDENTITY CASCADE;


\set content `cat "/Users/klombe/Downloads/Projects/Keyboard Layouts/Scripts/constants.json"`

INSERT INTO platforms (name)
SELECT * FROM jsonb_array_elements_text(:'content'::jsonb -> 'platforms');

INSERT INTO letter_layouts (name)
SELECT * FROM jsonb_object_keys(:'content'::jsonb -> 'letter_layouts');

INSERT INTO layout_status (status)
SELECT * FROM jsonb_array_elements_text(:'content'::jsonb -> 'layout_status');

INSERT INTO key_dependencies (enum)
SELECT * FROM jsonb_array_elements_text(:'content'::jsonb -> 'key_dependencies');

INSERT INTO countries(country, native_name, iso_3166)
VALUES('X','X','X');


INSERT INTO standard_keys (platform_id, key_code, enum_id)
SELECT p.id, skey.key_code, keydep.id
FROM jsonb_to_recordset(:'content'::jsonb -> 'standard_keys') AS skey(key_code INTEGER, dependency TEXT, platform TEXT)
JOIN platforms AS p ON p.name = skey.platform
JOIN key_dependencies AS keydep ON keydep.enum = skey.dependency;


COPY countries(country, native_name, iso_3166) FROM '/Users/klombe/Downloads/Projects/Keyboard Layouts/logs/countries.csv' WITH (FORMAT csv, HEADER true);

COPY languages (name, native_name, iso_639) FROM '/Users/klombe/Downloads/Projects/Keyboard Layouts/logs/languages.csv' WITH (FORMAT csv, HEADER true);

COPY characters (character, unicode_code, unicode_name) FROM '/Users/klombe/Downloads/Projects/Keyboard Layouts/logs/characters.csv' WITH (FORMAT csv, HEADER true);


CREATE TEMP TABLE IF NOT EXISTS keyboard_staging(
platform TEXT NOT NULL,
language TEXT NOT NULL,
country TEXT NOT NULL,
layout TEXT NOT NULL,
status TEXT NOT NULL,
klo TEXT NOT NULL UNIQUE,
klid TEXT UNIQUE,
apple_id TEXT UNIQUE
) ON COMMIT DROP;

COPY keyboard_staging FROM '/Users/klombe/Downloads/Projects/Keyboard Layouts/logs/layouts.csv' WITH (FORMAT csv, HEADER true);

INSERT INTO keyboard_layouts (platform_id, language_id, country_id, layout_id, status_id, klo, klid, apple_id)
SELECT p.id, lang.id, c.id, lay.id, st.id, staging.klo, staging.klid, staging.apple_id
FROM keyboard_staging AS staging
JOIN platforms AS p ON p.name = staging.platform
JOIN languages AS lang ON lang.iso_639 = staging.language
JOIN countries AS c ON c.native_name = staging.country
JOIN letter_layouts AS lay ON lay.name = staging.layout
JOIN layout_status AS st ON st.status = staging.status;

CREATE TEMP TABLE IF NOT EXISTS combos_staging(
output_char TEXT NOT NULL,
base_key TEXT NOT NULL,  
apple_id TEXT NOT NULL,
key_code TEXT,
opt_alt BOOL NOT NULL,
shift BOOL NOT NULL,
ctrl BOOL NOT NULL,
altgr BOOL NOT NULL
) ON COMMIT DROP;

COPY combos_staging FROM '/Users/klombe/Downloads/Projects/Keyboard Layouts/logs/combos.csv' WITH (FORMAT csv, HEADER true);

INSERT INTO key_combos (output_char_id, base_key_id, keyboard_id, key_code_id, modify_opt_alt, modify_shift, modify_ctrl, modify_altgr)
SELECT char.id, base.id, keyboard.id, skey.id, cs.opt_alt, cs.shift, cs.ctrl, cs.altgr
FROM combos_staging AS cs
JOIN characters AS char ON char.character = cs.output_char
JOIN characters AS base ON base.character = cs.base_key
JOIN keyboard_layouts AS keyboard ON keyboard.apple_id = cs.apple_id
LEFT JOIN standard_keys AS skey ON skey.key_code = CAST (cs.key_code AS INTEGER)
AND skey.platform_id = keyboard.platform_id
ON CONFLICT DO NOTHING;





-- INSERT INTO character_names(name, char_id, language_id) VALUES ('colon', 1, 1), ('deux-points', 1, 3), ('semikolon', 3, 2);

-- INSERT INTO key_combos(output_char_id, base_key, keyboard_id, modify_opt_alt, modify_shift, modify_ctrl, modify_altgr)
-- VALUES (1, '.', 1, FALSE, TRUE, FALSE, FALSE), (2, 'q', 1, TRUE, TRUE, FALSE, FALSE), (3, ',', 1, FALSE, TRUE, FALSE, FALSE);

COMMIT;