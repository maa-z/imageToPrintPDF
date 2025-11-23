import os
from flask import Flask, render_template, request, send_file
from fpdf import FPDF
from werkzeug.utils import secure_filename
from PIL import Image

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
GENERATED_FOLDER = "generated"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["GENERATED_FOLDER"] = GENERATED_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(GENERATED_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "heic", "heif"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def convert_to_jpg(input_path):
    """Converts PNG/HEIC/WEBP etc. to actual JPG file for FPDF."""
    img = Image.open(input_path).convert("RGB")
    output_path = input_path.rsplit(".", 1)[0] + "_converted.jpg"
    img.save(output_path, "JPEG", quality=95)
    return output_path


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate_pdf():
    files = request.files.getlist("photos")

    if not files:
        return "No files selected!"

    processed_images = []

    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            fp = os.path.join(UPLOAD_FOLDER, filename)
            file.save(fp)

            # Convert to safe JPG
            final_image = convert_to_jpg(fp)
            processed_images.append(final_image)

    # Generate PDF
    pdf = FPDF("P", "mm", "A4")
    pdf.add_page()

    img_w = 30
    img_h = 35
    gap_x = 3
    gap_y = 5
    margin_left = 10
    margin_top = 10
    current_y = margin_top

    for img in processed_images:
        current_x = margin_left

        for _ in range(6):
            pdf.image(img, x=current_x, y=current_y, w=img_w, h=img_h)
            current_x += img_w + gap_x

        current_y += img_h + gap_y

    output_pdf = os.path.join(GENERATED_FOLDER, "passport_photos.pdf")
    pdf.output(output_pdf)

    return send_file(output_pdf, as_attachment=True)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
