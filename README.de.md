<h1 align="center">📄 Merge Images Into PDF</h1>

<p align="center">
  <em>Überwacht einen Ordner, macht aus jedem Unterordner voller Bilder eine eigene PDF und archiviert die Originale in einem Zeitstempel-Ordner.</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Pillow-4A5568?style=for-the-badge" alt="Pillow">
  <img src="https://img.shields.io/badge/Windows-0078D4?style=for-the-badge&logo=windows&logoColor=white" alt="Windows">
</p>

<p align="center">
  <a href="README.md">🇬🇧 English version</a>
</p>

---

## 📖 Über das Projekt

Ein Scan-und-Ablage-Workflow für Papier. Du legst Bilder in einen Input-Ordner —
ein Unterordner pro Dokument — und jeder Ordner wird zu einer eigenen PDF, die
Seiten in natürlicher Reihenfolge.

Der Clou: Der Input-Ordner bleibt leer zurück. Sobald eine PDF geschrieben ist,
wandern die Quellbilder in einen Zeitstempel-Ordner im Output und behalten dabei
ihre Struktur. Lässt du das Ganze regelmäßig laufen, wird Scannen zur
Nebensache: Dateien rein, PDFs raus, nichts wird doppelt verarbeitet.

Dateien, die gerade noch geschrieben werden, überspringt das Skript. Eine Datei
muss ein paar Sekunden unverändert sein, bevor sie verarbeitet wird — ein halb
kopierter Scan landet also nie in einer PDF.

## 🛠️ Tech-Stack

| Technologie | Version | Zweck |
|-------------|---------|-------|
| <img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"> Python | 3.9+ | Laufzeitumgebung |
| Pillow | 10.0+ | Bilder laden und PDF erzeugen |

## ✨ Funktionen

- **Eine PDF pro Ordner** — Bilder aus verschiedenen Ordnern werden nie vermischt
- **Natürliche Sortierung** — `1, 2, 10` statt `1, 10, 2`
- **Transparenz wird aufgelöst** — PNGs werden auf Weiß gelegt, statt schwarz zu werden
- **Zeitstempel-Archiv** — verarbeitete Bilder wandern nach `output/YYYY-MM-DD_HH-MM-SS/`, Struktur bleibt erhalten
- **Sicher gegen halbe Kopien** — Dateien jünger als `--min-age-seconds` warten auf den nächsten Lauf
- **Atomares Schreiben** — die PDF wird erst temporär geschrieben und dann verschoben; ein abgebrochener Lauf hinterlässt keine kaputte Datei
- **Loop-Modus** — einmalig ausführen oder in einem Intervall pollen

Unterstützte Eingabeformate: `.jpg`, `.jpeg`, `.png`.

## 🚀 Erste Schritte

### Voraussetzungen

- Python 3.9 oder neuer
- Windows 10/11 für die Aufgabenplanung; das Skript selbst läuft überall

### Installation

```powershell
git clone https://github.com/cooolinho/python-merge-images-into-pdf.git
cd python-merge-images-into-pdf

py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Unter Linux und macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 📋 Verwendung

### Einzelner Lauf

```powershell
py merge_images_to_pdf.py --watch-dir ".\input" --output-dir ".\output" --verbose
```

### Dauerbetrieb, alle 60 Sekunden

```powershell
py merge_images_to_pdf.py --watch-dir ".\input" --output-dir ".\output" --loop --interval 60 --verbose
```

### Parameter

| Argument | Beschreibung | Standard |
|----------|--------------|----------|
| `--watch-dir` | Input-Ordner. Unterordner werden separat verarbeitet | **erforderlich** |
| `--output-dir` | Basis-Output-Ordner. Pro Lauf entsteht ein Zeitstempel-Unterordner | **erforderlich** |
| `--min-age-seconds` | Mindestalter einer Datei, bevor sie verarbeitet wird | `2` |
| `--loop` | Weiterlaufen statt nach einem Durchgang zu beenden | aus |
| `--interval` | Sekunden zwischen den Durchgängen im Loop-Modus | `60` |
| `--verbose` | Ausführliche Logausgabe | aus |

### Wie Ordner behandelt werden

```
input/
├── rechnung-maerz/      → rechnung-maerz.pdf
│   ├── 1.jpg
│   └── 2.jpg
└── vertrag/             → vertrag.pdf
    └── seite1.png
```

Nach einem erfolgreichen Lauf ist `input/` leer und die Bilder liegen unter
`output/2026-09-06_14-30-00/` in ihrer ursprünglichen Struktur. Leere Unterordner
werden gelöscht.

## ⏱️ Automatisierung unter Windows

Minütlicher Lauf über die Aufgabenplanung. In einer `cmd` **als Administrator**:

```bat
SCHTASKS /Create /SC MINUTE /MO 1 /TN "ImageToPDF" ^
  /TR "\"C:\pfad\zu\python-merge-images-into-pdf\windows\run_image_merger.bat\"" /RL HIGHEST
```

Aufgabe prüfen, deaktivieren oder löschen:

```bat
SCHTASKS /Query  /TN "ImageToPDF" /V /FO LIST
SCHTASKS /Change /TN "ImageToPDF" /ENABLE
SCHTASKS /Delete /TN "ImageToPDF" /F
```

Passe die Pfade in [`windows/run_image_merger.bat`](windows/run_image_merger.bat)
an deine Installation an.

## 📁 Projektstruktur

```
python-merge-images-into-pdf/
├── merge_images_to_pdf.py     # Das Tool
├── requirements.txt           # Pillow
├── windows/
│   └── run_image_merger.bat   # Wrapper für die Aufgabenplanung
├── input/                     # Hier kommen die Bilder hinein
└── output/                    # PDFs und Zeitstempel-Archive
```

## 📄 Lizenz

Veröffentlicht unter der [MIT-Lizenz](LICENSE).
