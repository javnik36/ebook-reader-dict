from typing import Dict, List

from scripts_utils import get_content

url = "https://{0}.wiktionary.org/w/api.php?action=query&meta=siteinfo&siprop={1}&format=json"

# https://en.wiktionary.org/wiki/Wiktionary:Namespace
ids = {6, 14}  # File, and Category

results: Dict[str, List[str]] = {}
locales = ("ca", "da", "de", "el", "en", "es", "fr", "it", "no", "pl", "pt", "ro", "ru", "sv")

for locale in locales:
    result_discard_last: List[str] = []
    for kind in ("namespaces", "namespacealiases"):
        json = get_content(url.format(locale, kind), as_json=True)
        data = json["query"][kind]
        if kind == "namespaces":
            result_discard_last.extend(data[str(id_)]["*"] for id_ in ids)
        else:
            result_discard_last.extend(namespace["*"] for namespace in data if namespace["id"] in ids)
    results[locale] = sorted(result_discard_last)

print("namespaces =", end=" ")
print(results)
