@echo off
REM Projekt- und Pfadkonfiguration (auf deine Angaben zugeschnitten)
SET "PROJECT_DIR=D:\Projekte\python-merge-images-into-pdf"
SET "WATCH_DIR=D:\Projekte\python-merge-images-into-pdf\input"
SET "OUTPUT_DIR=D:\Projekte\python-merge-images-into-pdf\output"

REM Virtuelle Umgebung aktivieren (optional)
IF EXIST "%PROJECT_DIR%\.venv\Scripts\activate.bat" (
    CALL "%PROJECT_DIR%\.venv\Scripts\activate.bat"
)

PUSHD "%PROJECT_DIR%"
echo [%DATE% %TIME%] Starte Merge …
python merge_images_to_pdf.py --watch-dir "%WATCH_DIR%" --output-dir "%OUTPUT_DIR%"  --min-age-seconds 2 --verbose
SET "EXITCODE=%ERRORLEVEL%"
IF NOT "%EXITCODE%"=="0" (
  echo [%DATE% %TIME%] Fehlercode: %EXITCODE%
)
POPD

EXIT /B %EXITCODE%
