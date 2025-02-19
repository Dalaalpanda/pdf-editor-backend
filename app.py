from flask import Flask, request, send_file, jsonify
from flask_cors import CORS  # 🟢 CORS Fix ke liye import
import fitz  # PyMuPDF
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)  # 🟢 Enable CORS so that frontend can access the backend

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

# ✅ Root Route (Fixes "Not Found" Error)
@app.route("/")
def home():
    return "PDF Editor Backend is Running!", 200

@app.route("/process-pdf", methods=["POST"])
def process_pdf():
    try:
        if "pdf" not in request.files:
            return jsonify({"error": "PDF file is missing"}), 400

        # 📌 Upload Files
        pdf_file = request.files["pdf"]
        pdf_filename = secure_filename(pdf_file.filename)
        pdf_path = os.path.join(UPLOAD_FOLDER, pdf_filename)
        pdf_file.save(pdf_path)

        images = {
            "photo": request.files.get("photo"),
            "signature": request.files.get("signature"),
            "aadhar_front": request.files.get("aadhar_front"),
            "aadhar_back": request.files.get("aadhar_back"),
            "pan": request.files.get("pan")
        }

        # 📌 Save Images
        image_paths = {}
        for key, file in images.items():
            if file:
                path = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
                file.save(path)
                image_paths[key] = path

        # 📌 Process PDF
        doc = fitz.open(pdf_path)

        # 🟢 Ensure PDF has at least 2 Pages
        if len(doc) < 2:
            return jsonify({"error": "PDF must have at least 2 pages"}), 400

        # 🟢 Page 1 - Place Images
        for idx, img_type in enumerate(["photo", "photo", "signature", "signature"]):
            if img_type in image_paths:
                x, y = COORDINATES[img_type][idx]
                doc[0].insert_image((x, y, x + 100, y + 100), filename=image_paths[img_type])

        # 🟢 Page 2 - Place Signature
        if "signature" in image_paths:
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

        # 🟢 Ensure File is Properly Closed Before Sending
        return send_file(output_pdf, as_attachment=True, mimetype="application/pdf")

    except Exception as e:
        return jsonify({"error": str(e)}), 500  # 🟢 Better Error Response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)  # ✅ Port Fix for Render
