import os
import subprocess
import sys

def concat_audio_files(root_folder):
    for dirpath, dirnames, filenames in os.walk(root_folder):
        dirnames.sort(key=str.lower)  # Sortiere Unterordner alphabetisch
        filenames.sort(key=str.lower)  # Sortiere Dateien alphabetisch

        audio_files = [
            f for f in filenames
            if f.lower().endswith((".mp3", ".m4a", ".flac")) and not f.startswith((".", "._"))
        ]

        if len(audio_files) < 2:
            continue

        list_path = os.path.join(dirpath, "concat_list.txt")
        with open(list_path, "w") as f:
            for file in audio_files:
                file_path = os.path.join(dirpath, file).replace("'", "'\\''")
                f.write(f"file '{file_path}'\n")

        folder_name = os.path.basename(os.path.normpath(dirpath))
        output_ext = os.path.splitext(audio_files[0])[1].lower()
        output_file = os.path.join(dirpath, f"{folder_name}{output_ext}")
        audio_files = [f for f in audio_files if f != os.path.basename(output_file)]

        print(f"Concatenating {folder_name}")

        cmd = [
            "ffmpeg",
            "-f", "concat",
            "-safe", "0",
            "-i", list_path,
            "-c", "copy",
            output_file
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        os.remove(list_path)

        for file in audio_files:
            file_path = os.path.join(dirpath, file)
            os.remove(file_path)
        print(f"Deleting      {folder_name}")
        print(" ")

        for file in filenames:
            if file.endswith((".ini", ".m3u", ".ico", ".txt", ".url")):
                try:
                    os.remove(os.path.join(dirpath, file))
                except FileNotFoundError:
                    pass

if __name__ == "__main__":
    input_path = sys.argv[1]
    concat_audio_files(input_path)
