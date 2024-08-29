"""Render templates from raw data."""

import json
import multiprocessing
import os
import re
from collections import defaultdict
from functools import partial
from itertools import chain
from pathlib import Path
from typing import Callable, Dict, List, Pattern, Tuple, cast

import wikitextparser as wtp
import wikitextparser._spans

from .lang import (
    definitions_to_ignore,
    etyl_section,
    find_genders,
    find_pronunciations,
    head_sections,
    section_level,
    section_patterns,
    section_sublevels,
    sections,
    sublist_patterns,
    variant_templates,
    variant_titles,
)
from .stubs import Definitions, SubDefinitions, Word, Words
from .utils import process_templates, table2html, uniq, transform_grammar_template

# As stated in wikitextparser._spans.parse_pm_pf_tl():
#   If the byte_array passed to parse_to_spans contains n WikiLinks, then
#   this function will be called n + 1 times. One time for the whole byte_array
#   and n times for each of the n WikiLinks.
#
# We do not care about links, let's speed-up the all process by skipping the n times call.
# Doing that is a ~30% optimization.
wikitextparser._spans.WIKILINK_PARAM_FINDITER = lambda *_: ()


Sections = Dict[str, List[wtp.Section]]

# Multiprocessing shared globals, init in render() see #1054
MANAGER = ""
LOCK = multiprocessing.Lock()
MISSING_TPL_SEEN: List[str] = []


def find_definitions(word: str, parsed_sections: Sections, locale: str) -> List[Definitions]:
    """Find all definitions, without eventual subtext."""
    definitions = list(
        chain.from_iterable(
            find_section_definitions(word, section, locale)
            for sections in parsed_sections.values()
            for section in sections
        )
    )
    if not definitions:
        return []

    # Remove duplicates
    seen = set()
    return [d for d in definitions if not (d in seen or seen.add(d))]  # type: ignore


def es_replace_defs_list_with_numbered_lists(
    lst: wtp.WikiList,
    regex_item: Pattern[str] = re.compile(
        r"(^|\\n);\d+[ |:]+",
        flags=re.MULTILINE,
    ),
    regex_subitem: Pattern[str] = re.compile(
        r"(^|\\n):;\s*[a-z]:+\s+",
        flags=re.MULTILINE,
    ),
) -> str:
    """
    ES uses definition lists, not well supported by the parser...
    replace them by numbered lists.
    """
    res = regex_item.sub(r"\1# ", lst.string)
    return regex_subitem.sub(r"\1## ", res)


def find_section_definitions(word: str, section: wtp.Section, locale: str) -> List[Definitions]:
    """Find definitions from the given *section*, with eventual sub-definitions."""
    definitions: List[Definitions] = []

    # do not look for definitions in french verb form section
    if locale == "fr" and section.title.strip().startswith("{{S|verbe|fr|flexion"):
        return definitions

    if locale == "es" and section.title.strip().startswith(("Forma adjetiva", "Forma verbal")):
        return definitions

    if locale == "es" and (lists := section.get_lists(pattern="[:;]")):
        section.contents = "".join(es_replace_defs_list_with_numbered_lists(lst) for lst in lists)

    if locale == "pl" and section.title.strip().startswith("{{odmiana"):
        return definitions

    if lists := section.get_lists(pattern=section_patterns[locale]):
        for a_list in lists:
            for idx, code in enumerate(a_list.items):
                # Ignore some patterns
                if any(ignore_me in code.lower() for ignore_me in definitions_to_ignore[locale]):
                    continue

                # Transform and clean the Wikicode
                definition = process_templates(word, code, locale)

                # Skip empty definitions
                # [SV] Skip almost empty definitions
                if not definition or (locale == "sv" and len(definition) < 2):
                    continue

                # Keep the definition ...
                definitions.append(definition)

                # ... And its eventual sub-definitions
                subdefinitions: List[SubDefinitions] = []
                for sublist in a_list.sublists(i=idx, pattern=sublist_patterns[locale]):
                    for idx2, subcode in enumerate(sublist.items):
                        subdefinition = process_templates(word, subcode, locale)
                        if not subdefinition:
                            continue

                        subdefinitions.append(subdefinition)
                        subsubdefinitions: List[str] = []
                        for subsublist in sublist.sublists(i=idx2, pattern=sublist_patterns[locale]):
                            for subsubcode in subsublist.items:
                                if subsubdefinition := process_templates(word, subsubcode, locale):
                                    subsubdefinitions.append(subsubdefinition)
                        if subsubdefinitions:
                            subdefinitions.append(tuple(subsubdefinitions))
                if subdefinitions:
                    definitions.append(tuple(subdefinitions))

    return definitions


def find_etymology(word: str, locale: str, parsed_section: wtp.Section) -> List[Definitions]:
    """Find the etymology."""
    definitions: List[Definitions] = []
    etyl: str

    if locale in {"ca", "no"}:
        definitions.append(process_templates(word, parsed_section.contents, locale))
        return definitions

    elif locale == "en":
        items = [
            item
            for item in parsed_section.get_lists(pattern=("",))[0].items
            if not item.lstrip().startswith(("===Etymology", "{{PIE root"))
        ]
        for item in items:
            if etyl := process_templates(word, item, locale):
                definitions.append(etyl)
        return definitions

    elif locale in {"es", "it", "ro"}:
        items = [item.strip() for item in parsed_section.get_lists(pattern=("",))[0].items[1:]]
        for item in items:
            if (etyl := process_templates(word, item, locale)) and etyl != ".":
                definitions.append(etyl)
        return definitions

    elif locale == "pt":
        section_title = parsed_section.title.strip()
        if section_title == "{{etimologia|pt}}":
            try:
                etyl = parsed_section.get_lists()[0].items[0]
            except IndexError:
                etyl = parsed_section.get_lists(pattern=("",))[0].items[1]
        else:
            # "Etimologia" title section
            try:
                etyl = parsed_section.get_lists(pattern=("^:",))[0].items[0]
            except IndexError:
                etyl = parsed_section.get_lists(pattern=("",))[0].items[1]
        definitions.append(process_templates(word, etyl, locale))
        return definitions
    elif locale == "ru":
        section_title = parsed_section.title.strip()
        if section_title == "Этимология":
            definitions.append(process_templates(word, parsed_section.contents, locale))
        return definitions
    elif locale == "da":
        section_title = parsed_section.title.strip()
        if section_title in {"{{etym}}", "Etymologi"}:
            definitions.append(process_templates(word, parsed_section.contents, locale))
        return definitions

    tables = parsed_section.tables
    tableindex = 0
    for section in parsed_section.get_lists():
        for idx, section_item in enumerate(section.items):
            if any(ignore_me in section_item.lower() for ignore_me in definitions_to_ignore[locale]):
                continue
            if section_item == ' {| class="wikitable"':
                phrase = table2html(word, locale, tables[tableindex])
                definitions.append(phrase)
                tableindex += 1
            else:
                definitions.append(process_templates(word, section_item, locale))
                subdefinitions: List[SubDefinitions] = []
                for sublist in section.sublists(i=idx):
                    subdefinitions.extend(process_templates(word, subcode, locale) for subcode in sublist.items)

                if subdefinitions:
                    definitions.append(tuple(subdefinitions))

    return definitions


def _find_genders(top_sections: List[wtp.Section], func: Callable[[str], List[str]]) -> List[str]:
    """Find the genders."""
    for top_section in top_sections:
        if result := func(top_section.contents):
            return result
    return []


def _find_pronunciations(top_sections: List[wtp.Section], func: Callable[[str], List[str]]) -> List[str]:
    """Find pronunciations."""
    results = []
    for top_section in top_sections:
        if result := func(top_section.contents):
            results.extend(result)
    return sorted(uniq(results))


def find_all_sections(code: str, locale: str) -> Tuple[List[wtp.Section], List[Tuple[str, wtp.Section]]]:
    """Find all sections holding definitions."""
    parsed = wtp.parse(code)
    all_sections = []
    level = section_level[locale]

    # Add fake section for etymology if in the leading part
    if locale == "ca":
        etyl_data = etyl_data_section = leading_lines = ""
        etyl_l_sections = etyl_section[locale]

        leading_part = parsed.get_sections(include_subsections=False, level=level)
        if leading_part:
            leading_lines = leading_part[0].contents.split("\n")

        for etyl_l_section in etyl_l_sections:
            for line in leading_lines:
                if line.startswith(etyl_l_section):
                    etyl_data = line
                    etyl_data_section = etyl_l_section
                    break

        if etyl_data:
            all_sections.append(
                (
                    etyl_data_section,
                    wtp.Section(f"=== {etyl_data_section} ===\n{etyl_data}"),
                )
            )

    def section_title(title: str) -> str:
        if locale == "de":
            title = title.split("(")[-1].strip(" )")
        if locale == "pl":
            # kot ({{język X}}) => {{język X}}
            return title.split("(")[-1].strip(" )")
        return title.replace(" ", "").lower().strip() if title else ""

    # Get interesting top sections
    top_sections = [
        section
        for section in parsed.get_sections(include_subsections=True, level=level)
        if section_title(section.title) in head_sections[locale]
    ]

    # Get _all_ sections without any filtering
    all_sections.extend(
        (
            (section.title.strip(), section)
            for top_section in top_sections
            for sublevel in section_sublevels[locale]
            for section in top_section.get_sections(include_subsections=False, level=sublevel)
        )
    )

    #for section in all_sections:
    #    print(section[0])
    return top_sections, all_sections


def find_sections(code: str, locale: str) -> Tuple[List[wtp.Section], Sections]:
    """Find the correct section(s) holding the current locale definition(s)."""
    ret = defaultdict(list)
    wanted = sections[locale]
    top_sections, all_sections = find_all_sections(code, locale)
    for title, section in all_sections:
        # Filter on interesting sections
        if title.startswith(wanted):
            ret[title].append(section)
    
    #for nm, sc in ret.items():
    #    print(nm)
    return top_sections, ret


def add_potential_variant(word: str, tpl: str, locale: str, variants: List[str]) -> None:
    if locale == "pl":
        if var_list := transform_grammar_template(word, tpl, locale):
            #for i in var_list:
            #    print(i)
            variants += (var_list)
    else:
        if (variant := process_templates(word, tpl, locale)) and variant != word:
            variants.append(variant)


def adjust_wikicode(code: str, locale: str) -> str:
    """Sometimes we need to adapt the Wikicode."""
    code = re.sub(r"(<!--.*?-->)", "", code, flags=re.DOTALL)

    if locale == "de":
        # {{Bedeutungen}} -> === {{Bedeutungen}} ===
        code = re.sub(r"^\{\{(.+)\}\}", r"=== {{\1}} ===", code, flags=re.MULTILINE)

        # Definition lists are not well supported by the parser, replace them by numbered lists
        # Note: using `[ ]*` rather than `\s*` to bypass issues when a section above another one
        #       contains an empty item.
        code = re.sub(r":\[\d+\][ ]*", "# ", code)

        # {{!}} -> "|"
        code = code.replace("{{!}}", "|")

    elif locale == "es":
        # {{ES|xxx|núm=n}} -> == {{lengua|es}} ==
        code = re.sub(r"^\{\{ES\|.+\}\}", r"== {{lengua|es}} ==", code, flags=re.MULTILINE)

    elif locale == "it":
        if "{{Tabs" not in code:
            # Hack for a fake variants to support more of them
            # `# plurale di [[-ectomia]]`
            code = re.sub(
                r"^(#\s?)+((?:femminile|plurale) [^\[]+)\[\[([^\]]+)\]\]",
                r"\1{{\2|\3}}",
                code,
                flags=re.MULTILINE,
            )

    elif locale == "ro":
        locale = "ron"

        # {{-avv-|ANY|ANY}} -> === {{avv|ANY|ANY}} ===
        code = re.sub(
            r"^\{\{-(.+)-\|(\w+)\|(\w+)\}\}",
            r"=== {{\1|\2|\3}} ===",
            code,
            flags=re.MULTILINE,
        )

        # Try to convert old Wikicode
        if "==Romanian==" in code:
            # ==Romanian== -> == {{limba|ron}} ==
            code = code.replace("==Romanian==", "== {{limba|ron}} ==")

            # ===Adjective=== -> === {{Adjective}} ===
            code = re.sub(r"===(\w+)===", r"=== {{\1}} ===", code, flags=re.MULTILINE)

        # ===Verb tranzitiv=== -> === {{Verb tranzitiv}} ===
        code = re.sub(r"====([^=]+)====", r"=== {{\1}} ===", code, flags=re.MULTILINE)

        # Hack for a fake variants support because RO doesn't use templates most of the time
        # `#''forma de feminin singular pentru'' [[frumos]].` -> `# {{forma de feminin singular pentru|frumos}}`
        code = re.sub(
            r"^(#\s?)'+(forma de [^']+)'+\s*'*\[\[([^\]]+)\]\]'*\.?",
            r"\1{{\2|\3}}",
            code,
            flags=re.MULTILINE,
        )

    if locale in {"it", "ron", "da"}:
        # {{-avv-|it}} -> === {{avv}} ===
        code = re.sub(
            rf"^\{{\{{-(.+)-\|{locale}\}}\}}",
            r"=== {{\1}} ===",
            code,
            flags=re.MULTILINE,
        )

        # {{-avv-|ANY}} -> === {{avv|ANY}} ===
        code = re.sub(r"^\{\{-(.+)-\|(\w+)\}\}", r"=== {{\1|\2}} ===", code, flags=re.MULTILINE)

        # {{-avv-}} -> === {{avv}} ===
        code = re.sub(r"^\{\{-(\w+)-\}\}", r"=== {{\1}} ===", code, flags=re.MULTILINE)

        # {{!}} -> "|"
        code = code.replace("{{!}}", "|")

    if locale == "da":
        # {{=da=}} -> =={{da}}==
        code = re.sub(r"\{\{=(\w{2})=\}\}", r"=={{\1}}==", code, flags=re.MULTILINE)

    if locale == "pl":
        #{{wymowa}} => === {{wymowa}} ===
        code = re.sub(r"^\{\{(\w+)\}\}", r"=== {{\1}} ===", code, flags=re.MULTILINE)
        # Definition lists are not well supported by the parser, replace them by numbered lists
        # Note: using `[ ]*` rather than `\s*` to bypass issues when a section above another one
        #       contains an empty item.
        # "'' rzecz.." => "# ''rzecz..."
        #code = re.sub(r"^\'\'", "# ''", code)
        # ": (1.1)" => "## (1.1)"
        #code = re.sub(r"^\:\s", "## ", code)
        #[[Aneks:Język polski - zaimki|opis polskich zaimków na stronie aneksu]] => {{odmiana-zaimków}}
        # hack to catch all variants later on
        code = re.sub(r"\[\[Aneks:Język polski - zaimki\|.+\]\]", r"{{odmiana-zaimków}}", code, flags=re.MULTILINE)


    return code


def parse_word(word: str, code: str, locale: str, force: bool = False) -> Word:
    """Parse *code* Wikicode to find word details.
    *force* can be set to True to force the pronunciation and gender guessing.
    It is disabled by default to speed-up the overall process, but enabled when
    called from get_and_parse_word().
    """
    code = adjust_wikicode(code, locale)
    top_sections, parsed_sections = find_sections(code, locale)
    prons = []
    genders = []
    etymology = []
    variants: List[str] = []

    # Etymology
    for section in etyl_section[locale]:
        if etyl_data := parsed_sections.pop(section, []):
            etymology = find_etymology(word, locale, etyl_data[0])

    definitions = find_definitions(word, parsed_sections, locale)

    if definitions or force:
        prons = _find_pronunciations(top_sections, find_pronunciations[locale])
        genders = _find_genders(top_sections, find_genders[locale])

    # Find potential variants
    if interesting_titles := variant_titles[locale]:
        interesting_templates = variant_templates[locale]
        for title, parsed_section in parsed_sections.items():
            print(f"Tytuł sekcji: {title}")
            if not title.startswith(interesting_titles):
                continue
            for tpl in parsed_section[0].templates:
                tpl = str(tpl)
                print(f"TO JEST TEMPLEJT >> '{tpl}' <<")
                if tpl.startswith(interesting_templates):
                    add_potential_variant(word, tpl, locale, variants)
        if variants:
            variants = sorted(set(uniq(variants)))

    return Word(prons, genders, etymology, definitions, variants)


def load(file: Path) -> Dict[str, str]:
    """Load the JSON file containing all words and their details."""
    with file.open(encoding="utf-8") as fh:
        words: Dict[str, str] = json.load(fh)
    print(f">>> Loaded {len(words):,} words from {file}", flush=True)
    return words


def render_word(w: List[str], words: Words, locale: str) -> None:
    word, code = w
    print(f"## {word} ##")
    try:
        details = parse_word(word, code, locale)
    except Exception as w:  # pragma: nocover
        #raise Exception
        print(f"ERROR with {word!r}", flush=True)
        print(w)
    else:
        if details.definitions or details.variants:
            words[word] = details


def render(in_words: Dict[str, str], locale: str, workers: int) -> Words:
    # Skip not interesting words early as the parsing is quite heavy
    sections = head_sections[locale]
    in_words = {word: code for word, code in in_words.items() if any(head_section in code for head_section in sections)}

    MANAGER = multiprocessing.Manager()
    MISSING_TPL_SEEN = MANAGER.list()  # noqa:F841
    results: Words = cast(Dict[str, Word], MANAGER.dict())

    with multiprocessing.Pool(processes=workers) as pool:
        pool.map(partial(render_word, words=results, locale=locale), in_words.items())

    return results.copy()


def save(snapshot: str, words: Words, output_dir: Path) -> None:
    """Persist data."""
    raw_data = output_dir / f"data-{snapshot}.json"
    with raw_data.open(mode="w", encoding="utf-8") as fh:
        json.dump(words, fh, indent=4, sort_keys=True)
    print(f">>> Saved {len(words):,} words into {raw_data}", flush=True)


def get_latest_json_file(output_dir: Path) -> Path | None:
    """Get the name of the last data_wikicode-*.json file."""
    files = list(output_dir.glob("data_wikicode-*.json"))
    return sorted(files)[-1] if files else None


def main(locale: str, workers: int = multiprocessing.cpu_count()) -> int:
    """Entry point."""

    output_dir = Path(os.getenv("CWD", "")) / "data" / locale
    file = get_latest_json_file(output_dir)
    if not file:
        print(">>> No dump found. Run with --parse first ... ", flush=True)
        return 1

    print(f">>> Loading {file} ...", flush=True)
    in_words: Dict[str, str] = load(file)

    workers = workers or multiprocessing.cpu_count()
    words = render(in_words, locale, workers)
    if not words:
        raise ValueError("Empty dictionary?!")

    date = file.stem.split("-")[1]
    save(date, words, output_dir)

    print(">>> Render done!", flush=True)
    return 0

#main("pl",1)