#!/usr/bin/env python3
import argparse
import os
import sys
import time
import shutil
import tempfile
from pathlib import Path
from typing import List
from datetime import datetime

from PIL import Image
import re

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG"}

def natsort_key(s: str):
    # Natürliche Sortierung: 'file2' < 'file10'
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r"(\d+)", s)]

def is_image_file(p: Path) -> bool:
    return p.is_file() and (p.suffix in IMAGE_EXTS) and (not p.name.startswith("."))

def list_images_in_dir_sorted(dir_path: Path, min_age_seconds: int, now: float, verbose: bool) -> List[Path]:
    images: List[Path] = []
    for entry in dir_path.iterdir():
        if not is_image_file(entry):
            continue
        try:
            st = entry.stat()
        except FileNotFoundError:
            continue
        age = now - st.st_mtime
        if age < min_age_seconds:
            if verbose:
                print(f"Überspringe (zu neu): {entry} (Alter {age:.1f}s < {min_age_seconds}s)")
            continue
        images.append(entry)
    images.sort(key=lambda x: natsort_key(x.name))
    return images

def to_rgb_flatten_white(im: Image.Image) -> Image.Image:
    # Transparenz (RGBA/LA/P mit Transparenz) auf weißem Hintergrund
    if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
        if im.mode == "P":
            im = im.convert("RGBA")
        bg = Image.new("RGB", im.size, (255, 255, 255))
        alpha = im.getchannel("A") if "A" in im.getbands() else None
        if alpha is not None:
            bg.paste(im.convert("RGB"), mask=alpha)
        else:
            bg.paste(im.convert("RGB"))
        return bg
    return im.convert("RGB")

def load_image_rgb(path: Path) -> Image.Image:
    with Image.open(path) as im:
        rgb = to_rgb_flatten_white(im)
        # Kopie zurückgeben, damit keine offenen Handles auf path bleiben
        return rgb.copy()

def ensure_unique_path(dest: Path) -> Path:
    if not dest.exists():
        return dest
    stem = dest.stem
    suffix = dest.suffix
    parent = dest.parent
    i = 1
    while True:
        cand = parent / f"{stem} ({i}){suffix}"
        if not cand.exists():
            return cand
        i += 1

def save_pdf_atomic(image_paths: List[Path], pdf_path: Path, verbose: bool):
    pdf_path.parent.mkdir(parents=True, exist_ok=True)

    rgb_images: List[Image.Image] = []
    for p in image_paths:
        if verbose:
            print(f"Lade: {p}")
        try:
            rgb_images.append(load_image_rgb(p))
        except Exception as e:
            print(f"Warnung: Konnte Bild nicht laden, überspringe {p}: {e}", file=sys.stderr)

    if not rgb_images:
        if verbose:
            print(f"Keine gültigen Bilder in {pdf_path.parent}.")
        return

    # Windows-sicherer Tempfile-Pfad (Handle sofort schließen)
    fd, tmp_name = tempfile.mkstemp(dir=str(pdf_path.parent), suffix=".pdf.tmp")
    os.close(fd)
    tmp_path = Path(tmp_name)

    try:
        if len(rgb_images) == 1:
            rgb_images[0].save(tmp_path, format="PDF")
        else:
            rgb_images[0].save(tmp_path, format="PDF", save_all=True, append_images=rgb_images[1:])
        # Atomar ersetzen
        if pdf_path.exists():
            try:
                pdf_path.unlink()
            except Exception:
                pass
        os.replace(tmp_path, pdf_path)
        if verbose:
            print(f"Geschrieben: {pdf_path}")
    finally:
        if tmp_path.exists():
            try:
                tmp_path.unlink()
            except Exception:
                pass
        for im in rgb_images:
            try:
                im.close()
            except Exception:
                pass

def move_files_to_dir(files: List[Path], dest_dir: Path, verbose: bool):
    dest_dir.mkdir(parents=True, exist_ok=True)
    for src in files:
        dest = dest_dir / src.name
        dest = ensure_unique_path(dest)
        if verbose:
            print(f"Verschiebe: {src} -> {dest}")
        shutil.move(str(src), str(dest))

def remove_empty_dirs(root: Path, verbose: bool):
    # Leere Unterordner entfernen (post-order)
    for dirpath, dirnames, filenames in os.walk(root, topdown=False):
        p = Path(dirpath)
        if p == root:
            continue
        try:
            next(p.iterdir())
            # Nicht leer
        except StopIteration:
            try:
                p.rmdir()
                if verbose:
                    print(f"Entferne leeren Ordner: {p}")
            except Exception:
                pass

def make_pdf_filename_from_dir(dir_path: Path) -> str:
    # Benennt die PDF nach dem Quellordner; ungültige Windows-Zeichen werden ersetzt
    name = dir_path.name.strip().strip(". ")
    # Ersetze unzulässige Zeichen: <>:"/\|?*
    safe = re.sub(r'[<>:"/\\|?*]', "_", name)
    # Leere Namen auffangen
    if not safe:
        safe = "merged"
    return f"{safe}.pdf"

def process_once(watch_dir: Path, output_dir: Path, min_age_seconds: int, verbose: bool) -> bool:
    now = time.time()
    # Erzeuge Zeitstempel-Ordner für diesen Lauf
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    run_root = output_dir / ts

    processed_any = False

    # Alle Ordner durchsuchen, beginnend mit watch_dir
    for dirpath, dirnames, filenames in os.walk(watch_dir):
        src_dir = Path(dirpath)
        # Bilder in diesem Ordner ermitteln
        images = list_images_in_dir_sorted(src_dir, min_age_seconds, now, verbose)
        if not images:
            continue

        rel = src_dir.relative_to(watch_dir)
        dest_dir = run_root / rel
        pdf_filename = make_pdf_filename_from_dir(src_dir)
        pdf_path = dest_dir / pdf_filename

        if verbose:
            print(f"Verarbeite Ordner: {src_dir} -> {pdf_path}")

        # PDF schreiben
        save_pdf_atomic(images, pdf_path, verbose)
        # Bilder verschieben
        move_files_to_dir(images, dest_dir, verbose)
        processed_any = True

    # Leere Ordner aus dem Input entfernen
    remove_empty_dirs(watch_dir, verbose)

    if not processed_any and verbose:
        print("Keine verarbeitbaren Bilder gefunden.")
    return processed_any

def main():
    parser = argparse.ArgumentParser(
        description="Fügt Bilder je Ordner (inkl. Unterordner) zu PDFs zusammen und verschiebt verarbeitete Bilder in einen Zeitstempel-Output."
    )
    parser.add_argument("--watch-dir", required=True, help="Input-Ordner mit Bildern (JPG/PNG). Unterordner werden separat verarbeitet.")
    parser.add_argument("--output-dir", required=True, help="Basis-Output-Ordner. Pro Lauf wird ein Zeitstempel-Unterordner erstellt.")
    parser.add_argument("--min-age-seconds", type=int, default=2, help="Mindestalter der Dateien in Sekunden (vermeidet halbfertige Kopien).")
    parser.add_argument("--loop", action="store_true", help="Endlosschleife (z. B. für minütliche Ausführung).")
    parser.add_argument("--interval", type=int, default=60, help="Intervall in Sekunden im Loop-Modus.")
    parser.add_argument("--verbose", action="store_true", help="Ausführliche Ausgaben.")
    args = parser.parse_args()

    watch_dir = Path(args.watch_dir).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()

    if not watch_dir.exists() or not watch_dir.is_dir():
        print(f"Fehler: Input-Ordner existiert nicht: {watch_dir}", file=sys.stderr)
        sys.exit(1)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.loop:
        if args.verbose:
            print(f"Starte Loop. Beobachte: {watch_dir} -> {output_dir} alle {args.interval}s")
        while True:
            try:
                process_once(watch_dir, output_dir, args.min_age_seconds, args.verbose)
            except Exception as e:
                print(f"Fehler in process_once: {e}", file=sys.stderr)
            time.sleep(args.interval)
    else:
        processed = process_once(watch_dir, output_dir, args.min_age_seconds, args.verbose)
        if args.verbose and not processed:
            print("Fertig (nichts verarbeitet).")

if __name__ == "__main__":
    main()
