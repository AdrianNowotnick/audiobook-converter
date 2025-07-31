#!/usr/bin/env python3
import os
import sys
from mutagen.id3 import ID3, TIT2, TALB, TPE1, TPE2, TRCK, APIC, ID3NoHeaderError
from mutagen.mp3 import MP3

AUTHOR = "Unbekannter Autor"
TITLE = "Unbekannter Titel"

def find_cover_file(folder):
    image_files = [f for f in os.listdir(folder)
                   if f.lower().endswith(('.jpg', '.jpeg', '.png')) and not f.startswith('.')]
    if not image_files:
        return None
    elif len(image_files) == 1:
        return os.path.join(folder, image_files[0])
    else:
        return os.path.join(folder, sorted(image_files)[0])  # nimm erste alphabetisch

def set_metadata_for_folder(folder, no_cover_list):
    print(f"\nVerarbeite Ordner: {folder}")

    cover_path = find_cover_file(folder)

    for fn in os.listdir(folder):
        if not fn.lower().endswith(".mp3"):
            continue

        filepath = os.path.join(folder, fn)
        try:
            audio = MP3(filepath, ID3=ID3)
            audio.add_tags()
        except ID3NoHeaderError:
            audio = MP3(filepath)
            audio.add_tags()

        audio.tags["TIT2"] = TIT2(encoding=3, text=TITLE)
        audio.tags["TALB"] = TALB(encoding=3, text=TITLE)
        audio.tags["TPE1"] = TPE1(encoding=3, text=AUTHOR)
        audio.tags["TPE2"] = TPE2(encoding=3, text=AUTHOR)
        audio.tags["TRCK"] = TRCK(encoding=3, text="1")

        if cover_path:
            with open(cover_path, "rb") as img:
                mime = "image/jpeg" if cover_path.lower().endswith((".jpg", ".jpeg")) else "image/png"
                audio.tags["APIC"] = APIC(
                    encoding=3,
                    mime=mime,
                    type=3,
                    desc="Cover",
                    data=img.read()
                )
        else:
            no_cover_list.append(filepath)

        audio.save()
        print(f"Metadaten gesetzt für: {fn}")

def main(root_dir):
    no_cover_files = []
    for root, dirs, files in os.walk(root_dir):
        mp3s = [f for f in files if f.lower().endswith(".mp3")]
        if mp3s:
            set_metadata_for_folder(root, no_cover_files)

    print("\nDateien ohne eingebettetes Cover:")
    if no_cover_files:
        for f in no_cover_files:
            print("  -", f)
    else:
        print("  Alle Dateien haben ein Cover.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Pfad muss als Argument übergeben werden.")
        sys.exit(1)
    path = sys.argv[1]
    if not os.path.isdir(path):
        print("Ungültiger Pfad:", path)
        sys.exit(1)
    main(path)
