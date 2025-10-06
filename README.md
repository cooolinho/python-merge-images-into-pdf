# Bilder in Ordnern zu PDFs zusammenführen (Windows, mit Archivierung pro Lauf)

Dieses Setup verarbeitet einen Input-Ordner inkl. Unterordnern. Für jeden Ordner, der Bilder enthält, wird eine eigene PDF erzeugt (Reihenfolge nach natürlicher Dateinamenssortierung). Nach erfolgreicher Erstellung werden die verarbeiteten Bilder in einen neuen Zeitstempel-Unterordner im Output verschoben, wobei die Ordnerstruktur beibehalten wird. Der Input-Ordner bleibt somit nach dem Lauf leer (abgesehen von Dateien, die noch zu neu sind).

- Input: `D:\Projekte\python-merge-images-into-pdf\input`
- Output (Basis): `D:\Projekte\python-merge-images-into-pdf\output`
- Pro Lauf: `D:\Projekte\python-merge-images-into-pdf\output\YYYY-MM-DD_HH-MM-SS\...`

Eigenschaften:
- Natürliche Sortierung: `1, 2, 10`
- PNG-Transparenz auf weißem Hintergrund
- Pro Ordner eine PDF (keine Vermischung zwischen unterschiedlichen Ordnern)
- Archivierung aller verarbeiteten Bilder im Zeitstempel-Output-Ordner
- Zu neue Dateien (Standard < 2s seit letzter Änderung) werden übersprungen und im nächsten Lauf verarbeitet

## Voraussetzungen
- Windows 10/11
- Python 3.9+ (über `py`-Launcher)

## Installation
```powershell
cd D:\Projekte\python-merge-images-into-pdf
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Manuell testen
```powershell
py merge_images_to_pdf.py --watch-dir "D:\Projekte\python-merge-images-into-pdf\input" --output-dir "D:\Projekte\python-merge-images-into-pdf\output" --verbose
```

Optionaler Loop (alle 60 Sekunden):
```powershell
py merge_images_to_pdf.py --watch-dir "D:\Projekte\python-merge-images-into-pdf\input" --output-dir "D:\Projekte\python-merge-images-into-pdf\output" --loop --interval 60 --verbose
```

Wichtige Optionen:
- `--min-age-seconds` (Standard 2): Verarbeitet nur Dateien, deren letzte Änderung mindestens X Sekunden her ist (vermeidet halbfertige Kopien).
- `--verbose`: Mehr Logausgabe.

## Automatisierung: Task Scheduler (jede Minute)
Task anlegen (als Administrator in `cmd`):
```bat
SCHTASKS /Create /SC MINUTE /MO 1 /TN "ImageToPDF" /TR "\"D:\Projekte\python-merge-images-into-pdf\windows\run_image_merger.bat\"" /RL HIGHEST
```

Task prüfen/ändern/löschen:
```bat
SCHTASKS /Query /TN "ImageToPDF" /V /FO LIST
SCHTASKS /Change /TN "ImageToPDF" /ENABLE
SCHTASKS /Delete /TN "ImageToPDF" /F
```

## Verhalten bei Unterordnern
- Es wird pro Ordner (einschließlich des Input-Hauptordners) eine eigene PDF erzeugt.
- Dateien werden nicht ordnerübergreifend gemischt.
- Die Ausgabe spiegelt die relative Ordnerstruktur unterhalb des Zeitstempelordners im Output.

## Hinweise
- Wenn einzelne Dateien noch „zu neu“ sind, bleiben sie im Input und werden im nächsten Lauf verarbeitet.
- Leere Unterordner werden nach dem Verschieben gelöscht.
- Dateinamen in der PDF: Seitenreihenfolge entspricht der natürlichen Sortierung nach Dateinamen.
