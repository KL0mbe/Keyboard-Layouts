# Keyboard Character Lookup

A lookup tool that maps key combinations to the characters they produce across keyboard layouts and platforms. Ask "what does `Option` + `E` produce on a Danish Mac layout?" or "which keys produce `é` here?" and get an answer grounded in the layout data the OS actually ships.

## Why this exists

"What character does this key produce?" sounds trivial but isn't. The answer depends on the platform (macOS, Windows, even linx) the physical form factor (ANSI, ISO, JIS) the letter layout (qwerty, azerty, fgğıod) the active modifier layers (shift, command, shift+option) and dead-key primed state. Vendor layout data is inconsistent, sparsely documented, and encoded differently on every platform. This project models that complexity in a normalized database and builds the ingest pipeline that gets real OS layout data into it.

## Tech stack

- **Database:** PostgreSQL: 12-table normalized schema
- **Data pipeline:** Python: Apple `.keylayout` XML parser
- **Layout identity:** macOS TIS registry: extracted via a Swift script
- **Backend / API:** Go
- **Frontend:** React + TypeScript

## How it works

### Schema

Twelve tables, normalized to 3NF(minimum) each fact lives in one place instead of being duplicated across rows:

- **ANSI and ISO determined by the key code.** A nullable `required_standard_id` on each key combo flags only the keys where the two form factors actually diverge (e.g. the ISO-only `<` key). Combos shared by both are stored once.
- **Variants** are distinguished by a variant number plus a `layout_id` column, instead of baking letter-layout into the identifier. Determined by reading key codes 12-17 in the order (12, 13, 14, 15, 17, 16) as those represent the "qwerty" row.
- Derived and redundant columns were identified and removed during normalization.

### The KLO identifier

Every layout gets a stable identifier that bridges the gap between Windows KLID identifiers and Apple's `com.apple.keylayout.X` names. It's called the KLO Keyboard Layout Code(the O is the "o" in code, since KLC sounded too much like KFC) and takes the form `platform-lang-COUNTRY-variant`, fx `m-en-US-2`. Variant `0` is inferred when none is given. It encodes only immutable physical facts about a layout — notably, the ANSI/ISO standard is **not** part of the string. That distinction lives per-key-combo in the schema, since `.keylayout` files are standard-agnostic and rely solely on keycodes, so one identifier maps to one layout regardless of form factor.

### Data pipeline (macOS)

Real layout data is messy, so most of the work is ingest:

1. Parse Apple `.keylayout` XML files into key-combo → character mappings.
2. Source official layout IDs (`com.apple.keylayout.X`) from the macOS TIS registry, which is authoritative for layout identity. The layout files themselves are not.
3. Match parsed layouts to registry IDs by name (in two passes), handling identity edge cases such as legacy vs modern name collisions.
4. Resolve each layout's language/country, then assemble the KLO and the database rows in csv files.

## Queries

v2(macOS Beta) supports the core lookup end to end:

- **Character-name lookup**: given a character and country, return its localized name and the combos that produce it on all layouts for that country.

## Setup

```bash
# create and seed the database (adjust filenames to your repo)
createdb keyboards
psql keyboards < schema.sql
python parser.py
```

## Status & scope

**v2 (current):** Apple `.keylayout` data, base modifier layer, the two queries above.

Deliberately deferred to v3:

- Windows (MSKLC / KLC) layout track
- Modified (non-base) modifier layers
- OS-native key extraction via `UCKeyTranslate`
  Scope was drawn to ship something working over something complete.
