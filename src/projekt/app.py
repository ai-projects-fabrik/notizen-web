"""JSON-Webschnittstelle fuer Notizen als WSGI-App ohne Fremdpakete."""

import json
from collections.abc import Callable, Iterable
from typing import Any

from projekt.speicher import NotizSpeicher

_StartResponse = Callable[[str, list[tuple[str, str]]], Any]
_WSGIApp = Callable[[dict[str, Any], _StartResponse], Iterable[bytes]]


def _json_antwort(start_response: _StartResponse, status: str, daten: object) -> Iterable[bytes]:
    """Serialisiert eine JSON-Antwort und setzt die zugehoerigen Header."""
    koerper = json.dumps(daten, ensure_ascii=False).encode("utf-8")
    start_response(
        status,
        [
            ("Content-Type", "application/json; charset=utf-8"),
            ("Content-Length", str(len(koerper))),
        ],
    )
    return [koerper]


def _fehler(start_response: _StartResponse, status: str, text: str) -> Iterable[bytes]:
    """Liefert eine Fehlerantwort im vereinbarten JSON-Format."""
    return _json_antwort(start_response, status, {"fehler": text})


def _lies_json(environ: dict[str, Any]) -> dict[str, object]:
    """Liest und validiert den JSON-Objekt-Body einer Anfrage."""
    laenge_roh = environ.get("CONTENT_LENGTH") or "0"
    try:
        laenge = int(laenge_roh)
    except (TypeError, ValueError) as fehler:
        raise ValueError("Content-Length ist ungueltig") from fehler
    if laenge < 0:
        raise ValueError("Content-Length ist ungueltig")

    try:
        roh = environ["wsgi.input"].read(laenge)
    except (AttributeError, KeyError) as fehler:
        raise ValueError("Anfragebody fehlt") from fehler
    if not roh:
        raise ValueError("JSON-Objekt erwartet")

    try:
        daten = json.loads(roh.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as fehler:
        raise ValueError("Ungueltiges JSON") from fehler
    if not isinstance(daten, dict):
        raise ValueError("JSON-Objekt erwartet")
    return daten


def erzeuge_app(speicher: NotizSpeicher | None = None) -> _WSGIApp:
    """Erzeugt eine WSGI-App; ohne Speicher wird ein eigener leerer angelegt."""
    notiz_speicher = speicher if speicher is not None else NotizSpeicher()

    def app(environ: dict[str, Any], start_response: _StartResponse) -> Iterable[bytes]:
        methode = str(environ.get("REQUEST_METHOD", "")).upper()
        pfad = str(environ.get("PATH_INFO", ""))

        if pfad == "/health":
            if methode != "GET":
                return _fehler(start_response, "405 Method Not Allowed", "Methode nicht erlaubt")
            return _json_antwort(start_response, "200 OK", {"status": "ok"})

        if pfad == "/notizen":
            if methode == "GET":
                return _json_antwort(start_response, "200 OK", notiz_speicher.liste())
            if methode == "POST":
                try:
                    daten = _lies_json(environ)
                    notiz = notiz_speicher.anlegen(daten["titel"], daten["text"])
                except (KeyError, ValueError, TypeError):
                    return _fehler(start_response, "400 Bad Request", "Ungueltige Notizdaten")
                return _json_antwort(start_response, "201 Created", notiz)
            return _fehler(start_response, "405 Method Not Allowed", "Methode nicht erlaubt")

        if pfad.startswith("/notizen/"):
            id_text = pfad.removeprefix("/notizen/")
            if not id_text.isascii() or not id_text.isdecimal():
                return _fehler(start_response, "404 Not Found", "Nicht gefunden")
            if methode not in {"GET", "DELETE"}:
                return _fehler(start_response, "405 Method Not Allowed", "Methode nicht erlaubt")

            try:
                id = int(id_text)
            except ValueError:
                return _fehler(start_response, "404 Not Found", "Nicht gefunden")
            try:
                if methode == "GET":
                    return _json_antwort(start_response, "200 OK", notiz_speicher.holen(id))
                notiz_speicher.loeschen(id)
            except KeyError:
                return _fehler(start_response, "404 Not Found", "Nicht gefunden")

            start_response("204 No Content", [("Content-Length", "0")])
            return []

        return _fehler(start_response, "404 Not Found", "Nicht gefunden")

    return app
