
-- QUERY for resetting the db data
TRUNCATE countries, languages, letter_layouts, layout_standards, layout_status, platforms, characters, keyboard_layouts RESTART IDENTITY CASCADE;

-- Query for seeding schema and data
\i '~/Downloads/Projects/Keyboard Layouts/schema/schema.sql'
\i '~/Downloads/Projects/Keyboard Layouts/schema/seed.sql'

-- QUERY for answering "how to type •" on a specific keyboard
-- c.character = "•" is the user input and the keyboard kl.klo = "m-da-DK-i" is the one they select

SELECT kc.base_key, kc.modify_opt_alt, kc.modify_shift, kc.modify_ctrl, kc.modify_altgr
FROM key_combos kc
JOIN characters c ON kc.output_char_id = c.id
JOIN keyboard_layouts kl ON KC.keyboard_id = kl.id
WHERE c.character = '•' AND kl.klo = 'm-da-DK-i';


-- Query for answering "whats the name for :" in french
-- the c.character == : is the user inputed character and the l.iso_639 == fr is the user selected language
SELECT cn.name
FROM character_names cn
JOIN characters c ON cn.char_id = c.id
JOIN languages l ON cn.language_id = l.id
WHERE c.character = ':' AND l.iso_639 = 'fr';