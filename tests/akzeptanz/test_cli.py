"""Akzeptanztest (spec-first) fuer projekt.cli: Beispiele aus dem Ziel `notizen-cli`."""

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest

if importlib.util.find_spec("projekt.cli") is None:
    pytest.skip("Modul noch nicht umgesetzt", allow_module_level=True)

from projekt.cli import main  # noqa: E402

import projekt  # noqa: E402


def test_selbsttest_ist_null_und_meldet_ok(capsys):
    assert main(["--selbsttest"]) == 0
    assert "selbsttest ok" in capsys.readouterr().out.lower()


def test_unbekannte_option_ist_zwei_ohne_ausnahme(capsys):
    assert main(["--gibt-es-nicht"]) == 2
    assert capsys.readouterr().err


def test_ungueltiger_port_ist_zwei():
    assert main(["--port", "abc"]) == 2
    assert main(["--port", "70000"]) == 2


def test_als_modul_aufrufbar():
    quelle = str(Path(projekt.__file__).resolve().parent.parent)
    umgebung = {**os.environ, "PYTHONPATH": quelle}
    r = subprocess.run(
        [sys.executable, "-m", "projekt.cli", "--selbsttest"],
        capture_output=True,
        text=True,
        timeout=60,
        env=umgebung,
        check=False,
    )
    assert r.returncode == 0
    assert "selbsttest ok" in r.stdout.lower()
