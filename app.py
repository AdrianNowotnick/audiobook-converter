from flask import Flask, render_template, request, jsonify
import os
import subprocess
import threading

app = Flask(__name__)

script_sequence = [
    ("concat", "1_concat.py"),
    ("mp3_to_flac", "2_mp3_to_flac.py"),
    ("flac_to_mp3", "3_flac_to_mp3.py"),
    ("set_metadata", "4_set_metadata.py")
]

process_log = []
process_lock = threading.Lock()

# Blockierende Skriptausführung
def run_script(tag, script_path, folder):
    try:
        process_log.append(f"[{tag}] Starte für {os.path.basename(folder)} ...")
        result = subprocess.run(["python3", script_path, folder], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        if result.returncode == 0:
            process_log.append(f"[{tag}:{os.path.basename(folder)}] abgeschlossen.")
        else:
            process_log.append(f"[ERROR] [{tag}:{os.path.basename(folder)}] Fehler (Exit {result.returncode})")
    except Exception as e:
        process_log.append(f"[ERROR] [{tag}:{os.path.basename(folder)}] Exception: {e}")

# Verarbeitung: alle Tasks → für alle Unterordner
def run_all(input_path, tasks_to_run):
    with process_lock:
        try:
            subdirs = sorted([
                os.path.join(input_path, name)
                for name in os.listdir(input_path)
                if os.path.isdir(os.path.join(input_path, name)) and not name.startswith('@')
            ])
            for tag, script in script_sequence:
                if tag not in tasks_to_run:
                    continue
                for folder in subdirs:
                    run_script(tag, script, folder)
        except Exception as e:
            process_log.append(f"[ERROR] global: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start_process():
    if process_lock.locked():
        return jsonify({"status": "busy", "message": "Ein Prozess läuft bereits."})

    data = request.get_json()
    input_path = data.get('input_path')
    tasks = data.get('tasks', [])

    process_log.clear()
    threading.Thread(target=run_all, args=(input_path, tasks)).start()
    return jsonify({"status": "started"})

@app.route('/progress')
def progress():
    return jsonify({"log": process_log})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888)
