from babel import Locale, localedata
import pycountry as pc
import config

en = Locale("en")


def extract_country_language(name, languages, countries):
    lang = pc.languages.lookup(config.LayoutLocale.get(name).get("language"))
    langAlpha = getattr(lang, "alpha_2", None) or lang.alpha_3
    locale = Locale(langAlpha)

    dictCountry = config.LayoutLocale.get(name).get("country")

    # extract languages for lang table
    languages[langAlpha] = {
        "name": lang.name,
        "native_name": locale.languages.get(langAlpha),
    }

    if dictCountry is not None:
        country = pc.countries.lookup(dictCountry)
        countryAlpha = country.alpha_2
    else:
        country = None
        countryAlpha = "X"

    # get Country Names
    nativeCountry = None
    if localedata.exists(langAlpha) and country is not None:
        nativeCountry = Locale(langAlpha).territories.get(
            countryAlpha, country.name
        )

    # extract countries for country table
    if countryAlpha != "X":
        englishCountry = en.territories.get(countryAlpha, country.name)
        countries[nativeCountry] = {
            "country": englishCountry,
            "iso": countryAlpha,
        }
    return langAlpha, countryAlpha, country, nativeCountry
