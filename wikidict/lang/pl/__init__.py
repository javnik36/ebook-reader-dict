"""Polish language (polski)."""

import re
from typing import List, Pattern, Tuple

from ...user_functions import uniq, small_caps, strong

# Float number separator
float_separator = ","

# Thousads separator
thousands_separator = " "

# Markers for sections that contain interesting text to analyse.
head_sections = "{{język polski}}"
etyl_section = ("{{etymologia}}",)

section_patterns = (r"\:",)
section_level = 2
section_sublevels = (3,)


sections = (
    "{{znaczenia}}",
    *etyl_section,
    "{{odmiana}}",
)

variant_titles = (
    "{{odmiana"
)

variant_templates = ()

# Release content on GitHub
# https://github.com/BoboTiG/ebook-reader-dict/releases/tag/pl
release_description = """\
Liczba słów: {words_count}
Dump Wikisłownika z dnia: {dump_date}

Dostępne formaty słownika:

- [Kobo]({url_kobo}) (dicthtml-{locale}-{locale}.zip)
- [StarDict]({url_stardict}) (dict-{locale}-{locale}.zip)
- [DictFile]({url_dictfile}) (dict-{locale}-{locale}.df.bz2)

<sub>Ostatnia aktualizacja: {creation_date}.</sub>
"""  # noqa

# Dictionary name that will be printed below each definition
wiktionary = "Wikisłownik (ɔ) {year}"

# Some definitions are not good to keep (plural, gender, ... )
definitions_to_ignore = ()

# Templates to ignore: the text will be deleted.
templates_ignored = (
    "audio",
    "fakt", #odnośnik do brakującego źródła
    "Gloger",
    "homofony",
    "język linków", #odsyła linki poniżej do innego wiktionary
    "objaśnienie wymowy",
    "ortograficzny",
    "podobne",
    "nieodm-przymiotnik-polski",
    "niestopn",
    "wikipedia", #link do ~
    "wikicytaty", #link do ~
    "wikispecies", #link do ~
    "por", #porównaj (lista słów)
    "PoradniaPWN",
    "transkrypcja etymologii", #daje cytat o brakującej transkrypcji
    "zoblistę", #tworzy listę słów
    "zn-stperski", #1no użycie, żeby znaczki perskie były obrazkami - worth it?
)

# Templates that will be completed/replaced using italic style.
templates_italic = {
    #{{fm}}
    "fm": "forma męska",
    #{{fż}}
    "fż": "forma żeńska",
    #{{etc}}
    "etc": "et cetera",
}

# Templates more complex to manage.
templates_multi = {
    #{{stopn|szybciej|najszybciej}}
    "stopn": "f'{italic('stopień wyższy')} {parts[1]}; {italic('stopień najwyższy')} {parts[2]}'",
    #{{zob|[[słoń]], [[nosorożec]]}}
    #{{zob|słoń#pl|słoń}}
    "zob": "f'{italic('zobacz')} {parts[-1]}'",
    #{{skrócenie od|słoń}}
    "skrócenie od": "f'{italic('forma skrócona od')} {parts[-1]}'",
    #{{odczasownikowy od|nie|robić}}
    "odczasownikowy od": "f'{italic('rzeczownik odczasownikowy od')} {concat(parts[1:], ' ')}'",
    #{{odprzymiotnikowy od|łapczywy}}
    "odprzymiotnikowy od": "f'{italic('rzeczownik odprzymiotnikowy od')} {parts[-1]}'",
    #{{gw-pl|Poznań}}
    #{{gw-pl|Śląsk Cieszyński|[[polywka]]}}
    "gw-pl": "f'{italic('gwara, gwarowy')} {parenthesis(italic(parts[1]))}' + f' {parts[2]}' if len(parts)==3 else ''",
    #{{reg-pl|Poznań}}
    #{{reg-pl|Śląsk Cieszyński|[[polywka]]}}
    "reg-pl": "f'{italic('regionalizm, regionalny')} {parenthesis(italic(parts[1]))}' + f' {parts[2]}' if len(parts)==3 else ''",
    #{{plural|Cielętnik}} !it appears to be error in wiki (en only template used for pl words)
    "plural": "f'{italic('liczba mnoga od')} {parts[-1]}'",
    #{{dokonany od|opóźniać się}}
    "dokonany od": "f'{italic('aspekt dokonany od')} {parts[-1]}'",
    #{{niedokonany od|opóźniać się}}
    "niedokonany od": "f'{italic('aspekt niedokonany od')} {parts[-1]}'",
    #{{IPA2|ʧ}}
    "IPA2": "f'/{parts[-1]}/'",
    #{{IPA4|w}}
    "IPA4": "f'[{parts[-1]}]'",
    #{{źle|poszłem}} red?
    "źle": "strike(parts[-1])",
    #{{nie mylić z|poddawać}}
    #{{nie mylić z|březnový|marcowy}}
    "nie mylić z": "f'nie mylić z: {parts[1]}' + f' → {parts[2]}' if len(parts)==3 else ''",
    #{{*}}
    "*": "parenthesis('słowo rekonstruowane')",
    #{{pinyin}}
    #{{pinyin|yī běn shū}}
    #{{pinyin|yī běn shū|yi1 ben3 shu1}}
    "pinyin": "italic(parts[0]) + (f' {parts[1]}' if len(parts)==2 else '') + (f' {parenthesis(parts[2])}' if len(parts)==3 else '')",
    #{{forma przymiotnika|pl}}
    "forma przymiotnika": "italic('przymiotnik, forma fleksyjna')",
    #{{forma zaimka|pl}}
    "forma zaimka": "italic('zaimek, forma fleksyjna')",
    #{{forma czasownika|pl}}
    "forma czasownika": "italic('czasownik, forma fleksyjna')",
}

def find_genders(
    code: str,
    pattern: Pattern[str] = re.compile(r"\w+\,\srodzaj\s(\w+)"),
) -> List[str]:
    """
    >>> find_genders("")
    []
    >>> find_genders("rzeczownik, rodzaj nijaki")
    ['nijaki']
    """
    return uniq(pattern.findall(code))

def find_pronunciations(
    code: str) -> List[str]:
    """
    >>> find_pronunciations("")
    []
    >>> find_pronunciations(":{{IPA3|kɔt}}, {{AS3|kot}}")
    ['<span style='font-variant:small-caps'>IPA:</span> [kɔt]', '<span style='font-variant:small-caps'>AS:</span> [kot]']
    >>> find_pronunciations("{{wymowa}} {{audio|Pl-Szwecja.ogg}}, {{IPA3|ˈʃfɛʦ̑ʲja}}, {{AS3|šf'''e'''cʹi ̯a}}, {{objaśnienie wymowy|ZM|BDŹW}}")
    ['<span style='font-variant:small-caps'>IPA:</span> [ˈʃfɛʦ̑ʲja]', '<span style='font-variant:small-caps'>AS:</span> [šf<b>e</b>cʹi ̯a]']
    """  # noqa
    IPA_pattern = re.compile(r"{{IPA3\|([^}]+)}}")
    AS_pattern = re.compile(r"{{AS3\|([^}]+)}}")

    IPA_prons = [f"{small_caps('IPA:')} [{pron}]" for pron in uniq(IPA_pattern.findall(code))]
    AS_prons = []

    for pron in uniq(AS_pattern.findall(code)):
        pron = re.sub(r"\'\'\'([^']*)\'\'\'",strong("\1"),pron)
        AS_prons.append(f"{small_caps('AS:')} [{pron}]")

    return IPA_prons + AS_prons

def last_template_handler(template: Tuple[str, ...], locale: str, word: str = "") -> str:
    """
    Will be called in utils.py::transform() when all template handlers were not used.

    >>> last_template_handler(["default"], "de")
    '##opendoublecurly##default##closedoublecurly##'
    >>> last_template_handler(["fr."], "de")
    'französisch'
    >>> last_template_handler(["fr.", ":"], "de")
    'französisch:'
    >>> last_template_handler(["fr"], "de")
    'Französisch'
    """  # noqa
    from ...user_functions import italic
    from ..defaults import last_template_handler as default
    from .skr_all import skr_all, grammar_skr, inflection_skr, langs_skr, alias_skr
    from .template_handlers import lookup_template, render_template

    if skr_all_render := skr_all.get(template[0]):
        return italic(f"{skr_all_render}")
    
    if skr_grammar_render := grammar_skr.get(template[0]):
        return italic(f"{skr_grammar_render}")
    
    if skr_inflection_render := inflection_skr.get(template[0]):
        return italic(f"{skr_inflection_render}")
    
    manual_langs = {"warmia": "regionalizm warmiński",
                    "chin": "chiński",
                    "khm": "khmerski",
                    "białorus": "białoruski",
                    "łacina średniowieczna": "średniowiecznołaciński",
                    "prowans": "prowansalski"}
    
    if skr_lang_render := (langs_skr.get(template[0]) or alias_skr.get(template[0]) or manual_langs.get(template[0])):
        if len(template) > 1:
            return f"{italic(f'{skr_lang_render}')} {template[-1]}"
        else:
            return italic(f"{skr_lang_render}")
    
    if lookup_template(template[0]):
        return render_template(template)

    return default(template, locale, word=word)