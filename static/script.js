function start() {
    const input_path = document.getElementById('input_path').value;
    const tasks = [];
    if (document.getElementById('concat').checked) tasks.push("concat");
    if (document.getElementById('mp3_to_flac').checked) tasks.push("mp3_to_flac");
    if (document.getElementById('flac_to_mp3').checked) tasks.push("flac_to_mp3");
    if (document.getElementById('set_metadata').checked) tasks.push("set_metadata");

    fetch("/start", {
        method: "POST",
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ input_path, tasks })
    });

    // Start Log-Aktualisierung
    setInterval(() => {
        fetch("/progress")
            .then(res => res.json())
            .then(data => {
                const logEl = document.getElementById('log');
                logEl.textContent = data.log.join("\n");
                logEl.scrollTop = logEl.scrollHeight;
            });
    }, 2000);
}

function pauseTask(task) {
    fetch("/pause", {
        method: "POST",
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task })
    });
}

function resumeTask(task) {
    fetch("/resume", {
        method: "POST",
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task })
    });
}
