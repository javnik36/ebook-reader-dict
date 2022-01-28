"""Deutsh language."""

# Regex to find the pronunciation
pronunciation = r"{{Lautschrift\|([^}]+)}}"

# Regex to find the gender
gender = r",\s+{{([fmn]+)}}"

# Float number separator
float_separator = "."

# Thousads separator
thousands_separator = ","

# Markers for sections that contain interesting text to analyse.
head_sections = ("{{Sprache|Deutsch}}", "{{sprache|deutsch}}")
etyl_section = ("{{Herkunft}}",)
sections = (
    *etyl_section,
    "{{Bedeutungen}",
)

# Some definitions are not good to keep (plural, gender, ... )
definitions_to_ignore = ()

# Templates to ignore: the text will be deleted.
templates_ignored = ()

# Templates that will be completed/replaced using italic style.
# templates_italic = {}

# Templates more complex to manage.
templates_multi = {
    # {{Ü|pl|dzień}}
    "Ü": "italic(parts[-1])",
}

# Release content on GitHub
# https://github.com/BoboTiG/ebook-reader-dict/releases/tag/de
release_description = """\
Words count: {words_count}
Wiktionary dump: {dump_date}

Available files:

- [Kobo]({url_kobo}) (dicthtml-{locale}-{locale}.zip)
- [StarDict]({url_stardict}) (dict-{locale}-{locale}.zip)
- [DictFile]({url_dictfile}) (dict-{locale}-{locale}.df)

<sub>Updated on {creation_date}</sub>
"""  # noqa

# Dictionary name that will be printed below each definition
wiktionary = "Wiktionary (ɔ) {year}"
