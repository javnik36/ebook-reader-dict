from typing import Callable, List

import pytest

from wikidict.render import parse_word
from wikidict.stubs import Definitions
from wikidict.utils import process_templates


@pytest.mark.parametrize(
    "word, pronunciations, etymology, definitions, variants",
    [
        (
            "kot",
            [
                "<span style='font-variant:small-caps'>AS:</span> [kot]",
                "<span style='font-variant:small-caps'>IPA:</span> [k\u0254t]"
            ],
            [
                "<i>od</i> <i>pras\u0142owia\u0144ski</i> *kot\u044a \u2192 kot (1.1), <i>od</i> <i>\u0142aci\u0144ski</i> cattus",
                "<i>bia\u0142oruski</i> \u043a\u043e\u0442, <i>dialekt</i> <i>bu\u0142garski</i> \u043a\u043e\u0442, <i>dialekt</i> <i>czeski</i> kot, <i>dolno\u0142u\u017cycki</i> k\u00f3t, <i>rosyjski</i> \u043a\u043e\u0442, <i>dialekt</i> <i>s\u0142owacki</i> kot <i>i</i> <i>ukrai\u0144ski</i> \u043a\u0456\u0442",
                "<i>angielski</i> cat, <i>hiszpa\u0144ski</i> gato, <i>niemiecki</i> Katze, <i>szwedzki</i> katt <i>i</i> <i>w\u0142oski</i> gatto",
                "<i>dzikie koty okre\u015blano w czasach pras\u0142owia\u0144skich nazw\u0105</i> (s\u0142owo rekonstruowane)st\u044cblj\u044c, <i>od czego pochodzi</i> <i>polski</i> \u017cbik, <i>zobacz</i> <i>tam\u017ce</i>"
            ],
            [
                "(1.1) <i>zoologia, zoologiczny</i> <i>Felis catus</i> <span style='font-variant:small-caps'>Linnaeus</span>, zwierz\u0119 domowe;",
                "(1.2) <i>zoologia, zoologiczny</i> ka\u017cde zwierz\u0119 drapie\u017cne z rodziny <i>Felidae</i> <span style='font-variant:small-caps'>G. Fischer</span>, o smuk\u0142ym ciele, mi\u0119kkiej sier\u015bci i d\u0142ugim ogonie",
                "(1.3) <i>\u0142owiectwo, \u0142owiecki</i> samiec zaj\u0105ca",
                "(1.4) <i>potocznie, potoczny</i> k\u0142\u0105b kurzu zbieraj\u0105cego si\u0119 w zakamarkach mieszkania",
                "(1.5) <i>dawniej, dawny</i> m\u0142ode zwierz\u0119",
                "(2.1) <i>slangowo</i> rekrut, nowy ucze\u0144"
            ],
            [],
        ),
    ]
)
def test_parse_word(
    word: str,
    pronunciations: List[str],
    etymology: List[Definitions],
    definitions: List[Definitions],
    variants: List[str],
    page: Callable[[str, str], str],
) -> None:
    """Test the sections finder and definitions getter."""
    code = page(word, "pl")
    details = parse_word(word, code, "pl", force=True)
    assert pronunciations == details.pronunciations
    assert etymology == details.etymology
    assert definitions == details.definitions
    assert variants == details.variants

@pytest.mark.parametrize(
    "wikicode, expected",
    [
        ("{{stopn|szybciej|najszybciej}}", "<i>stopień wyższy</i> szybciej; <i>stopień najwyższy</i> najszybciej"),
        ("{{zob|[[słoń]], [[nosorożec]]}}", "<i>zobacz</i> słoń, nosorożec"),
        ("{{zob|słoń#pl|słoń}}", "<i>zobacz</i> słoń"),
        ("{{skrócenie od|słoń}}", "<i>forma skrócona od</i> słoń"),
        ("{{skrócenie od|[[słoń]], [[nosorożec]]}}", "<i>forma skrócona od</i> słoń, nosorożec"),
        ("{{odczasownikowy od|nie|robić}}", "<i>rzeczownik odczasownikowy od</i> nie robić"),
        ("{{odczasownikowy od|robić}}", "<i>rzeczownik odczasownikowy od</i> robić"),
        ("{{odprzymiotnikowy od|łapczywy}}", "<i>rzeczownik odprzymiotnikowy od</i> łapczywy"),
        ("{{gw-pl|Poznań}}", "<i>gwara, gwarowy</i> (<i>Poznań</i>)"),
        ("{{gw-pl|Łódź, Warszawa|[[polywka]]}}", "<i>gwara, gwarowy</i> (<i>Łódź, Warszawa</i>) polywka"),
        ("{{reg-pl|Poznań}}", "<i>regionalizm, regionalny</i> (<i>Poznań</i>)"),
        ("{{reg-pl|Łódź, Warszawa|[[polywka]]}}", "<i>regionalizm, regionalny</i> (<i>Łódź, Warszawa</i>) polywka"),
        ("{{plural|Cielętnik}}", "<i>liczba mnoga od</i> Cielętnik"),
        ("{{dokonany od|opóźniać się}}", "<i>aspekt dokonany od</i> opóźniać się"),
        ("{{niedokonany od|opóźniać się}}", "<i>aspekt niedokonany od</i> opóźniać się"),
        ("{{IPA2|ʧ}}", "/ʧ/"),
        ("{{IPA4|w}}", "[w]"),
        ("{{źle|poszłem}}", "<s>poszłem</s>"),
        ("{{nie mylić z|poddawać}}", "nie mylić z: poddawać"),
        ("{{nie mylić z|březnový|marcowy}}", "nie mylić z: březnový → marcowy"),
        ("{{*}}", "(słowo rekonstruowane)"),
        ("{{pinyin}}", "<i>pinyin</i>"),
        ("{{pinyin|yī běn shū}}", "<i>pinyin</i> yī běn shū"),
        ("{{pinyin|yī běn shū|yi1 ben3 shu1}}", "<i>pinyin</i> yī běn shū (yi1 ben3 shu1)"),
        ("{{forma przymiotnika|pl}}", "<i>przymiotnik, forma fleksyjna</i>"),
        ("{{forma zaimka|pl}}", "zaimek, forma fleksyjna"),
        ("{{forma czasownika|pl}}", "czasownik, forma fleksyjna"),
        ("{{translit|ru|уникальный}}", "unikalʹnyj"),
        ("{{translit|uk|йолоп}}", "jolop")
    ],
)
def test_process_templates(wikicode: str, expected: str) -> None:
    """Test templates handling."""
    assert process_templates("foo", wikicode, "pl") == expected