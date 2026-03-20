import logging
import os
import subprocess
import tempfile
import time

from flask import Flask, request, jsonify

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
log = logging.getLogger(__name__)

app = Flask(__name__)

PRINTER = "Brother_DCP_L2540DW_series"
PRINT_RETRIES = 3
PRINT_RETRY_DELAY = 30  # seconds


@app.route("/print", methods=["POST"])
def print_file():
    if "file" not in request.files:
        log.warning("Request rejected: no file provided")
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]

    if not file.filename.lower().endswith(".pdf"):
        log.warning("Request rejected: non-PDF file '%s'", file.filename)
        return jsonify({"error": "Only PDF files are accepted"}), 400

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        file.save(tmp.name)
        tmp_path = tmp.name

    size_kb = os.path.getsize(tmp_path) // 1024
    log.info("Received '%s' (%d KB), sending to printer '%s'", file.filename, size_kb, PRINTER)

    try:
        last_stderr = ""
        for attempt in range(1, PRINT_RETRIES + 1):
            log.info("Print attempt %d/%d", attempt, PRINT_RETRIES)
            result = subprocess.run(
                ["lp", "-d", PRINTER, tmp_path],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                log.info("Print succeeded: %s", result.stdout.strip())
                return jsonify({"status": "ok", "message": result.stdout.strip()})

            last_stderr = result.stderr.strip()
            log.error("Attempt %d failed: %s", attempt, last_stderr)
            if attempt < PRINT_RETRIES:
                log.info("Retrying in %ds...", PRINT_RETRY_DELAY)
                time.sleep(PRINT_RETRY_DELAY)

        log.error("All %d attempts failed, giving up", PRINT_RETRIES)
        return jsonify({"error": "Print failed", "detail": last_stderr}), 500
    finally:
        os.unlink(tmp_path)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8631)
