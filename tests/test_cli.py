import pytest

import projekt.cli as cli


def test_selbsttest_meldet_ok_und_gibt_null_zurueck(capsys):
    assert cli.main(["--selbsttest"]) == 0
    assert capsys.readouterr().out.strip() == "Selbsttest OK"


@pytest.mark.parametrize(
    "argv",
    [
        ["--gibt-es-nicht"],
        ["--host"],
        ["--port", "abc"],
        ["--port", "0"],
        ["--port", "65536"],
        ["--port", "1.5"],
    ],
)
def test_ungueltiger_aufruf_ist_zwei_mit_meldung(argv, capsys):
    assert cli.main(argv) == 2
    assert capsys.readouterr().err


def test_hilfe_ist_null(capsys):
    assert cli.main(["--help"]) == 0
    assert "usage" in capsys.readouterr().out.lower()


def test_selbsttest_fehler_ist_eins(monkeypatch, capsys):
    def kaputte_app():
        raise RuntimeError("App nicht verfuegbar")

    monkeypatch.setattr(cli, "erzeuge_app", kaputte_app)

    assert cli.main(["--selbsttest"]) == 1
    assert "Selbsttest fehlgeschlagen" in capsys.readouterr().err


class _FakeServer:
    def __init__(self):
        self.gestartet = False
        self.geschlossen = False

    def serve_forever(self):
        self.gestartet = True

    def server_close(self):
        self.geschlossen = True


@pytest.mark.parametrize(
    ("argv", "host", "port"),
    [
        ([], "127.0.0.1", 8000),
        (["--host", "0.0.0.0", "--port", "8081"], "0.0.0.0", 8081),
    ],
)
def test_serverstart_verwendet_host_und_port(monkeypatch, argv, host, port):
    server = _FakeServer()
    aufrufe = []

    def fake_make_server(bind_host, bind_port, app):
        aufrufe.append((bind_host, bind_port, app))
        return server

    monkeypatch.setattr(cli, "make_server", fake_make_server)

    assert cli.main(argv) == 0
    assert len(aufrufe) == 1
    assert aufrufe[0][:2] == (host, port)
    assert callable(aufrufe[0][2])
    assert server.gestartet
    assert server.geschlossen
