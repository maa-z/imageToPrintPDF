import os
from flask import Flask, render_template, request, send_file
from fpdf import FPDF
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Folder paths
UPLOAD_FOLDER = "uploads"
GENERATED_FOLDER = "generated"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["GENERATED_FOLDER"] = GENERATED_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(GENERATED_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}


def allowed_file(filename):
    return "." in filename and \
        filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate_pdf():
    files = request.files.getlist("photos")

    if not files or len(files) == 0:
        return "No files uploaded!"

    image_paths = []

    # Save files
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            image_paths.append(filepath)

    # Create PDF
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()

    img_w = 30
    img_h = 35
    gap_x = 3
    gap_y = 5
    margin_left = 10
    margin_top = 10

    current_y = margin_top

    for img in image_paths:
        current_x = margin_left

        for _ in range(6):
            pdf.image(img, x=current_x, y=current_y, w=img_w, h=img_h)
            current_x += img_w + gap_x

        current_y += img_h + gap_y

    output_pdf = os.path.join(GENERATED_FOLDER, "passport_photos.pdf")
    pdf.output(output_pdf)

    return send_file(output_pdf, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
