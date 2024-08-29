import wikitextparser as wtp
from typing import List
import re
#plik = open("./kot.wiki","r")
#plik.close()


kot_def = '''=== {{znaczenia}} ===
# ''rzeczownik, rodzaj męskozwierzęcy''
## (1.1) {{zool}} {{nazwa systematyczna|Felis catus|Linnaeus|ref=tak}}, [[zwierzę domowe]]; {{wikipedia|kot domowy}}
## (1.2) {{zool}} [[każdy|każde]] [[zwierzę]] [[drapieżny|drapieżne]] [[z]] [[rodzina|rodziny]] {{nazwa systematyczna|Felidae|G. Fischer|ref=tak}}, [[o]] [[smukły]]m [[ciało|ciele]], [[miękki]]ej [[sierść|sierści]] [[i]] [[długi]]m [[ogon]]ie
## (1.3) {{łow}} [[samiec]] [[zając]]a
## (1.4) {{pot}} [[kłąb]] [[kurz]]u [[zbierać|zbierającego]] [[się]] [[w]] [[zakamarek|zakamarkach]] [[mieszkanie|mieszkania]]
## (1.5) {{daw}} [[młode zwierzę]]
# ''rzeczownik, rodzaj męskoosobowy''
## (2.1) {{slang}} [[rekrut]], [[nowy]] [[uczeń]]
'''

kspar = wtp.parse(kot_def)
k1l = kspar.get_lists()
k2l = []
# for i in k1l:
#     for idx,code in enumerate(i.items):
#         for sublist in i.sublists():
#             k2l.append(sublist)
dd = 0





def render_wzor(
        tpl: str,
        parts: List[str]
)-> str:
    # Pythonized version of code from https://pl.wiktionary.org/wiki/Modu%C5%82:wz%C3%B3r_chemiczny
    #{{wzór chemiczny|PbSO4}} CaMg[Si2O6]
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
            return f"{
                (x)}"
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


print(render_wzor("tpl",['PbSO4']))
print(render_wzor('tpl',['CaMg[Si2O6]']))
print(render_wzor('tpl',['C6H2(NO2)3CH3']))
print(render_wzor('tpl',['SO4(2-)']))


def uniq(seq: List[str]) -> List[str]:
    """
    Return *seq* without duplicates.

        >>> uniq(["foo", "foo"])
        ['foo']
    """
    res: List[str] = []
    for item in seq:
        if item not in res:
            res.append(item)
    return res

def render_wzor(
        tpl: str,
        parts: List[str]
)-> str:
    #{{wzór chemiczny|PbSO4}}
    chimy_parts = []
    # lp = 0
    wzor = parts[-1]
    # for i in range(0,len(wzor)):
    #     curr_char = wzor[i]
    #     if curr_char.isnumeric():
    #         chimy_parts.append(wzor[lp:i])
    #         lp=i
    # chimy_parts.append(wzor[lp:])

    if parenth := re.search("\(.+\)", wzor):
        for p in parenth:
            if ("+", "-") in p:
                wzor.replace(p,"SP")
            
            
    return chimy_parts

c=render_wzor("kasljalk", ["Pb2SO4Al8"])


kot ='''{{podobne|-kot|Kot|kott|kòt|köt|kött}}
== kot ({{język polski}}) ==
[[Plik:Felis catus-cat on snow.jpg|thumb|kot (1.1)]]
[[Plik:Snow Leopard at the Toronto Zoo.jpg|thumb|kot (1.2)]]
[[Plik:01-sfel-08-009a.jpg|thumb|kot (1.3)]]
[[Plik:Dust bunnies.jpg|thumb|koty (1.4)]]
[[Plik:Marine Corps drill instructor yells at recruit.jpg|thumb|kot (2.1)]]
=== {{wymowa}} ===
: {{IPA3|kɔt}}, {{AS3|kot}}
: {{homofony|kod}}
: {{audio|Pl-kot.ogg}}, {{audio|LL-Q809 (pol)-Olaf-kot.wav}} {{audio|LL-Q809 (pol)-Gower-kot.wav}}
=== {{znaczenia}} ===
''rzeczownik, rodzaj męskozwierzęcy''
: (1.1) {{zool}} {{nazwa systematyczna|Felis catus|Linnaeus|ref=tak}}, [[zwierzę domowe]]; {{wikipedia|kot domowy}}
: (1.2) {{zool}} [[każdy|każde]] [[zwierzę]] [[drapieżny|drapieżne]] [[z]] [[rodzina|rodziny]] {{nazwa systematyczna|Felidae|G. Fischer|ref=tak}}, [[o]] [[smukły]]m [[ciało|ciele]], [[miękki]]ej [[sierść|sierści]] [[i]] [[długi]]m [[ogon]]ie
: (1.3) {{łow}} [[samiec]] [[zając]]a
: (1.4) {{pot}} [[kłąb]] [[kurz]]u [[zbierać|zbierającego]] [[się]] [[w]] [[zakamarek|zakamarkach]] [[mieszkanie|mieszkania]]
: (1.5) {{daw}} [[młode zwierzę]]
''rzeczownik, rodzaj męskoosobowy''
: (2.1) {{slang}} [[rekrut]], [[nowy]] [[uczeń]]
=== {{odmiana}} ===
: (1.1-4) {{odmiana-rzeczownik-polski
|Mianownik lp = kot
|Dopełniacz lp = kota
|Celownik lp = kotu
|Biernik lp = kota
|Narzędnik lp = kotem
|Miejscownik lp = kocie
|Wołacz lp = kocie
|Mianownik lm = koty
|Dopełniacz lm = kotów
|Celownik lm = kotom
|Biernik lm = koty
|Narzędnik lm = kotami
|Miejscownik lm = kotach
|Wołacz lm = koty
}}
: (2.1) {{odmiana-rzeczownik-polski
|Mianownik lp = kot
|Dopełniacz lp = kota
|Celownik lp = kotowi
|Biernik lp = kota
|Narzędnik lp = kotem
|Miejscownik lp = kocie
|Wołacz lp = kocie
|Mianownik lm = koty
|Dopełniacz lm = kotów
|Celownik lm = kotom
|Biernik lm = kotów
|Narzędnik lm = kotami
|Miejscownik lm = kotach
|Wołacz lm = koty
|Forma ndepr = kotowie
}}
=== {{przykłady}} ===
: (1.1) ''[[kot|Kot]] [[gonić|goni]] [[za]] [[mysz]]ą.''
: (1.1) ''[[a|A]] [[jaki]] [[być|jest]] [[twój]] [[kot]]?''<ref>[https://www.youtube.com/watch?v=CQK2yclikf0 KOT JAKO CZŁOWIEK]</ref>
: (1.2) ''[[kot|Koty]] [[umieszczać|umieszczone]] [[być|są]] [[w]] [[północny]]m [[sektor]]ze [[zoo]].''
: (1.3) ''[[on|On]] [[wczoraj]] [[złapać|złapał]] [[kot]]a.''
: (1.4) ''[[Rozalia]] [[zamiatać|zamiotła]] [[kot]]y [[kurz]]u [[pod]] [[dywan]].''
: (2.1) ''[[bardzo|Najbardziej]] [[ekscytować|ekscytującym]] [[aspekt]]em [[służba|służby]] [[wojskowy|wojskowej]] [[być|jest]] [[bycie]] [[kot]]em.''
=== {{składnia}} ===
=== {{kolokacje}} ===
: (1.1) kot [[miauczeć|miauczy]] / [[drapać|drapie]] / [[mruczeć|mruczy]] / [[polować|poluje]] / [[marcować|marcuje]] • [[dać]] kotu [[mleko|mleka]] • [[karmić]] / [[dokarmiać]] / [[głaskać]] / [[hodować]] / [[oswoić]] / [[trzymać]] / [[pielęgnować]] kota • [[pokarm]] [[dla]] kotów • [[wystawa]] kotów [[rasowy]]ch • [[łasić się]] [[jak]] kot • [[chodzić]] [[cicho]] [[jak]] kot • [[poruszać się]] [[jak]] kot • [[opiekować się]] kotem • [[bawić się]] / [[chodzić]] [[na]] [[spacer]] [[z]] kotem • [[bezdomny]] / [[bezpański]] kot
=== {{synonimy}} ===
: (1.1) [[kot domowy]]; {{żart}} [[dachołaz]], [[dachowiec]]; {{pogard}} [[sierściuch]], [[futrzak]]; {{poznań|[[kociamber]]}}, {{lwów|[[kacaraba]]}}
: (1.4) [[farfocel]]
=== {{antonimy}} ===
=== {{hiperonimy}} ===
=== {{hiponimy}} ===
: (1.1) [[kot bengalski]] • [[kot perski]] • [[kot syjamski]] • [[kot europejski]] • [[kot norweski leśny]] • [[kot nubijski]]
: (1.2) [[kot bagienny]] • [[kot bengalski]] • [[kot błotny]] • [[kot nubijski]] • [[kot trzcinowy]]
=== {{holonimy}} ===
=== {{meronimy}} ===
=== {{pokrewne}} ===
: {{rzecz}} [[kotka]] {{ż}}, [[kocica]] {{ż}}, [[kocię]] {{n}}, [[kocik]] {{mzw}}, [[kocur]] {{mzw}}, [[kociarz]] {{mos}}, [[kociara]] {{ż}}, [[kocimiętka]] {{ż}}, [[kociarstwo]] {{n}}, [[kociamber]] {{mos}}/{{mzw}}, [[kociokwik]] {{mrz}}
:: {{zdrobn}} [[kotek]] {{mzw}}, [[kociak]] {{mzw}}, [[koteczek]] {{mzw}}, [[kociaczek]] {{mzw}}
:: {{zgrub}} [[kocisko]] {{n}}, [[kocurzysko]] {{n}}
: {{czas}} [[kocić się]], [[kocić]] {{ndk}}, [[okocić]] {{dk}}, [[wykocić]] {{dk}}, [[kotować]] {{ndk}}
: {{przym}} [[koci]], [[kociarski]], [[kotny]], [[kotowaty]]
: {{przysł}} [[kocio]]
: {{temsłow}} [[kocio-]]
=== {{frazeologia}} ===
: [[bawić się jak kot z myszą]] / [[bawić się w kotka i myszkę]] • [[biegać jak kot oparzony]] / [[biegać jak kot zagorzały]] • [[bodaj tak kot płakał]] • [[być łasym jak kot na myszy]] • {{gwara}} [[bystry jak Maćków kot]] • [[chadzać jak kot własnymi drogami]] / [[kot zawsze chadza własnymi ścieżkami]] • [[chodzić jak kot po gorącej blasze]] • [[ciągnąć kota]] • [[dostać kota]] / [[dostawać kota]] • [[drzeć koty]] • [[drzeć się jak pies z kotem]] / [[gryźć się jak pies z kotem]] / [[lubić się jak pies z kotem]] / [[zgodzić się jak pies z kotem]] / [[żreć się jak pies z kotem]] / [[żyć jak pies z kotem]] • [[fałszywy jak kot]] • [[jak kot z pęcherzem]] • [[kochliwy jak kot w marcu]] • [[kota paść]] • [[kot mu za uchem wrzeszczy]] • [[kot Schrödingera]] • [[kot w butach]] • [[kot zawsze spada na cztery łapy]] • {{daw}} [[koty w prawie]] • [[kupować kota w miechu]]<ref>Antoni Danysz, ''Odrębności słownikarskie kulturalnego języka polskiego w Wielkopolsce w stosunku do kulturalnego języka w Galicyi'', „Język Polski” nr 8–10, s. 249.</ref> / [[kupować kota w worku]] • [[mieć kota]] • [[mieć kota na punkcie]] • [[mieć minę jak kot srający na puszczy]] / [[mieć minę jak kot srający na pustyni]] • [[myszy tańcują, gdy kota nie czują]] • [[nie głaskać kota pod włos]] • [[odwracać kota ogonem]] / [[wykręcać kota ogonem]] • [[parszywy jak kot]] • [[patrzeć jak kot na szperkę]] • [[pierwsze koty za płoty]] • [[pogonić kota]] / [[popędzić kota]] • [[puszczać kota na czysto]] • [[rzygać jak kot]] • [[spaść jak kot na cztery łapy]] • [[spaść na cztery łapy]] • [[tłusty kot]] • [[widzieć jak kot]] • [[w marcu koty, w kwietniu psy, a dopiero w maju my]] • [[w nocy wszystkie koty są bure]] / [[w nocy wszystkie koty są czarne]] / [[w nocy wszystkie koty są szare]] • [[tyle, co kot napłakał]] • [[znać się jak kot na kwaśnym mleku]]
: zobacz też: [[Aneks:Przysłowia polskie - zwierzęta#kot|przysłowia o kotach]]
=== {{etymologia}} ===
: ''od'' {{etym|prasł|*kotъ}}<ref name="WSJP">{{WSJPonline|id=29368}}</ref><ref name="ESSJa">{{ESSJa|tom=XI|strony=209 i 210}}</ref> → kot (1.1), ''od'' {{etym|łac|cattus}}<ref name="WSJP" />
: {{por}} {{etymn|białor|кот}}, {{dial}} {{etymn|bułg|кот}}, {{dial}} {{etymn|czes|kot}}, {{etymn|dłuż|kót}}, {{etymn|ros|кот}}, {{dial}} {{etymn|słc|kot}} ''i'' {{etym2n|ukr|кіт|кіт}}
: {{por}} {{etymn|ang|cat}}, {{etymn|hiszp|gato}}, {{etymn|niem|Katze}}, {{etymn|szw|katt}} ''i'' {{etymn|wł|gatto}}
: ''dzikie koty określano w czasach prasłowiańskich nazwą'' {{*}}stьbljь<ref name="ESSJa" />, ''od czego pochodzi'' {{etymn|pl|żbik}}, {{zob|żbik#pl|''tamże''}}
=== {{uwagi}} ===
: {{wikicytaty}}
: (1.1-2) zobacz też: [[Indeks:Polski - Ssaki]]
=== {{tłumaczenia}} ===
* abazyński: (1.1) [[цгвы]] (cgvy)
* abchaski: (1.1) [[ацгә]] (acgw)
* aceh: (1.1) [[mië]]
* adygejski: (1.1) [[кӏэтыу]] (č̣̍ătəw)
* afrykanerski: (1.1) [[kat]]
* ajnoski: (1.1) [[チャペ]] (cape)
* akan: (1.1) [[agyinamoa]]
* albański: (1.1) [[mace]] {{ż}}
* alemański: (1.1) [[Chatz]] {{ż}}
* amharski: (1.1) [[ድመት]]
* angielski: (1.1) [[cat]]; (1.4) [[dust bunny]]; (2.1) [[freshman]]
* arabski: (1.1) [[قط]], [[هر]], {{marokarab|[[مش]]}}, {{libijarab|[[قطوسة]]}}, {{libijarab|[[قطوس]]}}
* awarski: (1.1) [[кето]]
* bambara: (1.1) [[jakuma]]
* baskijski: (1.1) [[katu]]
* bawarski: (1.1) [[Katz]]
* białoruski: (1.1) [[кот]] {{m}}
* bretoński: (1.1) [[kazh]]
* bułgarski: (1.1) [[котка]] {{ż}}
* chiński standardowy: (1.1) [[猫]] (māo)
* chorwacki: (1.1) [[mačka]] {{ż}}
* czeski: (1.1) [[kočka]] {{ż}}
* dolnołużycki: (1.1) [[kócka]] {{ż}}
* duński: (1.1) [[kat]] {{w}}; (1.2) [[kat]] {{w}}
* esperanto: (1.1) [[kato]]
* estoński: (1.1) [[kass]]
* farerski: (1.1) [[ketta]], [[kattur]]
* fiński: (1.1) [[kissa]]
* francuski: (1.1) [[chat]] {{m}}; (1.3) [[hase]] {{ż}}; (1.4) {{pot}} [[mouton]] {{m}}, {{pot}}[[chaton]] {{m}}; (2.1) {{slang}} [[bleu]] {{m}}
* friulski: (1.1) [[gjat]]
* fryzyjski: (1.1) [[kat]]
* galicyjski: (1.1) [[gato]]
* górnołużycki: (1.1) [[kóčka]]
* grenlandzki: (1.1) [[qitsuk]]
* gruziński: (1.1) [[კატა]] (k'at'a)
* hausa: (1.1) [[mussa]]
* hawajski: (1.1) [[pōpoki]]
* hebrajski: (1.1) [[חתול]] {{m}} (chatúl)
* hindi: (1.1) [[बिल्ली]] {{ż}} (billī)
* hiszpański: (1.1) [[gato]] {{m}}; (1.2) [[felino]] {{m}}; (1.4) [[mota]] [[de]] [[polvo]] {{ż}}
* indonezyjski: (1.1) [[kucing]]
* interlingua: (1.1) [[catto]]
* irlandzki: (1.1) [[cat]]
* islandzki: (1.1) [[köttur]] {{m}}
* japoński: (1.1) [[猫]] ([[ねこ]], neko)
* jawajski: (1.1) [[ꦏꦸꦕꦶꦁ]] / [[kucing]]
* jidysz: (1.1) [[קאַץ]] {{ż}} (kac)
* joruba: (1.1) [[ológbò]], [[ológìnní]], [[músù]], [[èse]]
* kabylski: (1.1) [[amcic]]
* karelski: (1.1) [[kazi]], [[kaži]]
* karpatorusiński: (1.1) [[мачка]] {{ż}}, [[мацур]] {{m}} ''(samiec)''
* kaszubski: (1.1) [[pùjk]] {{m}}, [[kòt]] {{m}}
* kataloński: (1.1) [[gat]], [[moix]]
* kazachski: (1.1) [[мысық]]
* keczua: (1.1) [[misi]]
* kikuju: (1.1) [[mbaka]]
* kirgiski: (1.1) [[мышык]]
* koreański: (1.1) [[고양이]] (koyangi)
* ladyński: (1.1) [[giat]]
* litewski: (1.1) [[katė]] {{ż}}
* łaciński: (1.1) [[felis]] {{ż}}
* łotewski: (1.1) [[kaķis]]
* macedoński: (1.1) [[мачка]] {{ż}}
* malajski: (1.1) [[kucing]]
* maltański: (1.1) [[qattus]]
* mongolski: (1.1) [[муур]]
* nepalski: (1.1) [[बिरालो]] (birālō)
* niderlandzki: (1.1) [[kat]]
* niemiecki: (1.1) [[Katze]] {{ż}}
* norweski (bokmål): (1.1) [[katt]] {{m}}
* norweski (nynorsk): (1.1) [[katt]] {{m}}
* nowogrecki: (1.1) [[γάτα]] {{ż}}
* orija: (1.1) [[ବିଲେଇ]] (bilēi)
* ormiański: (1.1) [[կատու]]
* perski: (1.1) [[گربه]] (gorbe)
* polski język migowy: {{PJM-ukryj| (1.1) {{PJM|kot}}}}
* portugalski: (1.1) [[gato]] {{m}}
* prowansalski: (1.1) [[cat]]
* romansz: (1.1) [[giat]]
* rosyjski: (1.1) [[кошка]] {{ż}}, [[кот]] {{m}} ''(samiec)''; (2.1) [[дух]]
* rumuński: (1.1) [[pisică]] {{ż}}
* sanskryt: (1.1) [[ओतु]], [[काहल]]
* sardyński: (1.1) [[gattu]]
* serbski: (1.1) [[мачка]] {{ż}}
* slovio: (1.1) [[kot]]
* słowacki: (1.1) [[mačka]] {{ż}}
* słoweński: (1.1) [[mačka]] {{ż}}
* sranan tongo: (1.1) [[puspusi]]
* suahili: (1.1) [[paka]]
* sycylijski: (1.1) [[jattu]] {{m}}
* szkocki: (1.1) [[cat]]
* szwedzki: (1.1) [[katt]] {{w}}; (1.4) [[dammråtta]] {{w}}
* średnio-wysoko-niemiecki: (1.1) [[katze]] {{ż}}
* tahitański: (1.1) [[mīmī]]
* tajski: (1.1) [[แมว]]
* turecki: (1.1) [[kedi]]
* tuvalu: (1.1) [[puusi]]
* udmurcki: (1.1) [[коӵыш]] (kočyš)
* ukraiński: (1.1) [[кіт]] {{m}}
* uzbecki: (1.1) [[mushuk]]
* walijski: (1.1) [[cath]]
* warajski: (1.1) [[kucing]]
* wepski: (1.1) [[kaži]]
* węgierski: (1.1) [[macska]]
* wilamowski: (1.1) [[koc]]
* włoski: (1.1) [[gatto]] {{m}}
* zulu: (1.1) [[ikati]] ''klasa 5/6'', [[ingobe]] ''klasa 5/6''
=== {{źródła}} ===
<references />'''




sparsowane = wtp.parse(kot)
level=2
section_sublevels = (3,)
head_sections = "{{język polski}}"

def section_title(title: str, flag: int) -> str:
    if flag == 1:
        return title.split("(")[-1].strip(" )")
    return title.replace(" ", "").lower().strip() if title else ""

top_sections =[]


for section in sparsowane.get_sections(include_subsections=True,level=level):
    print(section_title(section.title,1))
    if section_title(section.title,1) in head_sections:
        top_sections.append(section)

top_sections2 = [
    section
    for section in sparsowane.get_sections(include_subsections=True, level=level)
    if section_title(section.title,1) in head_sections
]
all_sections=[]
all_sections.extend(
    (
        (section.title.strip(), section)
        for top_section in top_sections
        for sublevel in section_sublevels
        for section in top_section.get_sections(include_subsections=False, level=sublevel)
    )
)

parts=["Mianownik lp = Urban", "Dopełniacz lp = Urbana", "Celownik lp = Urbanowi", "Biernik lp = Urbana", "Narzędnik lp = Urbanem", "Miejscownik lp = Urbanie", "Wołacz lp = Urbanie", "Mianownik lm = Urbanowie", "Dopełniacz lm = Urbanów", "Celownik lm = Urbanom", "Biernik lm = Urbanów", "Narzędnik lm = Urbanami", "Miejscownik lm = Urbanach", "Wołacz lm = Urbanowie", "Forma depr = Urbany"]

variants = []
for inflection in parts:
    if inflection := inflection.split("=")[-1].strip():
        variants.append(inflection)

variants = uniq(variants)


h=0


"""
== dowalić ({{język polski}}) ==
{{wymowa}}
{{znaczenia}}
''czasownik dokonany ({{ndk}} [[dowalać]])''
: (1.1) {{dok}} ''od:'' [[dowalać]]
: (1.2) {{pot}} [[mocno]] [[ktoś|kogoś]] [[uderzyć]]
: (1.3) {{pot}} ''o śniegu:'' [[spaść]] [[w]] [[dużo|dużej]] [[ilość|ilości]]
: (1.4) {{pot}} [[powiedzieć]] [[coś]] [[niewłaściwy|niewłaściwego]], [[nieprawidłowy|nieprawidłowego]], [[szokujący|szokującego]] [[w]] [[dany|danej]] [[sytuacja|sytuacji]]
: (1.5) {{pot}} [[pokonać]] [[ktoś|kogoś]] [[w]] [[rywalizacja|rywalizacji]]
''czasownik zwrotny dokonany '''dowalić się''' ({{ndk}} [[dowalać|dowalać się]])''
: (2.1) {{dok}} ''od:'' [[dowalać|dowalać się]]
{{odmiana}}
: (1.1-5) {{odmiana-czasownik-polski
| dokonany = tak
| koniugacja = 
| zrobię = dowalę
| zrobi = dowali
| zrobią = dowalą
| zrobiłem = dowaliłem
| zrobił = dowalił
| zrobiła = dowaliła
| zrobili = dowalili
| zrobiono =
| zrób =
| zrobiwszy = dowaliwszy
| zrobiony =
| zrobieni =
| zrobienie = dowalenie
}}
: (2.1) {{odmiana-czasownik-polski
| dokonany= tak
| się = się
| koniugacja = 
| zrobię = dowalę
| zrobi = dowali
| zrobią = dowalą
| zrobiłem = dowaliłem
| zrobił = dowalił
| zrobiła = dowaliła
| zrobili = dowalili
| zrobiono =   
| zrób =
| zrobiwszy = dowaliwszy
| zrobiony =
| zrobieni =
| zrobienie =dowalenie
}}
{{przykłady}}
: (1.2) ''Niech będzie to pojedynek słowny, ale i gdyby któryś dowalił pięścią, to może by na tym skorzystał naród.''<ref>{{NKJP|tytuł_mag=Gazeta Wyborcza|tytuł_art=Telefoniczna opinia publiczna|data=1992-03-11|hash=9d072cd68e52635da747c4f0d1e10cf7|match_start=871|match_end=878}}</ref>
: (1.3) ''Wczoraj wieczorem dowaliło 30 centymetrów śniegu w mojej wiosce''
: (1.5) 
{{składnia}}
: (1.2) dowalać + {{C}}
: (2.1) dowalać się + [[do]] + {{D}}, [[za]] + {{B}}
: (2.2) dowalać się + [[do]] + {{D}}
{{kolokacje}}
{{synonimy}}
{{antonimy}}
{{hiperonimy}}
{{hiponimy}}
{{holonimy}}
{{meronimy}}
{{pokrewne}}
{{frazeologia}}
{{etymologia}}
{{uwagi}}
{{tłumaczenia}}
{{źródła}}
<references />

"""


"""== piorunować ({{język polski}}) ==
{{wymowa}}
{{znaczenia}}
''czasownik niedokonany'' ({{dk}} [[spiorunować]])
: (1.1) gwałtownie krytykować kogoś lub coś
: (1.2) gniewnie spoglądać<ref>{{DoroszewskiOnline}}</ref>
: (1.3) przeklinać
: (1.4) {{daw}} strzelać, miotać piorunami<ref>{{Karłowicz1900}}</ref>
{{odmiana}}
{{przykłady}}
: (1.1) 
: (1.2) ''Odwrócił się do gospodarzy, zanim żona przestała [[piorunować]] męża wzrokiem.''<ref>{{NKJP|autorzy=Eugeniusz Dębski|tytuł_pub=Aksamitny Anschluss|data=2001|hash=2d4345b10d72e847d4506e7154d3eb6a|match_start=49|match_end=59}}</ref>
{{składnia}}
: piorunować + {{B}}, piorunować + na + {{B}}
{{kolokacje}}
: piorunować wzrokiem
{{synonimy}}
{{antonimy}}
{{hiperonimy}}
: (1.1) krytykować
: (1.3) przeklinać, kląć
{{hiponimy}}
{{holonimy}}
{{meronimy}}
{{pokrewne}}
: {{rzecz}} [[piorun]] {{mrz}}, [[piorunian]] {{mrz}}
: {{przym}} [[piorunowy]], [[pioruński]], [[piorunujący]]
: {{przysł}} [[piorunem]], [[pioruńsko]]
{{frazeologia}}
{{etymologia}}
{{etymn|pl|piorun}}
{{uwagi}}
{{tłumaczenia}}
* wilamowski: (1.3) [[vātyn]], [[waotyn]], [[watyn]]
{{źródła}}
<references />
"""