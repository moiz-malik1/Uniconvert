import os
import uuid
from flask import Flask, request, render_template, send_file, redirect, flash
from moviepy.editor import VideoFileClip
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "secretkey"
UPLOAD_FOLDER = "uploads"
CONVERTED_FOLDER = "converted"
ALLOWED_EXTENSIONS = {"mp4", "avi", "mov", "mkv"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["CONVERTED_FOLDER"] = CONVERTED_FOLDER

# Make sure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CONVERTED_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if uploaded file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("file")
        output_format = request.form.get("format", "mp3")

        if not file or file.filename == "":
            flash("No file uploaded")
            return redirect(request.url)

        if file and allowed_file(file.filename):
            # 🔹 Use unique filenames to avoid overwriting
            unique_id = str(uuid.uuid4())[:8]
            filename = secure_filename(file.filename)
            base_name, ext = os.path.splitext(filename)
            unique_filename = f"{base_name}_{unique_id}{ext}"
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)
            file.save(filepath)

            try:
                video = VideoFileClip(filepath)

                if not video.audio:
                    video.close()
                    return "No audio stream found in this video", 400

                # 🔹 Unique output filename
                output_filename = f"{base_name}_{unique_id}.{output_format}"
                output_path = os.path.join(app.config["CONVERTED_FOLDER"], output_filename)

                # Write audio file
                if output_format == "mp3":
                    video.audio.write_audiofile(output_path, codec="mp3")
                else:
                    video.audio.write_audiofile(output_path)

                video.close()

                return send_file(output_path, as_attachment=True)

            except Exception as e:
                return f"Conversion error: {str(e)}", 500

        return "Invalid file format", 400

    # Render homepage with available formats
    return render_template("index.html", formats=["mp3", "wav", "ogg", "aac"])

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
