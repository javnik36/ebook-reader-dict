import re
from scripts_utils import get_soup

url = "https://pl.wiktionary.org/wiki/Pomoc:Skr%C3%B3ty_u%C5%BCywane_w_Wikis%C5%82owniku"

soup = get_soup(url)
dls = soup.find_all("dl")

skr = {}
skr2merge = {}

def add_first_or_secend_match(macze):
    if macze[0] != '':
        return (macze[0].strip(),macze[1].strip())
    else:
        return (macze[2].strip(),macze[3].strip())

for dl in dls:
    dds = dl.find_all("dd")

    #pattern = re.compile(r"(.+)\s\→\s(.+)\(szablon.+|(.+)\s\→\s(.+)\;\sszablon.+")
    #pattern = re.compile(r"(.+)\s\→\s(.+)\(szablon.+")
    pattern = re.compile(r"(.+)\s?\→\s(.+)\(szablon.+|(.+)\s?\→\s(.+)\;\sszablon.+")

    for dd in dds:
        found_patterns = pattern.findall(dd.text)
        if len(found_patterns) == 0:
            #handles "KEY → zob. DEF" cases
            #e.g. "afg. → zob. paszto"
            pattern_link = re.compile(r"(.+)\s\→\szob.\s(.+)")
            #handles other cases (no "szablon" or "szablon" in parenthesis)
            pattern_failover = re.compile(r"(.+)\s\→\s(.+)\,\sszablon.+|(.+)\s\→\s(.+)")
            try:
                found_patternlink = pattern_link.findall(dd.text)[0]
                skr2merge[found_patternlink[0].strip()] = found_patternlink[1].strip()
            except:
                found_pattern_failover = pattern_failover.findall(dd.text)[0]
                matches = add_first_or_secend_match(found_pattern_failover)
                skr[matches[0]] = matches[1]
                #if found_pattern_failover[0] != '':
                #    skr[found_pattern_failover[0].strip()] = found_pattern_failover[1].strip()
                #else:
                #    skr[found_pattern_failover[2].strip()] = found_pattern_failover[3].strip()
                #print("Failed maczing " + f"{dd.text}")

                #starosaski (.+)\s?\→\s(.+\([^\,]+)
                #starossaski i bez szabl (.+)\s\→\s(.+)\,\sszablon.+|(.+)\s\→\s(.+)
        elif len(found_patterns) > 1:
            for macz in found_patterns:
                ex_matches = add_first_or_secend_match(macz)
                skr[ex_matches[0]] = ex_matches[1]
           #print("Więcej maczów?! " + f"{dd.text}")
        else:
            first_pattern = found_patterns[0]
            first_matches = add_first_or_secend_match(first_pattern)

            skr[first_matches[0]] = first_matches[1]

            #if first_pattern[0] != '':
            #    skr[first_pattern[0].strip()] = first_pattern[1].strip()
            #else:
            #    skr[first_pattern[2].strip()] = first_pattern[3].strip()

for di,dk in skr2merge.items():
    skr[di] = skr.get(dk)

# remove templ with | in it
print("skr_list = {")
for i, k in sorted(skr.items()):
    print(f'    "{i}": "{k}",')
print(f"}}  # {len(skr):,}")
