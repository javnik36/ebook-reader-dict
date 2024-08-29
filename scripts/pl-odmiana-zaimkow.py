import re
from scripts_utils import get_soup

url = "https://pl.wiktionary.org/wiki/Aneks:J%C4%99zyk_polski_-_zaimki"

soup = get_soup(url)
tables = soup.find_all("table", {"class": "wikitable"})

def deslashify(wej:str, delim: str = "/") -> list:
    try:
        list_i = wej.split(delim)
        list_i = [d.strip() for d in list_i]
        return list_i
    except:
        return []

dicta_zaimkow = {}#zaimek: [variant]

for table in tables:
    zaimek = ""
    lista_odmian = []
    tl = True
    tw = False
    trs = table.find_all("tr")
    for tr in trs:
        if tl:
            prz = tr.select("th")
            las = []
            for pr in prz:
                ptext = pr.text.strip()
                if "Przypadek" in ptext:
                    pass
                elif "Liczba" in ptext:
                    tl = False
                    break
                elif ptext == "":
                    zaimek = "się"
                    #tw = True
                    tl = False
                    break
                else:
                    #a = pr.find("a")
                    #las.extend(a.text.strip())
                    las.append(ptext)
            if las:
                tw = True
                tl = False
                if len(las) > 1:
                    zaimek = las
                else:
                    zaimek = las[0]
            # prz = tr.find("th",text="Przypadek")
            # prz = tr.select("th")
            # for d in prz if not "Liczba" in d.text.strip()
            # if prz:
            #     n_prz = prz.find_next_siblings("th")
            #     prz_href = prz.select("a title")
            #     if not prz_href:
            #         zaimek = "się"
            #     elif len(prz_href) > 1:
            #         tw = True
            #         zaimek = [k.text.strip() for k in prz_href]
            #     else:
            #         zaimek = prz_href[0]
            # else:
            #     tl = False
            #     continue
        if tw:
            for zaim in range(len(zaimek)):
                #formula = len(zaimek)*n+(zaim+1)
                tw_selects = [o.text.strip() for o in tr.select(f"td:nth-of-type({len(zaimek)}n+{zaim+1})")]
                
                dicta_zaimkow[zaimek[zaim]] = tw_selects

                #tw_odds = [o.text.strip() for o in tr.select("td:nth-of-type(odd)")]
                #tw_evens = [o.text.strip() for o in tr.select("td:nth-of-type(even)")]
            tw = False
            continue
        tds = tr.find_all("td")
        if len(tds) >= 1:
            for td in tds:
                lista_odmian.append(td.text.strip())
    # skip "się" as 3/4 words are separately described = no need for variants
    if "się" not in lista_odmian:
        zaimek = lista_odmian[0]
        lista_odmian.pop(0)
        dicta_zaimkow[zaimek] = lista_odmian

ndicta_zaimkow = {}
for zaim, odm in dicta_zaimkow.items():
    temp_entry = []
    if "," not in zaim:
        for i in odm:
            add_i = deslashify(i)
            if add_i:
                temp_entry.extend(add_i)
            else:
                temp_entry.extend(i)
    else:
        new_zaims = deslashify(zaim,",")
        all_vars = []
        for i in odm:
            new_var = deslashify(i,",")
            new_vars = [deslashify(p) for p in new_var]
            if new_vars:    
                all_vars.append(new_vars)
            else:
                all_vars.append(new_var)
        for s in range(len(new_zaims)):
            final_vars = []
            for z in range(len(all_vars)):
                final_vars.extend(all_vars[z][s])
            ndicta_zaimkow[new_zaims[s]] = final_vars
        continue
    while "-ń" in temp_entry:
        temp_entry.remove("-ń")
    ndicta_zaimkow[zaim] = temp_entry


print("odmiana_zaimkow = {")
for i, k in ndicta_zaimkow.items():
    print(f'    "{i}": "{k}",')
print(f"}}  # {len(dicta_zaimkow):,}")


#kto/co/wszystko/nikt/nic