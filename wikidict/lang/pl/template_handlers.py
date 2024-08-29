import re
from collections import defaultdict  # noqa
from typing import DefaultDict, List, Tuple, TypedDict

from ...user_functions import (
    capitalize,
    concat,
    chimy,
    extract_keywords_from,
    flatten,
    italic,
    lookup_italic,
    parenthesis,
    small,
    small_caps,
    strong,
    subscript,
    superscript,
    term,
    uniq
)

#from .odmiana_zaimkow import odmiana_zaimkow
from .skr import skr_list
from .langs import langs
from .etym_langs import etym_langs
from .skr_all import langs_skr, alias_skr
from ...transliterator import transliterate

def render_rzeczownik_inflection(
        tpl: str,
        parts: List[str],
        data: DefaultDict[str, str]
)-> list:
    """ 
    >>> render_rzeczownik_inflection("odmiana-rzeczownik-polski", ["Mianownik lp = Urban", "Dopełniacz lp = Urbana", "Celownik lp = Urbanowi", "Biernik lp = Urbana", "Narzędnik lp = Urbanem", "Miejscownik lp = Urbanie", "Wołacz lp = Urbanie", "Mianownik lm = Urbanowie", "Dopełniacz lm = Urbanów", "Celownik lm = Urbanom", "Biernik lm = Urbanów", "Narzędnik lm = Urbanami", "Miejscownik lm = Urbanach", "Wołacz lm = Urbanowie", "Forma depr = Urbany"], defaultdict(str))
    '['Urban', 'Urbana', 'Urbanowi', 'Urbanem', 'Urbanie', 'Urbanowie', 'Urbanów', 'Urbanom', 'Urbanami', 'Urbanach', 'Urbany']'
    >>> render_rzeczowanik_inflection("odmiana-rzeczownik-polski", ["Mianownik lp = ", "Dopełniacz lp = ", "Celownik lp = ", "Biernik lp = ", "Narzędnik lp = ", "Miejscownik lp = ", "Wołacz lp = "])
    '[]'
    """
    #aaaa! parts empty if same "=" in parts => only data in call
    variants = []
    for inflection in parts:
        if inflection := inflection.split("=")[-1].strip():
            variants.append(inflection)
    
    variants.pop(0) #remove Mianownik lp (because it is the same as word)
    return uniq(variants)


def inflect_przymiotnik(przymiotnik:str) -> list:
    pattern = re.compile(r"(.+)[iy]$")
    temat = pattern.findall(przymiotnik)
    # TODO: implement Mianownik l.mn. correctly
    dodatek_y = ["a", "e", "ego", "ej", "emu", "ą", "ym", "ych", "ymi"]
    dodatek_ony = ["a", "e", "ego", "ej", "emu", "ą", "ym", "ej", "i", "ych", "ymi"]
    dodatek_i = ["a", "e", "ego", "ej", "emu", "ą", "im", "ich", "imi"]

    variants = []
    if przymiotnik.endswith("i"):
        for dodatek in dodatek_i:
            variants.append(concat([temat,dodatek]))
    elif przymiotnik.endswith("ony"):
        for dodatek in dodatek_ony:
            variants.append(concat([temat,dodatek]))
    elif przymiotnik.endswith("y"):
            for dodatek in dodatek_y:
                variants.append(concat([temat,dodatek]))
    else:
        print(f"?!?!Przymiotnik dla którego nie ma zaimplementowanej odmiany : {przymiotnik}")
    
    return variants



def render_przymiotnik_inflection(
        tpl: str,
        parts: List[str],
        data: str
)-> list:
    """
    {{odmiana-przymiotnik-polski | [1] | [2] | odpowiednik = | ims = }}

[1] (opcjonalny) – forma podstawowa przymiotnika; jeżeli nie podano, szablon pobierze tytuł strony
[2] (opcjonalny) – stopień wyższy lub słowo brak, jeżeli go nie tworzy
odpowiednik – wymagany dla przymiotników niekończących się na -i ani na -y (np. zdrów, świadom, godzien, wart, gotów, żyw, pełen, pewien); należy podać odpowiednik przymiotnika kończący się na -y (np. zdrów: odpowiednik=zdrowy)
ims=nie – tylko dla przymiotników kończących się na -ony, które nie pochodzą od imiesłowu biernego (np. czerwony, zielony, słony, wrony); w tych przymiotnikach nie zachodzi wymiana samogłosek o-e w liczbie mnogiej, por. czerwony – czerwoni, doświadczony – doświadczeni

    >>> render_przymiotnik_inflection("odmiana-przymiotnik-polski", ["żółtszy"], "żółty")

    """
    #Parts = temat (optional), 2temat[bardziej|brak] (optional), odpowiednik=[2temat] (optional), ims=nie (optional)
    """     if parts[0] not in ("brak", "bardziej", data):
        #double deklin
        pass

    if "odpowiednik" not in parts:
        if data not in parts:
            if ("brak", "bardziej") not in parts:
                pass #deklinuj słowo które nie jest wordem i nei jest: brakiem/bardziejem/imsem
                # oraz deklinuj data
            else:
                pass#0 outcomu
    else:
        pass#0 outcomu

    if len(parts) == 1:
        if parts[0] not in ("brak", "bardziej", data):
            pass #deklinacja parts[0] wraz z deklinacją data
    elif len(parts) == 2:
        last_part = extract_keywords_from(parts[-1])
        if last_part in ("odpowiednik"):
            pass#nie deklinuj NIC
        elif last_part in ("ims"):
            pass#deklinuj tylko data
        else:
            if parts[1] in ("brak", "bardziej"):
                if parts[0] == data:
                    pass #tylko deklinacja data
                else:
                    pass#deklinacja data i parts[0]
            else: #parts[0] to temat2
                pass#deklinuj parts[0] i data
    """
    #aaaa! parts empty if same "=" in parts => only data in call

    variants = []

    for slowo in parts:
        if slowo in ("brak", "bardziej", data, "ims"):
            parts.remove(slowo)

    if "odpowiednik" not in parts:
        for w in parts:
            variants.extend(inflect_przymiotnik(w))
    
    return sorted(uniq(variants))

def render_zaimek_inflection(
        tpl: str,
        parts: List[str],
        data: DefaultDict[str, str]
)-> list:
    """
    """
    #data=word
    if variants := odmiana_zaimkow.get(data):
        return sorted(uniq(variants))
    else:
        return []

def find_lang(lang: str)-> str:
    """
    Browse through all language dicts to find the correct language shortcut.
    >>> find_lang("pl")
    'polski'
    >>> find_lang("sith")
    'sith'
    """ # noqa
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
    """
    Renders etymology templates (etym, etym2, etymn, etymn2m, źródło, źródło2):
    * "2" versions include internal linking with different visual output to the user,
        so every 2nd word is used here.
    * "n" versions just don't add categories on wiki, so this doesn't matter for us.
    * "*" sign resolves as "słowo rekonstruowane" within the templates.
    * multiple words are seperated by "+"sign.

    Full template documentation here: https://pl.wiktionary.org/wiki/Szablon:etym

    >>> render_etym("etym",["pol","krowa"], defaultdict(str)):
    '<i>polski</i> krowa'
    >>> render_etym("etym2",["łaciński","alphabetum","alphabētum"], defaultdict(str)):
    '<i>łaciński</i> alphabētum'
    >>> render_etym("etymn",["niem","*nein"], defaultdict(str)):
    '<i>niemiecki</i> (słowo rekonstruowane) nein'
    >>> render_etym("etym2n",["pl","kowal","Kowal","-ski","-ski"], defaultdict(str)):
    '<i>polski</i> Kowal + -ski'
    """
    phrase = italic(find_lang(parts[0])) + " "
    #etym + etymn to same słowa
    #etym2 i etym2n to słowa z pisownią ich (//2)

    if tpl in ("etym", "etymn", "źródło dla"):
        worth_words = parts[1:]
        for ww in worth_words:
            if ww.startswith("*"):
                ww.replace("*",f"{parenthesis("słowo rekonstruowane")} ") # Move to separate func
        phrase += concat(worth_words, " + ")
    elif tpl in ("etym2", "etym2n", "źródło dla2"):
        worth_words = parts[2::2]
        for ww in worth_words:
            if ww.startswith("*"):
                ww.replace("*",f"{parenthesis("słowo rekonstruowane")} ") # Move to separate func
        phrase += concat(worth_words, " + ")
    
        #print(f"Rendered '{phrase}'")
    return phrase

def render_nazwa_systematyczna(
        tpl: str,
        parts: List[str]
    )-> str:
    """
    Renders template for nazwa systematyczna (Scientific classification).
    "ref=*" template parameter is skipped.

    Full template documentation here: https://pl.wiktionary.org/wiki/Szablon:nazwa_systematyczna

    >>> render_etym("nazwa systematyczna",["Felis silvestris catus"]):
    '<i>Felis silvestris catus</i>'
    >>> render_etym("nazwa systematyczna",["Tussilago farfara","L."]):
    '<i>Tussilago farfara</i> <span style='font-variant:small-caps'>L.</span>'
    >>> render_etym("nazwa systematyczna",["Serratia marcescens","ref=tak"]):
    '<i>Serratia marcescens</i>'
    >>> render_etym("nazwa systematyczna",["Brassica oleracea","var=sabellica","L.","ref=tak"]):
    '<i>Brassica oleracea</i> var. <i>sabellica</i> <span style='font-variant:small-caps'>L.</span>'
    >>> render_etym("nazwa systematyczna",["Beta vulgaris","subsp=cicla","L.","ref=tak"]):
    '<i>Beta vulgaris</i> subsp. <i>cicla</i> <span style='font-variant:small-caps'>L.</span>'
    >>> render_etym("nazwa systematyczna",["Vaccinium","sect=Oxycoccus","Hill.","ref=tak"]):
    '<i>Vaccinium</i> sect. <i>Oxycoccus</i> <span style='font-variant:small-caps'>Hill.</span>'
    >>> render_etym("nazwa systematyczna",["Sorbus","subg=Micromeles","ref=tak"]):
    '<i>Sorbus</i> subg. <i>Micromeles</i>'
    >>> render_etym("nazwa systematyczna",["Pseudevernia furfuracea","f=furfuracea","ref=tak"]):
    '<i>Pseudevernia furfuracea</i> f. <i>furfuracea</i>'
    """
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
    """
    Renders chemical notation.

    Full template documentation here: https://pl.wiktionary.org/wiki/Szablon:wz%C3%B3r_chemiczny

    This is pythonized version of code from https://pl.wiktionary.org/wiki/Modu%C5%82:wz%C3%B3r_chemiczny

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
    """
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


def render_imie(
        tpl: str,
        parts: List[str],
        data: DefaultDict[str, str]
)-> str:
    """
    Renders imię (name) template. Omits lang tag (only used for wiki links).

    Full template documentation here: https://pl.wiktionary.org/wiki/Szablon:imi%C4%99

    >>> render_imie("imię",["niem","ż"], defaultdict(str))
    '<i>imię męskie</i>'
    >>> render_imię("imię",["polski","mż"], defaultdict(str))
    '<i>imię męskie lub żeńskie</i>'
    """
    phrase = italic(tpl) + " "
    lp = parts[-1]

    if lp == "ż":
        phrase += italic('żeńskie')
    elif lp == "m":
        phrase += italic('męskie')
    elif lp == "mż":
        phrase += italic('męskie lub żeńskie')
    # else:
    #     with suppress(KeyError):
    #         raise KeyError("No such part in 'imię' template: " + f'{template[-1]}')
    return phrase

def render_liczebnik_inflection(
        tpl:str,
        parts: List[str],
        data: DefaultDict[str, str],
        word: str
)-> list:
    '''{{odmiana-liczebnik-polski
        | Odmiana              = 2
        | Mianownik mos        = obaj / obu
        | Mianownik nmos       = oba
        | Mianownik ż          = obie
        | Dopełniacz           = obu
        | Celownik             = obu / {{daw}} obom
        | Biernik mos          = obu
        | Biernik nmos         = oba
        | Biernik ż            = obie
        | Narzędnik            = oboma / obu
        | Narzędnik ż          = obiema<br />oboma / obu
        | Miejscownik          = obu
        | Złożenia             = [[obu-]]
    }}'''

    def clean_inflection(text:str) -> str:
        #clean refs <ref name="Dorosz">{{DoroszewskiOnline|id=5501159|hasło=sto}}</ref>
        text = re.sub(r"<ref[^<]*</ref>", "", text)
        #clean line breaks <br />
        text = re.sub(r"<br[^>]*>", "/", text)
        #clean italics
        text = re.sub(r"\'\'[^\']*\'\'", "", text)
        #clean nested templates
        text = re.sub(r"\{\{[^}]*\}\}", "", text)
        #clean links
        text = re.sub(r"\[\[[^\]]*\]\]", "", text)
        text = text.strip()
        return text

    variants = []

    for przypadek, inflection in data.items():
        if przypadek in ("Odmiana", "Złożenia"):
            continue
        #if inflection.isnumeric():
        #    continue
        inflection = clean_inflection(inflection)
        try:
            inflect_parts = inflection.split("/")
            #inflect_parts = [clean_inflection_part(p) for p in inflect_parts]
            inflect_parts  = [p.strip() for p in inflect_parts]
            variants.extend(inflect_parts)
        except:
            #inflect_parts = clean_inflection_part(inflect_parts)
            #variants.append(inflect_parts)
            variants.append(inflection)
    
    print(f"(render_liczebnik_inflection): Inflected {word} with {len(variants)} variants!")
    for v in variants:
        print(v)
    #return sorted(uniq(flatten(variants)))
    return variants

variant_templates = (
    "{{alternatywna wymowa -izmów}",
    "{{alternatywna wymowa -izmów2}",
    "{{alternatywna wymowa -izmów3}",
    "{{stopn", #przysłówki stopniowalne
    "{{niestopn}", #przysłówki nieodmienne lit. "nieodm.""
    "{{KoniugacjaPL}", #deprecated verb odmiana
    "{{odmiana-czasownik-polski",
    "{{odmiana-czasownik-niewłaściwy-polski",
    "{{odmiana-liczebnik-polski",
    "{{odmiana-męskie-nazwisko-polskie-ki}",
    "{{odmiana-męskie-nazwisko-polskie-ny}"
)

template_mapping = {
    "etym": render_etym,
    "etymn": render_etym,
    "etym2": render_etym,
    "etym2n": render_etym,
    "źródło dla": render_etym,
    "źródło dla2": render_etym,
    "nazwa systematyczna": render_nazwa_systematyczna,
    "wzór chemiczny": render_wzor,
    "imię": render_imie,
}

grammar_mapping = {
    "odmiana-liczebnik-polski": render_liczebnik_inflection,
}

def lookup_template(tpl: str) -> bool:
    return tpl in template_mapping

def lookup_template_grammar(tpl: str) -> bool:
    return tpl in grammar_mapping

def render_template(template: Tuple[str, ...]) -> str:
    #add word as argument
    tpl, *parts = template
    if tpl in ("nazwa systematyczna", "wzór chemiczny"):
        #retain original parts as part of function call
        return template_mapping[tpl](tpl,parts)
    data = extract_keywords_from(parts)
    return template_mapping[tpl](tpl, parts, data)

def render_grammar_template(template: Tuple[str, ...], word) -> list:
    tpl, *parts = template
    
    data = extract_keywords_from(parts)
    return grammar_mapping[tpl](tpl,parts,data,word)