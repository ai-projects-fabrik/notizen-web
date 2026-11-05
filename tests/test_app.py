import io
import json
from wsgiref.util import setup_testing_defaults

import pytest

from projekt.app import erzeuge_app
from projekt.speicher import NotizSpeicher


def anfrage(app, methode, pfad, daten=None, roh=None, content_length=None):
    body = roh if roh is not None else (json.dumps(daten).encode() if daten is not None else b"")
    env = {}
    setup_testing_defaults(env)
    env.update(
        REQUEST_METHOD=methode,
        PATH_INFO=pfad,
        CONTENT_LENGTH=str(len(body)) if content_length is None else content_length,
        CONTENT_TYPE="application/json",
    )
    env["wsgi.input"] = io.BytesIO(body)
    kopf = {}

    def start(status, headers, exc_info=None):
        kopf["status"] = int(status.split()[0])
        kopf["headers"] = {name.lower(): wert for name, wert in headers}

    out = b"".join(app(env, start))
    return kopf["status"], kopf["headers"], (json.loads(out) if out else None)


def test_health_liefert_json_und_richtigen_header():
    status, headers, body = anfrage(erzeuge_app(), "GET", "/health")

    assert (status, body) == (200, {"status": "ok"})
    assert headers["content-type"].startswith("application/json")
    assert headers["content-length"] == str(len(json.dumps(body).encode()))


def test_notizen_anlegen_holen_listen_und_loeschen():
    app = erzeuge_app()

    status, _, angelegt = anfrage(app, "POST", "/notizen", {"titel": "Einkauf", "text": "Milch"})
    assert (status, angelegt) == (201, {"id": 1, "titel": "Einkauf", "text": "Milch"})
    assert anfrage(app, "GET", "/notizen/1")[::2] == (200, angelegt)
    assert anfrage(app, "GET", "/notizen")[::2] == (200, [angelegt])

    status, headers, body = anfrage(app, "DELETE", "/notizen/1")
    assert (status, headers, body) == (204, {"content-length": "0"}, None)
    assert anfrage(app, "GET", "/notizen")[::2] == (200, [])


def test_nicht_ascii_und_getrimmter_titel_kommen_korrekt_zurueck():
    app = erzeuge_app()

    status, _, notiz = anfrage(
        app, "POST", "/notizen", {"titel": "  Gruesse  ", "text": "Schoen \u4f60\u597d"}
    )

    assert (status, notiz) == (201, {"id": 1, "titel": "Gruesse", "text": "Schoen \u4f60\u597d"})
    assert anfrage(app, "GET", "/notizen/1")[2] == notiz


@pytest.mark.parametrize(
    ("methode", "pfad", "status"),
    [
        ("GET", "/gibt-es-nicht", 404),
        ("GET", "/notizen/abc", 404),
        ("GET", "/notizen/" + "9" * 5000, 404),
        ("GET", "/notizen/1/extra", 404),
        ("GET", "/notizen/", 404),
        ("PUT", "/notizen", 405),
        ("POST", "/health", 405),
        ("POST", "/notizen/1", 405),
        ("DELETE", "/health", 405),
    ],
)
def test_unbekannte_pfade_und_falsche_methoden_sind_json_fehler(methode, pfad, status):
    antwort_status, headers, body = anfrage(erzeuge_app(), methode, pfad)

    assert antwort_status == status
    assert headers["content-type"].startswith("application/json")
    assert isinstance(body["fehler"], str) and body["fehler"]


def test_unbekannte_notiz_ist_404_mit_fehlertext():
    app = erzeuge_app()

    for methode in ("GET", "DELETE"):
        status, _, body = anfrage(app, methode, "/notizen/99")
        assert status == 404
        assert isinstance(body["fehler"], str) and body["fehler"]


@pytest.mark.parametrize(
    "roh",
    [
        b"",
        b"kein json",
        b"\xff",
        b"[]",
        b"null",
        b'{"titel": "x"}',
        b'{"text": "t"}',
        b'{"titel": "", "text": "t"}',
        b'{"titel": "x", "text": 5}',
    ],
)
def test_ungueltiger_body_ist_400_und_verbraucht_keine_id(roh):
    app = erzeuge_app()

    status, _, body = anfrage(app, "POST", "/notizen", roh=roh)
    assert status == 400
    assert isinstance(body["fehler"], str) and body["fehler"]
    assert anfrage(app, "POST", "/notizen", {"titel": "ok", "text": ""})[2]["id"] == 1


def test_ungueltige_content_length_ist_400():
    status, _, body = anfrage(
        erzeuge_app(), "POST", "/notizen", roh=b"{}", content_length="keine-zahl"
    )

    assert status == 400
    assert body["fehler"]


def test_uebergebener_speicher_wird_benutzt():
    speicher = NotizSpeicher()
    speicher.anlegen("vorab", "da")

    status, _, body = anfrage(erzeuge_app(speicher), "GET", "/notizen")

    assert (status, [notiz["titel"] for notiz in body]) == (200, ["vorab"])


def test_apps_teilen_ohne_uebergebenen_speicher_keinen_zustand():
    erste_app = erzeuge_app()
    zweite_app = erzeuge_app()

    anfrage(erste_app, "POST", "/notizen", {"titel": "nur erste", "text": ""})

    assert anfrage(zweite_app, "GET", "/notizen")[::2] == (200, [])
