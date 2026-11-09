from babel import Locale, localedata
import pycountry as pc
import config

en = Locale("en")


def extract_country_language(appleID, languages, countries):
    cleanedID = config.clean_str(appleID.split(".")[-1])
    lang = pc.languages.lookup(config.LayoutLocale.get(cleanedID).get("language"))
    langAlpha = getattr(lang, "alpha_2", None) or lang.alpha_3
    hasLocale = localedata.exists(langAlpha)

    dictCountry = config.LayoutLocale.get(cleanedID).get("country")

    # extract languages for lang table
    native_name = Locale(langAlpha).languages.get(langAlpha) if hasLocale else None
    languages[langAlpha] = {
        "name": lang.name,
        "native_name": native_name,
    }

    if dictCountry is not None:
        country = pc.countries.lookup(dictCountry)
        countryAlpha = country.alpha_2
    else:
        country = None
        countryAlpha = "X"

    # get Country Names
    nativeCountry = None
    if hasLocale and country is not None:
        nativeCountry = Locale(langAlpha).territories.get(
            countryAlpha, country.name
        )

    # extract countries for country table
    if countryAlpha != "X":
        englishCountry = en.territories.get(countryAlpha, country.name)
        if nativeCountry is None:
            nativeCountry = englishCountry
        countries[nativeCountry] = {
            "country": englishCountry,
            "iso": countryAlpha,
        }
    return langAlpha, countryAlpha, country, nativeCountry
