"""Akzeptanztest (spec-first) fuer projekt.app: Beispiele aus dem Ziel `notizen-app`."""

import importlib.util
import io
import json
from wsgiref.util import setup_testing_defaults

import pytest

if importlib.util.find_spec("projekt.app") is None:
    pytest.skip("Modul noch nicht umgesetzt", allow_module_level=True)

from projekt.app import erzeuge_app  # noqa: E402
from projekt.speicher import NotizSpeicher  # noqa: E402


def anfrage(app, methode, pfad, daten=None, roh=None):
    body = roh if roh is not None else (json.dumps(daten).encode() if daten is not None else b"")
    env = {}
    setup_testing_defaults(env)
    env.update(
        REQUEST_METHOD=methode,
        PATH_INFO=pfad,
        CONTENT_LENGTH=str(len(body)),
        CONTENT_TYPE="application/json",
    )
    env["wsgi.input"] = io.BytesIO(body)
    kopf = {}

    def start(status, headers, exc_info=None):
        kopf["status"] = int(status.split()[0])
        kopf["headers"] = {k.lower(): v for k, v in headers}

    out = b"".join(app(env, start))
    return kopf["status"], kopf["headers"], (json.loads(out) if out else None)


def test_health():
    status, headers, body = anfrage(erzeuge_app(), "GET", "/health")
    assert (status, body) == (200, {"status": "ok"})
    assert headers["content-type"].startswith("application/json")


def test_anlegen_holen_liste_loeschen():
    app = erzeuge_app()
    status, _, body = anfrage(app, "POST", "/notizen", {"titel": "Einkauf", "text": "Milch"})
    assert (status, body) == (201, {"id": 1, "titel": "Einkauf", "text": "Milch"})
    assert anfrage(app, "GET", "/notizen/1")[::2] == (200, body)
    assert anfrage(app, "GET", "/notizen")[::2] == (200, [body])
    assert anfrage(app, "DELETE", "/notizen/1")[::2] == (204, None)
    assert anfrage(app, "GET", "/notizen")[::2] == (200, [])


def test_unbekannte_notiz_ist_404_mit_fehlertext():
    app = erzeuge_app()
    for methode in ("GET", "DELETE"):
        status, _, body = anfrage(app, methode, "/notizen/9")
        assert status == 404
        assert isinstance(body["fehler"], str) and body["fehler"]


@pytest.mark.parametrize(
    "roh",
    [
        b"",
        b"kein json",
        b"[]",
        b'{"titel": "x"}',
        b'{"titel": "", "text": "t"}',
        b'{"titel": 1, "text": "t"}',
    ],
)
def test_ungueltiger_body_ist_400(roh):
    status, _, body = anfrage(erzeuge_app(), "POST", "/notizen", roh=roh)
    assert status == 400
    assert body["fehler"]


def test_unbekannter_pfad_404_falsche_methode_405():
    app = erzeuge_app()
    assert anfrage(app, "GET", "/gibt-es-nicht")[0] == 404
    assert anfrage(app, "GET", "/notizen/abc")[0] == 404
    assert anfrage(app, "PUT", "/notizen")[0] == 405
    assert anfrage(app, "POST", "/health")[0] == 405


def test_uebergebener_speicher_wird_benutzt():
    speicher = NotizSpeicher()
    speicher.anlegen("vorab", "da")
    status, _, body = anfrage(erzeuge_app(speicher), "GET", "/notizen")
    assert (status, [n["titel"] for n in body]) == (200, ["vorab"])


def test_zwei_apps_teilen_keinen_zustand():
    a, b = erzeuge_app(), erzeuge_app()
    anfrage(a, "POST", "/notizen", {"titel": "nur a", "text": ""})
    assert anfrage(b, "GET", "/notizen")[::2] == (200, [])
