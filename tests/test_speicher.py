import pytest

from projekt.speicher import NotizSpeicher


def test_anlegen_trimmt_titel_und_vergibt_fortlaufende_ids():
    speicher = NotizSpeicher()

    assert speicher.anlegen("  Erste Notiz  ", "Text") == {
        "id": 1,
        "titel": "Erste Notiz",
        "text": "Text",
    }
    assert speicher.anlegen("Zweite Notiz", "")["id"] == 2


@pytest.mark.parametrize(
    ("titel", "text"),
    [
        ("", "text"),
        ("   ", "text"),
        ("x" * 81, "text"),
        ("titel", "x" * 2001),
        (None, "text"),
        ("titel", None),
        (5, "text"),
        ("titel", 5),
    ],
)
def test_ungueltige_eingabe_ist_value_error_ohne_id_zu_verbrauchen(titel, text):
    speicher = NotizSpeicher()

    with pytest.raises(ValueError):
        speicher.anlegen(titel, text)

    assert speicher.anlegen("Gueltig", "Text")["id"] == 1


def test_grenzwerte_von_titel_und_text_sind_erlaubt():
    speicher = NotizSpeicher()
    titel = "t" * 80
    text = "x" * 2000

    notiz = speicher.anlegen(titel, text)

    assert notiz == {"id": 1, "titel": titel, "text": text}
    assert speicher.holen(1) == notiz


def test_holen_und_liste_liefern_kopien():
    speicher = NotizSpeicher()
    angelegt = speicher.anlegen("Original", "Text")
    angelegt["titel"] = "veraendert"

    geholt = speicher.holen(1)
    geholt["text"] = "veraendert"
    gelistet = speicher.liste()
    gelistet[0]["titel"] = "veraendert"

    assert speicher.holen(1) == {"id": 1, "titel": "Original", "text": "Text"}
    assert speicher.liste() == [{"id": 1, "titel": "Original", "text": "Text"}]


def test_holen_unbekannter_id_ist_key_error():
    speicher = NotizSpeicher()

    with pytest.raises(KeyError):
        speicher.holen(1)


def test_loeschen_entfernt_notiz_und_gibt_none_zurueck():
    speicher = NotizSpeicher()
    speicher.anlegen("Bleibt", "Text")
    speicher.anlegen("Faellt weg", "Text")

    assert speicher.loeschen(2) is None
    assert speicher.liste() == [{"id": 1, "titel": "Bleibt", "text": "Text"}]


def test_loeschen_unbekannter_id_ist_key_error():
    speicher = NotizSpeicher()

    with pytest.raises(KeyError):
        speicher.loeschen(1)


def test_ids_werden_nach_loeschen_nicht_wiederverwendet():
    speicher = NotizSpeicher()
    speicher.anlegen("Erste", "Text")
    speicher.anlegen("Zweite", "Text")
    speicher.loeschen(2)

    assert speicher.anlegen("Dritte", "Text")["id"] == 3
