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
            "thumb": request.files.get("thumb"),
            "aadhar_front": request.files.get("aadhar_front"),
            "aadhar_back": request.files.get("aadhar_back"),
            "paadhar_front": request.files.get("paadhar_front"),
            "paadhar_back": request.files.get("paadhar_back"),
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

        # 🟢 Page 1 - Place Images using X, Y, Width, Height
        if len(doc) > 0:
            if "photo" in image_paths:
                X1, Y1 = 10.3, 101.1  # Starting Position
                WIDTH, HEIGHT = 84.5, 94  # Image Size
                X2, Y2 = X1 + WIDTH, Y1 + HEIGHT  # Calculate Ending Position
                doc[0].insert_image((X1, Y1, X2, Y2), filename=image_paths["photo"])

            if "signature" in image_paths:
                X1, Y1 = 47.1, 159.9  # Starting Position
                WIDTH, HEIGHT = 132.2, 32  # Image Size
                X2, Y2 = X1 + WIDTH, Y1 + HEIGHT
                doc[0].insert_image((X1, Y1, X2, Y2), filename=image_paths["signature"])

            if "thumb" in image_paths:
                X1, Y1 = 68.1, 156.7  # Starting Position
                WIDTH, HEIGHT = 55, 33  # Image Size
                X2, Y2 = X1 + WIDTH, Y1 + HEIGHT
                doc[0].insert_image((X1, Y1, X2, Y2), filename=image_paths["thumb"])

            if "photo" in image_paths:
                X1, Y1 = 467.3, 101.7  # Starting Position
                WIDTH, HEIGHT = 84.5, 94  # Image Size
                X2, Y2 = X1 + WIDTH, Y1 + HEIGHT  # Calculate Ending Position
                doc[0].insert_image((X1, Y1, X2, Y2), filename=image_paths["photo"])

            if "signature" in image_paths:
                X1, Y1 = 393, 203.5  # Starting Position
                WIDTH, HEIGHT = 144, 33.2  # Image Size
                X2, Y2 = X1 + WIDTH, Y1 + HEIGHT
                doc[0].insert_image((X1, Y1, X2, Y2), filename=image_paths["signature"])

            if "thumb" in image_paths:
                X1, Y1 = 429.3, 203.6  # Starting Position
                WIDTH, HEIGHT = 55, 33  # Image Size
                X2, Y2 = X1 + WIDTH, Y1 + HEIGHT
                doc[0].insert_image((X1, Y1, X2, Y2), filename=image_paths["thumb"])

        # 🟢 Page 2 - Place Signature
        if len(doc) > 1:
            if "signature" in image_paths:
                X1, Y1 = 326.5, 746.4
                WIDTH, HEIGHT = 169.8, 38.2
                X2, Y2 = X1 + WIDTH, Y1 + HEIGHT
                doc[1].insert_image((X1, Y1, X2, Y2), filename=image_paths["signature"])

            if "thumb" in image_paths:
                X1, Y1 = 350.5, 745.1
                WIDTH, HEIGHT = 55, 33
                X2, Y2 = X1 + WIDTH, Y1 + HEIGHT
                doc[1].insert_image((X1, Y1, X2, Y2), filename=image_paths["thumb"])

        # 🟢 Add Page 3 if Needed
        if len(doc) < 3:
            doc.new_page()

        # 🟢 Page 3 - Add & Place Images
        if len(doc) > 2:
            if "aadhar_front" in image_paths:
                X1, Y1 = 53, 43.5
                WIDTH, HEIGHT = 205.5, 127.7
                X2, Y2 = X1 + WIDTH, Y1 + HEIGHT
                doc[2].insert_image((X1, Y1, X2, Y2), filename=image_paths["aadhar_front"])

            if "aadhar_back" in image_paths:
                X1, Y1 = 280.2, 43.5
                WIDTH, HEIGHT = 205.5, 127.7
                X2, Y2 = X1 + WIDTH, Y1 + HEIGHT
                doc[2].insert_image((X1, Y1, X2, Y2), filename=image_paths["aadhar_back"])

            if "paadhar_front" in image_paths:
                X1, Y1 = 53, 43.5
                WIDTH, HEIGHT = 209, 129
                X2, Y2 = X1 + WIDTH, Y1 + HEIGHT
                doc[2].insert_image((X1, Y1, X2, Y2), filename=image_paths["pan"])

            if "paadhar_back" in image_paths:
                X1, Y1 = 280.2, 43.5
                WIDTH, HEIGHT = 209, 129
                X2, Y2 = X1 + WIDTH, Y1 + HEIGHT
                doc[2].insert_image((X1, Y1, X2, Y2), filename=image_paths["pan"])

            if "pan" in image_paths:
                X1, Y1 = 175.6, 211.1
                WIDTH, HEIGHT = 205.5, 127.7
                X2, Y2 = X1 + WIDTH, Y1 + HEIGHT
                doc[2].insert_image((X1, Y1, X2, Y2), filename=image_paths["pan"])

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
