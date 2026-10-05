# Keyboard Character Lookup

A lookup tool that maps key combinations to the characters they produce across keyboard layouts and platforms. Ask "what does `Option` + `e` produce on a Danish Mac layout?" or "which keys produce `ô` here?" and get an answer grounded in the layout data the OS actually ships.

## Why this exists

"What character does this key produce?" sounds trivial but isn't. The answer depends on the platform (macOS, Windows and Linux), the physical form factor (ANSI, ISO, JIS), the letter layout (qwerty, azerty, qwertz, fgğıod,...), the active modifier layers (shift, command, shift+option,...), and dead-key primed state. Vendor layout data is inconsistent, sparsely documented, and encoded differently on every platform. This project models that complexity in a normalized database and builds the ingest pipeline that gets real OS layout data into it.

## Tech stack

- **Database:** PostgreSQL: 12-table normalized schema
- **Data pipeline:** Python: Apple `.keylayout` XML parser
- **Layout identity:** macOS TIS registry: extracted via a Swift script
- **Backend / API:** Go
- **Frontend:** React + TypeScript, lives at [klombe.com/keyboards](https://klombe.com/keyboards), [Source](https://github.com/KL0mbe/KL0mbe.github.io)
- **Deployment:** Docker Compose, self hosted behind a Cloudflare Tunnel (running the stack locally does not require Cloudflare tunnel)

## How it works

### Schema

Twelve tables, normalized to 3NF (minimum), each fact lives in one place instead of being duplicated across rows:

- **ANSI and ISO are determined by the key code.** A nullable `required_standard_id` on each key combo flags only the keys where the two form factors actually diverge (e.g. the ISO-only `<` key). Combos shared by both are stored once.
- **Variants** are distinguished by a variant number plus a `layout_id` column, instead of baking letter-layout into the identifier. Determined by reading key codes 12-17 in the order (12, 13, 14, 15, 17, 16) as those represent the "qwerty" row.
- **Dead Keys** are modeled as `compositions` and not `key_combos`, instead the outputs that involve dead keys are. Using ordered `composition_steps`, each pointing to an existing row in `key_combos`. A dead key press like `Shift + ¨` is stored once and reused as the first step of every composition it starts (Ä, ö, ë, ...). Chained dead keys are simply more steps.
- Derived and redundant columns were identified and removed during normalization.

### The KLO identifier

Every layout gets a stable identifier that bridges the gap between Windows KLID identifiers and Apple's `com.apple.keylayout.X` names. It's called the KLO Keyboard Layout Code (the O is the "o" in code, since KLC sounded too much like KFC) and takes the form `platform-lang-COUNTRY-variant`, e.g. `m-en-US-2`. Variant `0` is inferred when none is given. It encodes only immutable physical facts about a layout — notably, the ANSI/ISO standard is **not** part of the string. That distinction lives per-key-combo in the schema, since `.keylayout` files are standard-agnostic and rely solely on keycodes, so one identifier maps to one layout regardless of form factor.

### Data pipeline (macOS)

Real layout data is messy, so most of the work is ingest:

1. Parse Apple `.keylayout` XML files into key-combo → character mappings.
2. Resolve each layout's dead key state (\<actions>, \<when state=...>, \<terminators>) into ordered multi step sequences, including chained dead key compositions.
3. Source official layout IDs (`com.apple.keylayout.X`) from the macOS TIS registry, which is authoritative for layout identity. The layout files themselves are not.
4. Match parsed layouts to registry IDs by name (in two passes), handling identity edge cases such as legacy vs modern name collisions.
5. Resolve each layout's language/country, then assemble the KLO and the database rows in csv files.

## Queries

v2 (macOS Beta) supports the core lookup end to end:

- **Character-name lookup**: given a character and country, return its native name and every way to produce it on that country's layouts, both single combos(shift+q -> Q) as well as multi stage dead key compositions(option+¨, then shift + A -> Ã).

## Setup

The stack runs in Docker: a Postgres container (schema and seed applied automatically on first startup) and the Go API container.

### Prerequisites

- Docker and Docker Compose

### Configuration

Copy the `.env.example` into a `.env` file and fill in your own username and password for the Postgres db.

```bash
POSTGRES_USER=username
POSTGRES_PASSWORD=password
```

### Run

```bash
docker compose up -d --build
```

On first start, Postgres runs the schema and seeds automatically from `db/` and `logs/` populating the database into a `pgdata` volume. The API is then available on port 8080.

To wipe and reseed from scratch including the data volume:

```bash
docker compose down -v && docker compose up -d --build
```

### API usage

**All responses are application/json. Both endpoints are GET-only.**

Two GET endpoints are exposed at `api.klombe.com` (`http://localhost:8080` when running locally).

**1. List countries** returns every country's English name, native name and iso_3166 code.

    GET /countries

Example:
`curl 'https://api.klombe.com/countries'`

Response:

```json
[
    {
        "country": "Hungary",
        "id": 2,
        "iso_3166": "HU",
        "native_name": "Magyarország"
    },
    {
        "country": "Canada",
        "id": 5,
        "iso_3166": "CA",
        "native_name": "ᑲᓇᑕᒥ"
    },
    {
        "country": "Canada",
        "id": 6,
        "iso_3166": "CA",
        "native_name": "Canada"
    },...
]
```

The `native_name` is what endpoint 2 expects as the `country` param.

**2. Lookup combos** given `char`(the character to produce) and `country`(the native name from `/countries`), returns all ways to produce that character on that country's layouts, including multi step dead-key compositions.

    GET /?char=<character>&country=<native_name>

Both params must be URL encoded e.g. ñ -> %C3%B1. Browsers do this automatically but not so with curl and other CLI tools.

Example:
`curl 'https://api.klombe.com/?char=%C3%B1&country=Danmark'`

Response:

```json
{
  "single": [
    {
      "character": "n",
      "display_name": "Dansk",
      "id": 64,
      "modify_altgr": false,
      "modify_ctrl": false,
      "modify_opt_alt": true,
      "modify_shift": false
    }
  ],
  "compositions": [
    {
      "base_char": "n",
      "composition_id": 7167,
      "display_name": "Dansk",
      "layout_id": 64,
      "modify_opt_alt": false,
      "modify_shift": false,
      "output_char": "ñ",
      "step": 2
    },
    {
      "base_char": "¨",
      "composition_id": 7167,
      "display_name": "Dansk",
      "layout_id": 64,
      "modify_opt_alt": true,
      "modify_shift": false,
      "output_char": "ñ",
      "step": 1
    }
  ]
}
```

- `single` lists key combos that produce the character in one press.
- `compositions` lists multi step dead key sequences. Group entries by
  `composition_id` and order by `step` to reconstruct each recipe the example above is one composition: press `Option + ¨` (step 1), then press `n` (step 2) to get `ñ`.
- `display_name` is the layout's human readable name, `layout_id` or `id` is its numeric key from the Postgres database.

**Errors**:

- Missing params returns 400 Bad Request with plain text message `Missing parameters`.
- DB failure returns 500 Internal Server Error with plain text message e.g. `Countries Query failed`.
- Unknown `country` or a `char` with no matches returns 200 OK with empty arrays `{"single":[], "compositions":[]}`

### Regenerating layout data

The CSVs in `logs/` are committed and up to date. No need to run the parser to produce them. To regenerate them from source `.keylayout` files:

```bash
pip install babel pycountry
cd parser/scripts
python3 -m macParser.keylayoutParser
```

## Status & scope

**v2 (current):** Apple `.keylayout` data, shift and option modifier layers, dead key compositions and the query above.

Deliberately deferred to v3:

- Windows (MSKLC / KLC) layout track
- Linux layout track
- OS-native key extraction via `UCKeyTranslate`

Scope was drawn to ship something working over something complete.
