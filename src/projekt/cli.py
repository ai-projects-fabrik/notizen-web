"""Kommandozeile zum Starten des Notiz-Servers und fuer den Selbsttest."""

from __future__ import annotations

import argparse
import io
import json
import sys
from collections.abc import Callable, Iterable
from typing import Any
from wsgiref.simple_server import make_server
from wsgiref.util import setup_testing_defaults

from projekt.app import erzeuge_app

_StartResponse = Callable[..., Any]
_WSGIApp = Callable[[dict[str, Any], _StartResponse], Iterable[bytes]]


def _port(wert: str) -> int:
    """Wandelt einen Porttext um und prueft den erlaubten Bereich."""
    try:
        port = int(wert)
    except ValueError as fehler:
        raise argparse.ArgumentTypeError("Port muss eine ganze Zahl sein") from fehler
    if not 1 <= port <= 65535:
        raise argparse.ArgumentTypeError("Port muss zwischen 1 und 65535 liegen")
    return port


def _erzeuge_parser() -> argparse.ArgumentParser:
    """Erzeugt den Argumentparser fuer die Kommandozeile."""
    parser = argparse.ArgumentParser(
        prog="projekt.cli",
        description="Startet den Notiz-Server oder fuehrt einen Selbsttest aus.",
        allow_abbrev=False,
    )
    parser.add_argument(
        "--selbsttest",
        action="store_true",
        help="prueft die WSGI-App ohne Netzwerkzugriff",
    )
    parser.add_argument("--host", default="127.0.0.1", help="Bind-Adresse des Servers")
    parser.add_argument(
        "--port",
        type=_port,
        default=8000,
        help="Port des Servers (1 bis 65535)",
    )
    return parser


def _anfrage(
    app: _WSGIApp, methode: str, pfad: str, daten: object | None = None
) -> tuple[int, object | None]:
    """Ruft die WSGI-App direkt mit einer Testanfrage auf."""
    koerper = b"" if daten is None else json.dumps(daten).encode("utf-8")
    environ: dict[str, Any] = {}
    setup_testing_defaults(environ)
    environ.update(
        {
            "REQUEST_METHOD": methode,
            "PATH_INFO": pfad,
            "CONTENT_LENGTH": str(len(koerper)),
            "CONTENT_TYPE": "application/json",
            "wsgi.input": io.BytesIO(koerper),
        }
    )

    antwort: dict[str, int] = {}

    def start_response(status: str, headers: list[tuple[str, str]], exc_info: Any = None) -> None:
        antwort["status"] = int(status.split(" ", 1)[0])

    ausgabe = b"".join(app(environ, start_response))
    return antwort["status"], json.loads(ausgabe) if ausgabe else None


def _pruefe_antwort(antwort: tuple[int, object | None], status: int, koerper: object) -> None:
    """Vergleicht eine WSGI-Antwort mit dem erwarteten Ergebnis."""
    if antwort != (status, koerper):
        raise RuntimeError(f"unerwartete Antwort: {antwort!r}")


def _fuehre_selbsttest() -> None:
    """Prueft alle wesentlichen App-Routen direkt und ohne Netzwerk."""
    app = erzeuge_app()
    _pruefe_antwort(_anfrage(app, "GET", "/health"), 200, {"status": "ok"})

    notiz = {"id": 1, "titel": "Selbsttest", "text": "In-process geprueft"}
    _pruefe_antwort(_anfrage(app, "POST", "/notizen", notiz), 201, notiz)
    _pruefe_antwort(_anfrage(app, "GET", "/notizen/1"), 200, notiz)
    _pruefe_antwort(_anfrage(app, "GET", "/notizen"), 200, [notiz])
    _pruefe_antwort(_anfrage(app, "DELETE", "/notizen/1"), 204, None)
    _pruefe_antwort(_anfrage(app, "GET", "/notizen"), 200, [])


def _starte_server(host: str, port: int) -> int:
    """Startet den WSGI-Server bis zur Unterbrechung."""
    server = make_server(host, port, erzeuge_app())
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


def main(argv: list[str] | None = None) -> int:
    """Fuehrt Selbsttest oder Serverstart aus und liefert den Exitcode."""
    parser = _erzeuge_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as fehler:
        return fehler.code if isinstance(fehler.code, int) else 2

    if args.selbsttest:
        try:
            _fuehre_selbsttest()
        except Exception as fehler:
            print(f"Selbsttest fehlgeschlagen: {fehler}", file=sys.stderr)
            return 1
        print("Selbsttest OK")
        return 0

    return _starte_server(args.host, args.port)


if __name__ == "__main__":
    raise SystemExit(main())
