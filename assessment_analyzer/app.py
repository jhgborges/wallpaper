import os
import uuid

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, send_from_directory, url_for
from werkzeug.utils import secure_filename

from services.analyzer import AnalysisError, analyze_assessment
from services.pdf_extract import extract_text
from services.report import generate_report

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {"pdf"}
MAX_CONTENT_LENGTH = 20 * 1024 * 1024  # 20 MB

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key-change-me")
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    uploaded_file = request.files.get("assessment_file")

    if uploaded_file is None or uploaded_file.filename == "":
        flash("Selecione um arquivo PDF com a avaliação.")
        return redirect(url_for("index"))

    if not allowed_file(uploaded_file.filename):
        flash("Apenas arquivos PDF são aceitos.")
        return redirect(url_for("index"))

    job_id = uuid.uuid4().hex
    safe_name = secure_filename(uploaded_file.filename)
    saved_path = os.path.join(UPLOAD_DIR, f"{job_id}_{safe_name}")
    uploaded_file.save(saved_path)

    try:
        assessment_text = extract_text(saved_path)
        analysis_data = analyze_assessment(assessment_text)

        report_filename = f"relatorio_{job_id}.pdf"
        report_path = os.path.join(REPORTS_DIR, report_filename)
        generate_report(analysis_data, report_path)
    except AnalysisError as exc:
        flash(str(exc))
        return redirect(url_for("index"))
    except Exception as exc:  # noqa: BLE001 - surfaced to the user as a friendly message
        flash(f"Ocorreu um erro ao processar o arquivo: {exc}")
        return redirect(url_for("index"))
    finally:
        if os.path.exists(saved_path):
            os.remove(saved_path)

    return render_template(
        "result.html",
        report_filename=report_filename,
        num_questoes=len(analysis_data.get("questoes", [])),
        titulo=analysis_data.get("titulo_avaliacao") or "Avaliação analisada",
    )


@app.route("/download/<filename>", methods=["GET"])
def download(filename):
    safe_filename = secure_filename(filename)
    return send_from_directory(REPORTS_DIR, safe_filename, as_attachment=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
