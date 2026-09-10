
-- QUERY for resetting the db data
TRUNCATE countries, languages, characters, letter_layouts, key_dependencies, layout_status, platforms, standard_keys, keyboard_layouts, key_combos RESTART IDENTITY CASCADE;

-- QUERY for resetting the db schema 
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;

-- Query for seeding schema and data
\i '~/Downloads/Projects/Keyboard Layouts/schema/schema.sql'
\i '~/Downloads/Projects/Keyboard Layouts/schema/seed.sql'

-- QUERY for answering "how to type •" on a specific keyboard

SELECT layout.id, base.character, combo.modify_opt_alt, combo.modify_shift, combo.modify_ctrl, combo.modify_altgr
FROM key_combos AS combo
JOIN characters AS out ON out.id = combo.output_char_id
JOIN keyboard_layouts AS layout ON layout.id = combo.keyboard_id
JOIN characters AS base ON base.id = combo.base_key_id
JOIN countries as c ON c.id = layout.country_id
WHERE out.character = 'Ğ'
AND c.native_name = 'Türkiye';

-- Query what does "combo" produce on "specific layout"
SELECT out.character
FROM key_combos AS combo
JOIN characters AS out ON out.id = combo.output_char_id
JOIN characters AS base ON base.id = combo.base_key_id
JOIN keyboard_layouts AS layout ON layout.id = combo.keyboard_id
WHERE layout.klo = 'm-da-DK'
AND combo.modify_shift = True
AND combo.modify_opt_alt = True
AND base.character = 'q';