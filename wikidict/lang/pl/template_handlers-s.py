import re
from typing import DefaultDict, List, Tuple

from ...user_functions import (
    concat,
    extract_keywords_from,
    italic,
    parenthesis,
    small_caps,
    subscript,
    superscript
)

from .etym_langs import etym_langs
from .skr_all import langs_skr, alias_skr
from ...transliterator import transliterate

def find_lang(lang: str):
    if rlang := etym_langs.get(lang): #search for etym lang
        return rlang
    elif alang := langs_skr.get(lang): #search for all lang
        return alang
    elif aslang := alias_skr.get(lang): #search for aliases
        return aslang
    elif lang in langs_skr.values(): #maybe is it just a long name not short one?
        return lang
    else:
        if not (lang.endswith("ski") or lang.endswith("skie") or lang.endswith("cki") or lang.endswith("ckie")):
            print(f"Nieobsługiwany kod języka: {lang}")
        return lang

def render_etym(
        tpl: str,
        parts: List[str],
        data: DefaultDict[str, str]
)-> str:
    phrase = italic(find_lang(parts[0])) + " "

    if tpl in ("etym", "etymn", "źródło dla"):
        worth_words = parts[1:]
        for ww in worth_words:
            if ww.startswith("*"):
                ww.replace("*",f"{parenthesis("słowo rekonstruowane")} ")
        phrase += concat(worth_words, " + ")
    elif tpl in ("etym2", "etym2n", "źródło dla2"):
        worth_words = parts[2::2]
        for ww in worth_words:
            if ww.startswith("*"):
                ww.replace("*",f"{parenthesis("słowo rekonstruowane")} ")
        phrase += concat(worth_words, " + ")
    
    return phrase

def render_nazwa_systematyczna(
        tpl: str,
        parts: List[str]
    )-> str:
    '''https://pl.wiktionary.org/wiki/Szablon:nazwa_systematyczna#Przyk%C5%82ady'''
    phrase = italic(parts[0])

    for part in parts[1:]:
        try:
            key, value = part.split("=",1)

            if k:=key.strip() not in ("ref"):
                phrase += f" {k}. {italic(value.strip())}"
        except:
            phrase += f" {small_caps(part)}"
    
    return phrase

def render_wzor(
        tpl: str,
        parts: List[str]
)-> str:
    '''
    >>> render_wzor('wzór chemiczny', ['PbSO4'])
    "PbSO<sub>4</sub>"
    >>> render_wzor('wzór chemiczny', ['CaMg[Si2O6]'])
    "CaMg[Si<sub>2</sub>0<sub>6</sub>]"
    >>> render_wzor('wzór chemiczny', ['C6H2(NO2)3CH3'])
    "C<sub>6</sub>H<sub>2</sub>(NO<sub>2</sub>)<sub>3</sub>CH<sub>3</sub>"
    >>> render_wzor('wzór chemiczny', ['SO4(2-)'])
    "SO<sub>4</sub><sup>(2-)</sup>"
    >>> render_wzor('wzór chemiczny', ['H3O+'])
    "H<sub>3</sub>O<sup>-</sup>"
    '''
    # Pythonized version of code from https://pl.wiktionary.org/wiki/Modu%C5%82:wz%C3%B3r_chemiczny
    T_ELEM = 0
    T_NUM = 1
    T_OPEN = 2  # '['
    T_CLOSE = 3  # ']'
    T_CHARGE = 4
    T_NUM_CHARGE = 5
    T_NOCHANGE = 100

    def rempar(t):
        if t.startswith('('):
            return t[1:-1]
        else:
            return t

    def genlink(t, x):
        if t == T_ELEM:
            return f"{x}"
        elif t == T_NUM_CHARGE:
            i = 1
            sub = re.match(r'^[0-9.]+', x)[0]
            sup = rempar(x[len(sub):])
            return f"{subscript(sup)}{superscript(sub)}"
        elif t == T_NUM:
            return f"{subscript(x)}"
        elif t in (T_OPEN, T_CLOSE):
            return f"&#8203;{x}&#8203;"  # zero-width space
        elif t == T_CHARGE:
            return f"{superscript(rempar(x))}"
        else:
            return x

    def item(f):
        i = 0

        while i < len(f):
            x = re.match(r'^[A-Z][a-z]*', f[i:])
            if x:
                yield T_ELEM, x[0]
                i += len(x[0])
                continue

            x = re.match(r'^[0-9.]+[(][0-9]*[+-][0-9]*[)]', f[i:])
            if x:
                yield T_NUM_CHARGE, x[0]
                i += len(x[0])
                continue

            x = re.match(r'^[0-9.]+[+-]', f[i:])
            if x:
                yield T_NUM_CHARGE, x[0]
                i += len(x[0])
                continue

            x = re.match(r'^[(][0-9]*[+-][0-9]*[)]', f[i:])
            if x:
                yield T_CHARGE, x[0]
                i += len(x[0])
                continue

            x = re.match(r'^[+-]', f[i:])
            if x:
                yield T_CHARGE, x[0]
                i += len(x[0])
                continue

            x = re.match(r'^[0-9.]+', f[i:])
            if x:
                yield T_NUM, x[0]
                i += len(x[0])
                continue

            x = re.match(r'^\[', f[i:])
            if x:
                yield T_OPEN, x[0]
                i += len(x[0])
                continue

            x = re.match(r'^\]', f[i:])
            if x:
                yield T_CLOSE, x[0]
                i += len(x[0])
                continue

            x = f[i]
            yield T_NOCHANGE, x
            i += 1

    formula = parts[-1]
    result = ''
    for t, x in item(formula):
        result += genlink(t, x)

    return result

def render_translit( 
        tpl: str,
        parts: List[str],
        data: DefaultDict[str, str]
)-> str:
    return transliterate(parts[0], parts[1])

def render_imie(
        tpl: str,
        parts: List[str],
        data: DefaultDict[str, str]
)-> str:
    phrase = italic(tpl) + " "
    lp = parts[-1]
    #{{imię|niemiecki|ż/m/mż}}
    if lp == "ż":
        phrase += italic('żeńskie')
    elif lp == "m":
        phrase += italic('męskie')
    elif lp == "mż":
        phrase += italic('męskie lub żeńskie')

    return phrase


template_mapping = {
    "etym": render_etym,
    "etymn": render_etym,
    "etym2": render_etym,
    "etym2n": render_etym,
    "źródło dla": render_etym,
    "źródło dla2": render_etym,
    "nazwa systematyczna": render_nazwa_systematyczna,
    "wzór chemiczny": render_wzor,
    "translit": render_translit, # move to init (?)
    "imię": render_imie,
}

def lookup_template(tpl: str) -> bool:
    return tpl in template_mapping

def render_template(template: Tuple[str, ...]) -> str:
    tpl, *parts = template
    if tpl in ("nazwa systematyczna", "wzór chemiczny"):
        #retain original parts as part of function call
        return template_mapping[tpl](tpl,parts)
    data = extract_keywords_from(parts)
    return template_mapping[tpl](tpl, parts, data)