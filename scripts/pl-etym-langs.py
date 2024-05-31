from scripts_utils import get_soup

url = "https://pl.wiktionary.org/wiki/Szablon:etym"
soup = get_soup(url)

langs = {}
h2 = soup.find("span",{"id": "Skróty_języków"})
h2_list = h2.find_next("ul")
lis = h2_list.find_all("li")

append_langs = {}

for li in lis:
    li = li.text
    try:
        key, value = li.split("–")
        langs[key.strip()] = value.strip()
    except:
        k,v = li.split("==>", maxsplit=1)
        if k.strip() == "niemdial":
            langs[k.strip()] = "niemiecki, dialekt"
            continue
        append_langs[k.strip()] = v.strip()

for l,s in append_langs.items():
    langs[l] = langs.get(s)


print("etym_langs = {")
for j,k in sorted(langs.items()):
    print(f'    "{j}": "{k}",')
print(f"}}  # {len(langs):,}")