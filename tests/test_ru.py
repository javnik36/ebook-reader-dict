from typing import Callable, List

import pytest

from wikidict.render import parse_word
from wikidict.stubs import Definitions
from wikidict.utils import process_templates


@pytest.mark.parametrize(
    "word, pronunciations, genders, etymology, definitions, variants",
    [
        (
            "страница",
            ["страни"],
            ["f"],
            ["Происходит от"],
            [
                "одна из сторон листа бумаги в составе книги, газеты и\xa0т.\xa0п.",
                "написанный или напечатанный текст на такой стороне листа",
                "лист бумаги в составе книги, газеты и\xa0т.\xa0п.",
                "<i>(Комп.)</i> отдельный документ в составе интернет-сайта",
                "<i>(П.)</i> очередной этап в развитии чего-либо",
                "<i>(Информ.)</i> блок, регион фиксированного размера физической или виртуальной памяти (выделение памяти, передача данных между диском и оперативной памятью осуществляется целыми страницами)",  # noqa
            ],
            [],
        ),
        (
            "какой",
            [],
            [],
            ["Происходит от"],
            [
                "(вопросительное мест.) обозначает вопрос о качестве, свойствах",
                "(вопросительное мест.) <i>(T)</i>",
                "в риторич. вопросе или восклицат. ответном предл. выражает эмоциональное отрицание: вовсе не, никакой",
                "(определительное мест.) (восклиц. мест.) в восклицат. предл. обозначает удивление, радость, возмущение качеством чего-нибудь",  # noqa
                "(относительное мест.) с теми же знач., что [1], [2] и [3] подчиняет придаточное предложение главному",
                "(относительное мест.) обозначает соответствие качества какого-нибудь предмета в придаточном предложении качеству того же предмета в главном ((преимущ. при местоим. такой, таков, тот, тот же в главн. предл.))",  # noqa
                "(неопределённое мест.), <i>(Разг.)</i> <i>(T)</i>",
                "(неопределённое мест.), <i>(Разг.)</i> в сочетании с отриц. выражениями: неизвестно, неведомо, не знаю и\xa0т.\xa0п., употр. в знач. какой-то",  # noqa
                "(разделительное мест.) в соединении с другими относит. местоимениями: смотря какой, неодинаковый, различный",  # noqa
            ],
            [],
        ),
        (
            "коса",
            ["коса"],
            ["с", "m"],
            [
                "Родств. церковносл./укр./болг./серб. коса, польск./словац./др.-чеш. kosa. М. Фасмер неубедительно связывает с др.-исл. haddr (волосы, протогерм. *hazda-), ср.-ирл. cír (гребень), лит. kasa, kasyti, kasît, др.-инд. <i>kacchus</i>, авест. <i>kasvis</i>, а тж. чередованием гласных с чесать, чешу и косма. Э. Бернекер, М. Рясянен и др. сводят коса I, коса II и коса III к косой.",  # noqa
            ],
            [
                "вид укладки волос, при которой волосы собираются в несколько прядей и затем переплетаются",
                "<i>(Матем.)</i> объект, состоящий из двух параллельных плоскостей в трёхмерном пространстве, содержащих упорядоченные множества точек, и из непересекающихся между собой простых дуг, пересекающих каждую параллельную плоскость однократно",  # noqa
                "<i>(Сх)</i> сельскохозяйственное орудие для срезания травы и злаков, напоминающее серп на длинном древке с рукояткой",  # noqa
                "<i>(T)</i>",
                "ряд косарей, работающих в одной линии, плечом к плечу",
                "протяжённая речная отмель",
                "народность в Южной Африке",
                "название одного из языков Южной Африки",
            ],
            [],
        ),
        (
            "бита",
            [],
            ["f", "ж"],
            ["Происходит от"],
            [
                "предмет (палка, бабка и\xa0т.\xa0п.), которым бьют во время игры в городки, в бабки, в лапту и\xa0т.\xa0п.",  # noqa
                "<i>(Разг.)</i> отвёртка-вставка",
            ],
            [],
        ),
    ],
)
def test_parse_word(
    word: str,
    pronunciations: List[str],
    genders: List[str],
    etymology: List[Definitions],
    definitions: List[Definitions],
    variants: List[str],
    page: Callable[[str, str], str],
) -> None:
    """Test the sections finder and definitions getter."""
    code = page(word, "ru")
    details = parse_word(word, code, "ru", force=True)
    assert pronunciations == details.pronunciations
    assert genders == details.genders
    assert definitions == details.definitions
    assert etymology == details.etymology
    assert variants == details.variants


@pytest.mark.parametrize(
    "wikicode, expected",
    [
        ("{{этимология:страница|да}}", ""),
    ],
)
def test_process_templates(wikicode: str, expected: str) -> None:
    """Test templates handling."""
    assert process_templates("foo", wikicode, "ru") == expected
