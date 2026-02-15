import os
import subprocess
import tempfile

from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/print", methods=["POST"])
def print_file():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]

    if not file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Only PDF files are accepted"}), 400

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        file.save(tmp.name)
        tmp_path = tmp.name

    try:
        result = subprocess.run(
            ["lp", tmp_path],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return jsonify({"error": "Print failed", "detail": result.stderr}), 500
        return jsonify({"status": "ok", "message": result.stdout.strip()})
    finally:
        os.unlink(tmp_path)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8631)
