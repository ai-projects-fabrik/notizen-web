"""Akzeptanztest (spec-first) fuer projekt.speicher: Beispiele aus dem Ziel `notizen-speicher`."""

import importlib.util

import pytest

if importlib.util.find_spec("projekt.speicher") is None:
    pytest.skip("Modul noch nicht umgesetzt", allow_module_level=True)

from projekt.speicher import NotizSpeicher  # noqa: E402

UNGUELTIG = [
    ("", "text"),
    ("   ", "text"),
    ("x" * 81, "text"),
    ("titel", "t" * 2001),
    (None, "text"),
    ("titel", None),
    (5, "text"),
]


def test_anlegen_vergibt_fortlaufende_ids_ab_eins():
    s = NotizSpeicher()
    assert s.anlegen("Einkauf", "Milch") == {"id": 1, "titel": "Einkauf", "text": "Milch"}
    assert s.anlegen("Post", "") == {"id": 2, "titel": "Post", "text": ""}


def test_titel_wird_getrimmt_und_grenzwerte_gelten():
    s = NotizSpeicher()
    assert s.anlegen("  Gruss  ", "hallo")["titel"] == "Gruss"
    assert s.anlegen("x" * 80, "t" * 2000)["id"] == 2


@pytest.mark.parametrize(("titel", "text"), UNGUELTIG)
def test_ungueltige_eingabe_ist_value_error_und_verbraucht_keine_id(titel, text):
    s = NotizSpeicher()
    with pytest.raises(ValueError):
        s.anlegen(titel, text)
    assert s.anlegen("ok", "ok")["id"] == 1


def test_holen_und_liste():
    s = NotizSpeicher()
    s.anlegen("a", "1")
    s.anlegen("b", "2")
    assert s.holen(2) == {"id": 2, "titel": "b", "text": "2"}
    assert [n["id"] for n in s.liste()] == [1, 2]
    with pytest.raises(KeyError):
        s.holen(3)


def test_rueckgaben_sind_kopien():
    s = NotizSpeicher()
    s.anlegen("a", "1")
    s.holen(1)["titel"] = "veraendert"
    s.liste()[0]["titel"] = "veraendert"
    assert s.holen(1)["titel"] == "a"


def test_loeschen_und_ids_werden_nicht_wiederverwendet():
    s = NotizSpeicher()
    s.anlegen("a", "1")
    s.anlegen("b", "2")
    assert s.loeschen(1) is None
    assert [n["id"] for n in s.liste()] == [2]
    assert s.anlegen("c", "3")["id"] == 3
    with pytest.raises(KeyError):
        s.loeschen(1)
