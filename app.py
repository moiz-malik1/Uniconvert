import os
import uuid
from flask import Flask, request, render_template, send_file, jsonify
from moviepy.editor import VideoFileClip
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "supersecretkey"

UPLOAD_FOLDER = "uploads"
CONVERTED_FOLDER = "converted"
ALLOWED_EXTENSIONS = {"mp4", "avi", "mov", "mkv"}
OUTPUT_FORMATS = {"mp3", "wav", "ogg", "aac"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["CONVERTED_FOLDER"] = CONVERTED_FOLDER

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CONVERTED_FOLDER, exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return render_template("index.html", formats=OUTPUT_FORMATS)


@app.route("/convert", methods=["POST"])
def convert_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    output_format = request.form.get("format", "mp3")

    if output_format not in OUTPUT_FORMATS:
        return jsonify({"error": "Invalid format"}), 400

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        file_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], f"{file_id}_{filename}")
        file.save(filepath)

        try:
            video = VideoFileClip(filepath)
            output_filename = f"{file_id}.{output_format}"
            output_path = os.path.join(app.config["CONVERTED_FOLDER"], output_filename)

            # Conversion
            video.audio.write_audiofile(
                output_path,
                codec="aac" if output_format == "aac" else None,
                logger=None
            )
            video.close()

            os.remove(filepath)  # cleanup uploaded file

            return send_file(output_path, as_attachment=True)

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return jsonify({"error": "Invalid file type"}), 400


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
