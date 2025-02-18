from flask import Flask, request, send_file, render_template
import fitz  # PyMuPDF
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# 📌 Image Placement Coordinates (Update later)
COORDINATES = {
    "photo": [(100, 150), (300, 150)],  # Page 1 (Two Places)
    "signature": [(100, 250), (300, 250), (150, 400)],  # Page 1 (Two), Page 2 (One)
    "aadhar_front": [(50, 50)],  # Page 3
    "aadhar_back": [(250, 50)],  # Page 3
    "pan": [(450, 50)]  # Page 3 (Optional)
}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/process-pdf", methods=["POST"])
def process_pdf():
    try:
        # 📌 Upload Files
        pdf_file = request.files["pdf"]
        images = {
            "photo": request.files["photo"],
            "signature": request.files["signature"],
            "aadhar_front": request.files["aadhar_front"],
            "aadhar_back": request.files["aadhar_back"],
            "pan": request.files.get("pan")
        }

        pdf_path = os.path.join(UPLOAD_FOLDER, secure_filename(pdf_file.filename))
        pdf_file.save(pdf_path)

        # 📌 Save Images
        image_paths = {}
        for key, file in images.items():
            if file:
                path = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
                file.save(path)
                image_paths[key] = path

        # 📌 Process PDF
        doc = fitz.open(pdf_path)

        # 🟢 Page 1 - Place Images
        for idx, img_type in enumerate(["photo", "photo", "signature", "signature"]):
            x, y = COORDINATES[img_type][idx]
            doc[0].insert_image((x, y, x + 100, y + 100), filename=image_paths[img_type])

        # 🟢 Page 2 - Place Signature
        x, y = COORDINATES["signature"][2]
        doc[1].insert_image((x, y, x + 100, y + 50), filename=image_paths["signature"])

        # 🟢 Page 3 - Add & Place Images
        page3 = doc.new_page()
        for img_type in ["aadhar_front", "aadhar_back", "pan"]:
            if img_type in image_paths:
                x, y = COORDINATES[img_type][0]
                page3.insert_image((x, y, x + 150, y + 100), filename=image_paths[img_type])

        # 📌 Save Processed PDF
        output_pdf = os.path.join(PROCESSED_FOLDER, "edited.pdf")
        doc.save(output_pdf)
        doc.close()

        return send_file(output_pdf, as_attachment=True)

    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    app.run(debug=True)
