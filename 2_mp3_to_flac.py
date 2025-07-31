#!/usr/bin/env python3
import os, sys, subprocess, re
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn, TimeRemainingColumn

# === Feste Pfade auf Synology ===
FFPROBE_PATH = "/volume1/@appstore/ffmpeg/bin/ffprobe"
FFMPEG_PATH = "/volume1/@appstore/ffmpeg/bin/ffmpeg"

def count_files(path):
    return sum(
        1 for root, _, files in os.walk(path)
        for fn in files
        if fn.lower().endswith((".mp3", ".m4a")) and not fn.startswith((".", "._"))
    )

def get_duration(path):
    try:
        out = subprocess.check_output([
            FFPROBE_PATH, "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", path
        ], text=True).strip()
        return float(out)
    except Exception:
        return -1

def parse_time(ts):
    h, m, s = ts.split(':')
    return int(h)*3600 + int(m)*60 + float(s)

def convert_to_flac(input_path):
    console = Console(force_terminal=True)
    total = count_files(input_path)
    done = 0
    time_pattern = re.compile(r"time=(\d+:\d+:\d+\.\d+)")

    for root, dirs, files in os.walk(input_path):
        dirs.sort(key=str.lower)
        files.sort(key=str.lower)
        for fn in files:
            if not fn.lower().endswith((".mp3", ".m4a")):
                continue
            src = os.path.join(root, fn)
            dst = os.path.splitext(src)[0] + ".flac"

            src_duration = get_duration(src)
            if src_duration <= 0:
                console.print(f"[red]Fehler beim Ermitteln der Quell-Länge für:[/red] {src}")
                continue

            console.print(f"\n[blue]{fn}[/blue]")
            console.print(f"Konvertiere Datei {done + 1} von {total} nach .flac              [yellow]Elapsed:[/yellow]     [cyan]Remaining:[/cyan]")

            with Progress(
                BarColumn(bar_width=None),
                TextColumn("{task.percentage:>6.2f}%     "),
                TimeElapsedColumn(),
                TextColumn("     "),
                TimeRemainingColumn(),
                TextColumn("    "),
                console=console,
                transient=True
            ) as progress:
                task = progress.add_task("", fn=fn, total=src_duration)

                cmd = [
                    FFMPEG_PATH, "-threads", "1", "-i", str(src),
                    "-map", "0:a", "-c:a", "flac",
                    "-map_metadata", "0", "-y", str(dst)
                ]

                retcode = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode


            if retcode != 0:
                console.print(f"[red]Fehler bei der Konvertierung von:[/red] {src} (Exit-Code {retcode})")
                with open("conversion_errors.log", "a") as log:
                    log.write(f"{src} failed with code {retcode}\n")
                continue

            flac_duration = get_duration(dst)
            if flac_duration <= 0:
                console.print(f"[red]Fehler beim Ermitteln der Zieldauer für:[/red] {dst}")
                continue

            if abs(flac_duration - src_duration) <= 1.0:
                os.remove(src)
                console.print(f"[green]Erfolgreich konvertiert und Original gelöscht:[/green] {fn}")
            else:
                console.print(f"[yellow]Warnung: Zieldatei ist zu kurz → Original nicht gelöscht:[/yellow] {fn}")
                with open("conversion_errors.log", "a") as log:
                    log.write(f"{src} → {dst} duration mismatch: src={src_duration:.2f}, dst={flac_duration:.2f}\n")

            done += 1
            if done == total:
                console.print(f"[bold green]Alle Dateien erfolgreich durchlaufen.[/bold green]\n\n")

if __name__ == "__main__":
    if len(sys.argv) == 2:
        convert_to_flac(sys.argv[1])
    else:
        print("Kein Pfad übergeben – benutze aktuellen Ordner.\n")
        convert_to_flac(os.getcwd())
