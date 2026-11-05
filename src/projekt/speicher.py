"""In-Memory-Speicher fuer Notizen."""


class NotizSpeicher:
    """Verwaltet Notizen im Arbeitsspeicher."""

    def __init__(self) -> None:
        """Erzeugt einen leeren Speicher."""
        self._notizen: dict[int, dict] = {}
        self._naechste_id = 1

    def anlegen(self, titel: str, text: str) -> dict:
        """Legt eine Notiz an und gibt eine Kopie davon zurueck."""
        if not isinstance(titel, str) or not isinstance(text, str):
            raise ValueError("Titel und Text muessen Zeichenketten sein")

        titel = titel.strip()
        if not 1 <= len(titel) <= 80:
            raise ValueError("Titel muss nach dem Trimmen 1 bis 80 Zeichen lang sein")
        if not 0 <= len(text) <= 2000:
            raise ValueError("Text darf hoechstens 2000 Zeichen lang sein")

        notiz = {"id": self._naechste_id, "titel": titel, "text": text}
        self._notizen[notiz["id"]] = notiz
        self._naechste_id += 1
        return dict(notiz)

    def holen(self, id: int) -> dict:
        """Gibt eine Kopie der Notiz mit der angegebenen Id zurueck."""
        return dict(self._notizen[id])

    def liste(self) -> list[dict]:
        """Gibt Kopien aller Notizen in aufsteigender Id-Reihenfolge zurueck."""
        return [dict(self._notizen[notiz_id]) for notiz_id in sorted(self._notizen)]

    def loeschen(self, id: int) -> None:
        """Loescht die Notiz mit der angegebenen Id."""
        del self._notizen[id]
