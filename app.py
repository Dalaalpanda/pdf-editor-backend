from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import fitz  # PyMuPDF
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

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
        if len(doc) > 0:
            if "photo" in image_paths:
                doc[0].insert_image((100, 150, 200, 250), filename=image_paths["photo"])
            if "signature" in image_paths:
                doc[0].insert_image((100, 250, 200, 290), filename=image_paths["signature"])

        # 🟢 Page 2 - Place Signature
        if len(doc) > 1:
            if "signature" in image_paths:
                doc[1].insert_image((100, 300, 200, 340), filename=image_paths["signature"])

        # 🟢 Add Page 3 if Needed
        if len(doc) < 3:
            doc.new_page()

        # 🟢 Page 3 - Add & Place Images
        if len(doc) > 2:
            if "aadhar_front" in image_paths:
                doc[2].insert_image((50, 50, 200, 200), filename=image_paths["aadhar_front"])
            if "aadhar_back" in image_paths:
                doc[2].insert_image((250, 50, 400, 200), filename=image_paths["aadhar_back"])
            if "pan" in image_paths:
                doc[2].insert_image((450, 50, 600, 200), filename=image_paths["pan"])

        # 📌 Save Processed PDF
        output_pdf = os.path.join(PROCESSED_FOLDER, "edited.pdf")
        doc.save(output_pdf)
        doc.close()

        # ✅ Ensure PDF is Valid Before Sending
        if not os.path.exists(output_pdf) or os.path.getsize(output_pdf) == 0:
            return jsonify({"error": "Failed to generate valid PDF"}), 500

        return send_file(output_pdf, as_attachment=True, mimetype="application/pdf")

    except Exception as e:
        return jsonify({"error": str(e)}), 500  # 🟢 Better Error Response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
