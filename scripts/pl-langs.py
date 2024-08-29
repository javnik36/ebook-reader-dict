from scripts_utils import get_soup

url = "https://pl.wiktionary.org/wiki/Wikis%C5%82ownik:Kody_j%C4%99zyk%C3%B3w"
soup = get_soup(url)

langs = {}
wiki_table = soup.find_all("table", {"class": "wikitable"})
for table in wiki_table:
    trs = table.find_all("tr")

    for tr in trs:
        tds = tr.find_all("td")
        for th in tds:
            langs[tds[1].text.strip()] = tds[0].text.strip()

print("langs = {")
for j,k in sorted(langs.items()):
    print(f'    "{j}": "{k}",')
print(f"}}  # {len(langs):,}")