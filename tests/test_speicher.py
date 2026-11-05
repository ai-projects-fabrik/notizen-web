"""Tests fuer den In-Memory-Speicher."""

import pytest

from projekt.speicher import NotizSpeicher


@pytest.mark.parametrize(
    ("titel", "erwartet"),
    [("x", "x"), ("x" * 80, "x" * 80), ("  " + "x" * 80 + "  ", "x" * 80)],
)
def test_titel_grenzwerte_sind_gueltig(titel, erwartet):
    speicher = NotizSpeicher()

    assert speicher.anlegen(titel, "")["titel"] == erwartet


@pytest.mark.parametrize("titel", ["", "   ", "x" * 81])
def test_titel_grenzwerte_werden_abgelehnt_ohne_id_zu_verbrauchen(titel):
    speicher = NotizSpeicher()

    with pytest.raises(ValueError):
        speicher.anlegen(titel, "text")
    assert speicher.anlegen("gueltig", "text")["id"] == 1


@pytest.mark.parametrize("laenge", [0, 2000])
def test_text_grenzwerte_sind_gueltig(laenge):
    speicher = NotizSpeicher()

    assert speicher.anlegen("Titel", "t" * laenge)["text"] == "t" * laenge


def test_zu_langer_text_wird_abgelehnt_ohne_id_zu_verbrauchen():
    speicher = NotizSpeicher()

    with pytest.raises(ValueError):
        speicher.anlegen("Titel", "t" * 2001)
    assert speicher.anlegen("Titel", "")["id"] == 1


def test_rueckgaben_von_anlegen_holen_und_liste_sind_kopien():
    speicher = NotizSpeicher()

    angelegt = speicher.anlegen("Titel", "Text")
    angelegt["titel"] = "veraendert"
    geholt = speicher.holen(1)
    geholt["text"] = "veraendert"
    aufgelistet = speicher.liste()[0]
    aufgelistet["id"] = 99

    assert speicher.holen(1) == {"id": 1, "titel": "Titel", "text": "Text"}


def test_loeschen_unbekannter_id_ist_key_error():
    speicher = NotizSpeicher()

    with pytest.raises(KeyError):
        speicher.loeschen(1)
