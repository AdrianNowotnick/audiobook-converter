# Audiobook Converter Web-GUI

Python-basiertes Webinterface zur Audiokonvertierung (MP3 ↔ FLAC) mit Metadaten, Fortschrittsanzeige und FFmpeg-Automatisierung.

## Features
- Konvertierung von Hörbüchern (MP3 → FLAC → MP3)
- Cover-Erkennung & Metadaten
- Fortschrittsbalken (pro Datei und gesamt)
- Web-GUI mit Start/Pause-Button
- Fehlerprotokollierung (Log)

## Installation
```bash
git clone https://github.com/AdrianNowotnick/audiobook-converter.git
cd audiobook-converter
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py

