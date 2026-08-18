
BEGIN;

INSERT INTO countries(country, iso_3166) VALUES('Denmark', 'DK'), ('United States', 'US'), ('United Kingdom', 'GB');

INSERT INTO languages(name, iso_639) VALUES('english', 'en'), ('dansk', 'da'), ('française', 'fr');

INSERT INTO letter_layouts(name) VALUES('qwerty'), ('azerty'), ('qwertz');

INSERT INTO layout_standards(name) VALUES('ISO'), ('ANSI'), ('DVORAK');

INSERT INTO layout_status(status) VALUES('active'), ('legacy'), ('deprecated');

INSERT INTO platforms(name) VALUES('macOS'), ('Windows'), ('Linux');

INSERT INTO characters(character, unicode, unicode_name) VALUES(':', 'U+003A', 'colon'), ('•', 'U+2022','bullet'), (';', 'U+003B', 'semicolon');

INSERT INTO character_names(name, char_id, language_id) VALUES ('colon', 1, 1), ('deux-points', 1, 3), ('semikolon', 3, 2);

INSERT INTO keyboard_layouts(platform_id, language_id, country_id, layout_id, standard_id, klo, klo1, klid, apple_id, cldr, os_version, status_id) 
VALUES(1, 2, 1, 1, 1, 'm-da-DK-i', 'm-da-DK-i-q', NULL, 'com.apple.keylayout.danish', 'da-t-k0-osx', NULL, 1);

INSERT INTO key_combos(output_char_id, base_key, keyboard_id, modify_opt_alt, modify_shift, modify_ctrl, modify_altgr)
VALUES (1, '.', 1, FALSE, TRUE, FALSE, FALSE), (2, 'q', 1, TRUE, TRUE, FALSE, FALSE), (3, ',', 1, FALSE, TRUE, FALSE, FALSE);

COMMIT;