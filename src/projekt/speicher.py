"""In-Memory-Speicher fuer Notizen."""


class NotizSpeicher:
    """Verwaltet Notizen im Arbeitsspeicher."""

    def __init__(self) -> None:
        """Erzeugt einen leeren Speicher mit fortlaufenden IDs ab 1."""
        self._notizen: dict[int, dict] = {}
        self._naechste_id = 1

    def anlegen(self, titel: str, text: str) -> dict:
        """Legt eine Notiz an und gibt eine Kopie davon zurueck."""
        if not isinstance(titel, str) or not isinstance(text, str):
            raise ValueError("titel und text muessen Zeichenketten sein")

        titel = titel.strip()
        if not 1 <= len(titel) <= 80:
            raise ValueError("titel muss nach dem Trimmen 1 bis 80 Zeichen lang sein")
        if len(text) > 2000:
            raise ValueError("text darf hoechstens 2000 Zeichen lang sein")

        notiz = {"id": self._naechste_id, "titel": titel, "text": text}
        self._notizen[self._naechste_id] = notiz
        self._naechste_id += 1
        return notiz.copy()

    def holen(self, id: int) -> dict:
        """Gibt eine Kopie der Notiz mit der angegebenen ID zurueck."""
        return self._notizen[id].copy()

    def liste(self) -> list[dict]:
        """Gibt Kopien aller Notizen in der Reihenfolge ihrer IDs zurueck."""
        return [notiz.copy() for notiz in self._notizen.values()]

    def loeschen(self, id: int) -> None:
        """Loescht die Notiz mit der angegebenen ID."""
        del self._notizen[id]
