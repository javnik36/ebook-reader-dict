"""Get and render a word; then compare with the rendering done on the Wiktionary to catch errors."""
import copy
import re
from typing import List
from functools import partial
from threading import Lock
from time import sleep


from .render import parse_word
from .stubs import Word
from .user_functions import color, int_to_roman
from .utils import get_word_of_the_day

import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException


# Remove all kind of spaces and some unicode characters
_replace_noisy_chars = re.compile(r"[\s\u200b\u200e]").sub
no_spaces = partial(_replace_noisy_chars, "")

# Retry mechanism
MAX_RETRIES = 5  # count
SLEEP_TIME = 5  # time, seconds


def check_mute(wiktionary_text: str, parsed_html: str, category: str) -> List[str]:
    results: List[str] = []
    clean_text = get_text(parsed_html)

    # It's all good!
    if contains(clean_text, wiktionary_text):
        return results

    results.append(category + wiktionary_text)

    # Try to highlight the bad text
    pattern = clean_text[:-1].rstrip()
    while pattern:
        if not contains(pattern, wiktionary_text):
            pattern = pattern[:-1].rstrip()
            continue

        idx = len(pattern)
        results.append(f"{clean_text[:idx]}\033[31m{clean_text[idx:]}\033[0m")
        break
    else:
        # No highlight possible, just output the whole sentence
        results.append(clean_text)

    return results


def check(wiktionary_text: str, parsed_html: str, category: str) -> int:
    """Run checks and return the error count to increment."""
    results = check_mute(wiktionary_text, parsed_html, category)
    for r in results:
        print(r, flush=True)
    return int(len(results) / 2)


def contains(pattern: str, text: str) -> bool:
    """Check if *pattern* is in *text*, with all spaces removed.
    *text* is already stripped from spaces in get_wiktionary_page().
    """
    return no_spaces(pattern) in text


def filter_html(html: str, locale: str) -> str:
    """Some parts of the Wiktionary HTML."""
    bs = BeautifulSoup(markup=html, features="html.parser")

    # Filter out warnings about obsolete template models used
    for span in bs.find_all("span", {"id": "FormattingError"}):
        span.decompose()

    # Filter out Wikispecies links
    for span in bs.find_all("span", {"class": "trad-exposant"}):
        span.decompose()

    # Filter out result of <math> and <chem>
    for span in bs.find_all("span", {"class": "mwe-math-element"}):
        span.decompose()

    if locale == "de":
        # Other Wikis
        for a in bs.find_all("a", {"class": "extiw"}):
            if ":Special:" in a["title"]:
                a.decompose()

    # Adapt the formatting for the ES locale as it differs from other locales
    if locale == "es":
        # Replace color rectangle
        for span in bs.find_all("span", {"id": "ColorRect"}):
            for style in span["style"].split(";"):
                kv = style.strip().split(":")
                if len(kv) == 2 and kv[0] == "background":
                    span.previous_sibling.decompose()
                    span.replaceWith(color(kv[1].strip()))
        for a in bs.find_all("a", href=True):
            if a["href"].startswith("#cite"):
                a.decompose()
            # cita requerida
            elif (
                a["href"] == "/wiki/Ayuda:Tutorial_(Ten_en_cuenta)#Citando_tus_fuentes"
            ):
                a.parent.parent.decompose()
        # external autonumber
        for a in bs.find_all("a", {"class": "external autonumber"}):
            a.decompose()
        dts = bs.find_all("dt")
        for dt in dts:
            dt_array = dt.text.split(" ", 1)
            if len(dt_array) == 2:
                dt.string = dt_array[0] + " "
                # 2 Historia. --> (Historia):
                if "." in dt_array[1]:
                    dt_array_dot = dt_array[1].split(".")
                    for da in dt_array_dot[:-1]:
                        dt.string += f"({da})"
                    dt.string += f" {dt_array_dot[-1]}:"
                else:
                    # duplicate the definition to cope with both cases above
                    newdt = copy.copy(dt)
                    dt.parent.append(newdt)
                    dd = dt.find_next_sibling("dd")
                    if dd:
                        dt.parent.append(copy.copy(dd))
                    # 2 Selva de Bohemia: --> Selva de Bohemia:
                    newdt.string = dt.string + dt_array[1] + ":"
                    # 2 Coloquial: --> (Coloquial):
                    dt.string += f"({dt_array[1]}):"

        return no_spaces(bs.text)

    if locale == "fr":
        # Filter out refnec tags
        for span in bs.find_all("span", {"id": "refnec"}):
            if span.previous_sibling:
                span.previous_sibling.decompose()
            span.decompose()
        # Cette information a besoin d’être précisée
        for span in bs.find_all(
            "span", {"title": "Cette information a besoin d’être précisée"}
        ):
            span.decompose()
        # {{invisible}}
        for span in bs.find_all("span", {"class": "invisible"}):
            span.decompose()
        # — (Richelet, Dictionnaire français 1680)
        for span in bs.find_all("span", {"class": "sources"}):
            span.decompose()
        # → consulter cet ouvrage
        for a in bs.find_all("a", {"class": "external text"}):
            if "consulter cet ouvrage" in a.text:
                a.decompose()
        # liens externes autres Wikis
        for a in bs.find_all("a", {"class": "extiw"}):
            # Wikispecies
            if (
                a["title"].startswith("wikispecies")
                and a.parent.next_sibling
                and "sur Wikispecies" in a.parent.next_sibling
            ):
                a.parent.next_sibling.replaceWith("")
            # Wikidata
            elif (
                a["title"].startswith("d:")
                and a.next_sibling
                and "base de données Wikidata" in a.next_sibling
            ):
                a.next_sibling.replaceWith("")
            # {{LienRouge|lang=en|trad=Reconstruction
            elif "Reconstruction" in a["title"]:
                a.decompose()
        # external autonumber
        for a in bs.find_all("a", {"class": "external autonumber"}):
            a.decompose()
        # attention image
        for a in bs.find_all("a", {"title": "alt = attention"}):
            a.replaceWith("⚠")
        # other anchors
        for a in bs.find_all("a", href=True):
            if a["href"].lower().startswith(("#cite", "#ref", "#voir")):
                a.decompose()
        return no_spaces(bs.text)

    if locale == "en":
        for span in bs.find_all("span"):
            if span.string == "and other forms":
                span.string += f' {span["title"]}'

    # Filter out anchors as they are ignored from templates
    for a in bs.find_all("a", href=True):
        if a["href"].startswith("#"):
            a.decompose()
    return no_spaces(bs.text)


def get_text(html: str) -> str:
    """Parse the HTML code and return it as a string."""
    return str(BeautifulSoup(markup=html, features="html.parser").text)


def craft_url(word: str, locale: str, raw: bool = False) -> str:
    """Craft the *word* URL for the given *locale*."""
    url = f"https://{locale}.wiktionary.org/w/index.php?title={word}"
    if raw:
        url += "&action=raw"
    return url


def get_url_content(url: str) -> str:
    """Fetch given *url* content with retries mechanism."""
    retry = 0
    while retry < MAX_RETRIES:
        try:
            with requests.get(url, timeout=10) as req:
                req.raise_for_status()
                return req.text
        except TimeoutError:
            sleep(SLEEP_TIME)
            retry += 1
        except RequestException as err:
            wait_time = 1
            resp = err.response
            if resp is not None and resp.status_code == 429:
                print(resp, resp.status_code == 429)
                wait_time = int(resp.headers.get("retry-after") or "1")
            sleep(wait_time * SLEEP_TIME)
            retry += 1
    raise RuntimeError(f"Sorry, too many tries for {url!r}")


def get_word(word: str, locale: str) -> Word:
    """Get a *word* wikicode and parse it."""
    url = craft_url(word, locale, raw=True)
    html = get_url_content(url)
    return parse_word(word, html, locale)


def get_wiktionary_page(word: str, locale: str) -> str:
    """Get a *word* HTML."""
    url = craft_url(word, locale)
    html = get_url_content(url)
    return filter_html(html, locale)


def check_word(word: str, locale: str, lock: Lock = None) -> int:
    errors = 0
    results: List[str] = []
    details = get_word(word, locale)
    if not details.etymology and not details.definitions:
        return errors
    text = get_wiktionary_page(word, locale)

    if details.etymology:
        for etymology in details.etymology:
            if isinstance(etymology, tuple):
                for i, sub_etymology in enumerate(etymology, 1):
                    r = check_mute(text, sub_etymology, f"\n !! Etymology {i}")
                    results.extend(r)
            else:
                r = check_mute(text, etymology, "\n !! Etymology")
                results.extend(r)

    index = 1
    for definition in details.definitions:
        message = f"\n !! Definition n°{index}"
        if isinstance(definition, tuple):
            for a, subdef in zip("abcdefghijklmopqrstuvwxz", definition):
                if isinstance(subdef, tuple):
                    for rn, subsubdef in enumerate(subdef, 1):
                        r = check_mute(
                            text, subsubdef, f"{message}.{int_to_roman(rn).lower()}"
                        )
                        results.extend(r)
                else:
                    r = check_mute(text, subdef, f"{message}.{a}")
                    results.extend(r)
        else:
            r = check_mute(text, definition, message)
            results.extend(r)
            index += 1
    # print with lock if any
    if results:
        errors = int(len(results) / 2)
        if lock:
            lock.acquire()
        for result in results:
            print(result, flush=True)
        print(f"\n >>> [{word}] - Errors:", errors, flush=True)
        if lock:
            lock.release()

    return errors


def main(locale: str, word: str) -> int:
    """Entry point."""
    # If *word* is empty, get the word of the day
    if not word:
        word = get_word_of_the_day(locale)

    return check_word(word, locale)
