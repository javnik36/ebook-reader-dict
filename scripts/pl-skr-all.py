from typing import Dict

from scripts_utils import get_soup

ROOT_URL = "https://pl.wiktionary.org"
START_URL = f"{ROOT_URL}/wiki/Kategoria:Szablony_skr%C3%B3t%C3%B3w"
NEXTPAGE_TEXT = "następna strona"


GRAMMAR_URL = "https://pl.wiktionary.org/wiki/Kategoria:Szablony_skr%C3%B3t%C3%B3w_-_gramatyka"
INFLECTION_URL = "https://pl.wiktionary.org/wiki/Kategoria:Szablony_skr%C3%B3t%C3%B3w_-_deklinacja"
LANGS_URL = "https://pl.wiktionary.org/wiki/Kategoria:Szablony_skr%C3%B3t%C3%B3w_nazw_j%C4%99zyk%C3%B3w"

REDIRECTS_URL = "https://pl.wiktionary.org/wiki/Specjalna:Linkuj%C4%85ce?target={}&hidetrans=1&hidelinks=1"

skr_all = {}
aliasys = {}

def process_page(page_url: str, skr_all: Dict[str,str]) -> str:
    soup = get_soup(page_url)

    nextpage = ""
    nextpage_div = soup.find(id="mw-pages")
    last_link = nextpage_div.find_all("a")[-1]
    if NEXTPAGE_TEXT == last_link.text:
        nextpage = ROOT_URL + last_link.get("href")

    content = nextpage_div.findAll("div", {"class": "mw-category-group"})
    for con in content:
        h3 = con.find_next("h3")
        if h3.text in ("*", u'\xa0'):
            continue

        lis = con.findAll("li")
        for li in lis:
            link = li.find("a")["href"]
            li_url = ROOT_URL + link
            key = li.text.split(":")[1]

            sub_soup = get_soup(li_url)

            dexp = sub_soup.find_all("span", class_="short-wrapper")
            if dexp == []:
                dexp = sub_soup.find("div", class_="mw-parser-output")
                value = dexp.find("i").text.strip()
                skr_all[key] = value
            else:
                value = ""
                if key in ["daw", "hist", "przest", "stpol", "śrpol"]:
                    value = dexp[0]["data-expanded"]
                else:
                    for v in dexp:
                        if v != value.strip():#nie działa (duplikaty wew)
                            value += v["data-expanded"]
                        else:
                            continue
                        if all([len(dexp) > 1, v != dexp[-1]]):
                            value += " "
                skr_all[key] = value

            a_url = REDIRECTS_URL.format(li.text)
            soup_alias = get_soup(a_url)

            if ul_alias := soup_alias.find("ul", {"id": "mw-whatlinkshere-list"}):
                for alias_li in ul_alias.findAll("li"):
                    alias_text = alias_li.find("a").text
                    alias_key = alias_text.split(":")[1]
                    aliasys[alias_key] = value

    return nextpage

def produce_result(name:str, result_dict:dict)->None:
    print(name + " = {")
    for k,v in sorted(result_dict.items()):
        print(f'    "{k}": "{v}",')
    print(f"}}  # {len(result_dict):,}")


next_page_url = START_URL

while next_page_url:
    next_page_url = process_page(next_page_url, skr_all)
produce_result("skr_all", skr_all)

grammar_skr = {}
np = process_page(GRAMMAR_URL, grammar_skr)
produce_result("grammar_skr", grammar_skr)

inflection_skr = {}
ip = process_page(INFLECTION_URL, inflection_skr)
produce_result("inflection_skr", inflection_skr)

langs_skr = {}
next_page_url = LANGS_URL
while next_page_url:
    next_page_url = process_page(next_page_url, langs_skr)
produce_result("langs_skr", langs_skr)

produce_result("alias_skr", aliasys)