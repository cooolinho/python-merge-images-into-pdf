<h1 align="center">📄 Merge Images Into PDF</h1>

<p align="center">
  <em>Watches a folder, turns each subfolder of images into its own PDF, and archives the originals into a timestamped run folder.</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Pillow-4A5568?style=for-the-badge" alt="Pillow">
  <img src="https://img.shields.io/badge/Windows-0078D4?style=for-the-badge&logo=windows&logoColor=white" alt="Windows">
</p>

<p align="center">
  <a href="README.de.md">🇩🇪 Deutsche Version</a>
</p>

---

## 📖 About

A scan-and-file workflow for paper. Drop images into an input folder — one
subfolder per document — and every folder becomes its own PDF, pages ordered
naturally.

The point is that it leaves the input folder empty. Once a PDF is written, the
source images are moved into a timestamped folder under the output directory,
keeping their structure. Run it on a schedule and scanning becomes fire and
forget: drop files in, PDFs come out, nothing is processed twice.

Files still being written are skipped. A file has to be untouched for a couple of
seconds before it is picked up, so a half-copied scan never lands in a PDF.

## 🛠️ Tech Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| <img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"> Python | 3.9+ | Runtime |
| Pillow | 10.0+ | Image loading and PDF generation |

## ✨ Features

- **One PDF per folder** — images from different folders are never mixed
- **Natural sorting** — `1, 2, 10`, not `1, 10, 2`
- **Transparency flattened** — PNGs are composited onto white instead of turning black
- **Timestamped archive** — processed images move to `output/YYYY-MM-DD_HH-MM-SS/`, structure preserved
- **Safe against partial copies** — files younger than `--min-age-seconds` wait for the next run
- **Atomic writes** — the PDF is written to a temporary file and moved into place, so an interrupted run leaves no corrupt output
- **Loop mode** — run once, or poll on an interval

Supported input: `.jpg`, `.jpeg`, `.png`.

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or newer
- Windows 10/11 for the scheduled-task setup; the script itself runs anywhere

### Installation

```powershell
git clone https://github.com/cooolinho/python-merge-images-into-pdf.git
cd python-merge-images-into-pdf

py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

On Linux and macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 📋 Usage

### Single run

```powershell
py merge_images_to_pdf.py --watch-dir ".\input" --output-dir ".\output" --verbose
```

### Continuous, every 60 seconds

```powershell
py merge_images_to_pdf.py --watch-dir ".\input" --output-dir ".\output" --loop --interval 60 --verbose
```

### Parameters

| Argument | Description | Default |
|----------|-------------|---------|
| `--watch-dir` | Input folder. Subfolders are processed separately | **required** |
| `--output-dir` | Base output folder. Each run creates a timestamped subfolder | **required** |
| `--min-age-seconds` | Minimum age of a file before it is processed | `2` |
| `--loop` | Keep running instead of exiting after one pass | off |
| `--interval` | Seconds between passes in loop mode | `60` |
| `--verbose` | Detailed logging | off |

### How folders are handled

```
input/
├── invoice-march/       → invoice-march.pdf
│   ├── 1.jpg
│   └── 2.jpg
└── contract/            → contract.pdf
    └── page1.png
```

After a successful run, `input/` is empty and the images live under
`output/2026-09-06_14-30-00/`, mirroring their original structure. Empty
subfolders are removed.

## ⏱️ Scheduling on Windows

Run every minute via Task Scheduler. In an **administrator** `cmd`:

```bat
SCHTASKS /Create /SC MINUTE /MO 1 /TN "ImageToPDF" ^
  /TR "\"C:\path\to\python-merge-images-into-pdf\windows\run_image_merger.bat\"" /RL HIGHEST
```

Inspect, disable or remove the task:

```bat
SCHTASKS /Query  /TN "ImageToPDF" /V /FO LIST
SCHTASKS /Change /TN "ImageToPDF" /ENABLE
SCHTASKS /Delete /TN "ImageToPDF" /F
```

Adjust the paths inside [`windows/run_image_merger.bat`](windows/run_image_merger.bat)
to match your installation.

## 📁 Project Structure

```
python-merge-images-into-pdf/
├── merge_images_to_pdf.py     # The tool
├── requirements.txt           # Pillow
├── windows/
│   └── run_image_merger.bat   # Wrapper for Task Scheduler
├── input/                     # Drop images here
└── output/                    # PDFs and timestamped archives
```

## 📄 License

Released under the [MIT License](LICENSE).
