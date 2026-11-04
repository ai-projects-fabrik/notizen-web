# AGENTS.md - Regeln fuer jeden Coding-Agenten in diesem Repo

Diese Datei gilt unabhaengig vom Agenten (Codex, Claude Code oder andere) und vom Modell.

## Projekt

Kleine JSON-Webschnittstelle fuer Notizen (WSGI, nur Standardbibliothek), Pilot der Projektfabrik.

- Code: `src/projekt/`
- Tests: `tests/` (pytest)
- Python 3.12, keine Laufzeit-Abhaengigkeiten
- Datenklasse: oeffentlich-tauglich

## Fachregeln

- Nur Standardbibliothek; kein Netzwerkzugriff in Tests (WSGI-Callable direkt aufrufen).
- Fehler immer als JSON `{"fehler": "<Text>"}` mit dem im Modulvertrag genannten Statuscode.
- Aus anderen Modulen des Projekts nur oeffentliche Namen importieren (ohne fuehrenden
  Unterstrich). Fehlt etwas, die Funktion im eigenen Modul oeffentlich machen, wenn das Issue
  dieses Modul zustaendig macht, sonst die Luecke im Pull-Request-Text nennen.
- Jede oeffentliche Funktion hat Typangaben und einen Docstring.

## Modulvertrag (bei mehreren Aufgaben ausfuellen)

Wenn mehrere Issues parallel laufen sollen, legt diese Tabelle vorab fest, welches Modul welche
Namen mit welcher Signatur bereitstellt. Abhaengige Module nutzen nur diese Namen. Loeschen, wenn
das Projekt nur aus einer Aufgabe besteht.

| Modul | Funktionen | Hinweis |
|---|---|---|
| `speicher.py` | `NotizSpeicher.anlegen(titel: str, text: str) -> dict`, `.holen(id: int) -> dict`, `.liste() -> list[dict]`, `.loeschen(id: int) -> None` | `ValueError` bei ungueltiger Eingabe, `KeyError` bei unbekannter Id |
| `app.py` | `erzeuge_app(speicher: NotizSpeicher \| None = None)` | WSGI-Callable, Routen laut Akzeptanztest |
| `cli.py` | `main(argv: list[str] \| None = None) -> int` | `--selbsttest`, `--host`, `--port`; Rueckgabe 0, 1 oder 2 |

## Arbeitsablauf

1. Aufgabe aus dem Issue lesen. Unklarheit nicht raten: Annahme im Pull-Request-Text nennen.
   Weicht deine Umsetzung von einer Acceptance Criterion des Issues ab (oder laesst du eine aus,
   oder gewinnt eine Regel aus dieser Datei gegen das Issue), schreibe im Pull-Request-Text eine
   eigene Zeile `ABWEICHUNG: <was und warum>`. Ein solcher Pull Request wird nicht automatisch
   gemergt, sondern von einem Menschen geprueft.
2. Nur `src/` und `tests/` aendern. README nur, wenn die Aufgabe es verlangt.
3. Fuer jede neue Funktion Tests schreiben, inklusive Grenzfaelle aus dem Issue.
4. Vor dem Abschluss alle drei Pruefungen ausfuehren und gruen machen:
   - `ruff check .`
   - `ruff format --check .` (bei Bedarf vorher `ruff format .`)
   - `pytest`
5. Bleibt eine Pruefung nach drei Korrekturrunden rot: aufhoeren und den Fehler im
   Pull-Request-Text offen beschreiben, nicht Tests abschwaechen oder loeschen.

## Akzeptanztests und Widersprueche

- Akzeptanztests in `tests/akzeptanz/` definieren das fachliche Soll. Widerspricht einer davon einer
  Regel in dieser Datei oder dem Issue, **klaert ein Mensch den Widerspruch vor dem Bau** (Spec oder
  diese Datei per Pull Request anpassen). Das Label `agent` kommt erst danach.
- Stoesst der Agent trotzdem auf einen Widerspruch, baut er nach dem Akzeptanztest und meldet den
  Widerspruch im Pull-Request-Text mit `ABWEICHUNG: <was und warum>`. Diese Meldung wird nie
  weggelassen oder abgeschwaecht; der Pull Request braucht dann einen Menschen.

## Verboten

- Aenderungen an `.github/`, `AGENTS.md`, `pyproject.toml` oder `requirements-dev.txt`.
- Aenderungen an `tests/akzeptanz/`: diese Akzeptanztests gibt ein Mensch vorab vor. Die
  Implementierung muss sie erfuellen; schlagen sie fehl, die Implementierung anpassen oder nach
  drei Runden offen melden.
- Tests loeschen, ueberspringen oder Erwartungen aufweichen, damit sie gruen werden.
- Neue Abhaengigkeiten, Netzwerkzugriffe, Secrets oder Zugangsdaten im Code.
- Personen- oder Kundendaten, ausser die Datenklasse oben erlaubt sie ausdruecklich.
