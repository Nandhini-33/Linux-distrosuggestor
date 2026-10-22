"""
Linux Distribution Advisor - Flask Web Application
Provides interactive hardware & preference assessment, algorithmic distribution
recommendations, comparison tools, and beginner guides.
"""

import os
import tempfile
import logging
from dotenv import load_dotenv

# Load environment variables at app startup
load_dotenv()

from flask import Flask, render_template, request, jsonify, redirect, url_for
from distro_data import DISTRIBUTIONS, get_all_distros, get_distro_by_id
from recommender import calculate_recommendation
from database import init_db, save_recommendation, get_recent_recommendations, get_distro_popularity
from voice_engine import transcribe_audio, match_voice_to_option
from chat_advisor import process_chat_message

logger = logging.getLogger(__name__)

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates"),
    static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
)
# Initialize SQLite database on startup
init_db()

@app.route("/")
def index():
    """Main landing page with interactive advisor questionnaire."""
    recent_recs = get_recent_recommendations(limit=4)
    popularity = get_distro_popularity()
    all_distros = get_all_distros()
    return render_template(
        "index.html",
        recent_recs=recent_recs,
        popularity=popularity,
        total_distros=len(all_distros),
        distros=all_distros
    )

@app.route("/api/recommend", methods=["POST"])
def api_recommend():
    """API endpoint to calculate recommendation from JSON."""
    data = request.get_json() or {}
    
    # Extract user inputs with sensible defaults
    user_input = {
        "ram": data.get("ram", "4GB - 8GB"),
        "experience": data.get("experience", "Beginner"),
        "purpose": data.get("purpose", "General use"),
        "cpu": data.get("cpu", "Mid-range Quad Core (Intel i3/i5, AMD Ryzen 3/5)"),
        "storage": data.get("storage", "20GB - 50GB"),
        "preference": data.get("preference", "Easy to use"),
        "prev_experience": data.get("prev_experience", "None / First time")
    }

    result = calculate_recommendation(user_input)
    rec_id = save_recommendation(user_input, result)
    result["recommendation_id"] = rec_id

    return jsonify({"success": True, "data": result})

@app.route("/api/chat_advisor", methods=["POST"])
@app.route("/chat", methods=["POST"])
def api_chat_advisor():
    """
    Handles conversational Linux distribution advisory questions.
    Filters out unrelated queries, respects chat history, and contextualizes quiz results.
    """
    data = request.get_json() or {}
    message = data.get("message", "")
    context = data.get("context", {})
    history = data.get("history", [])
    quiz_result = data.get("quiz_result")

    if not quiz_result:
        from database import get_latest_recommendation
        quiz_result = get_latest_recommendation()

    response_data = process_chat_message(
        message=message,
        context=context,
        history=history,
        quiz_result=quiz_result
    )
    return jsonify({"success": True, "data": response_data})

@app.route("/transcribe", methods=["POST"])
def transcribe():
    """
    Transcribes audio received from browser MediaRecorder (webm/ogg/mp4) in-memory using Gemini,
    maps spoken words to questionnaire option values if question is specified, and returns JSON.
    """
    if "audio" not in request.files:
        return jsonify({"success": False, "error": "No audio file provided"}), 400

    audio_file = request.files["audio"]
    question_key = request.form.get("question", "")
    language_hint = request.form.get("language", "auto")

    # Read audio into memory only - never save to disk
    audio_bytes = audio_file.read()
    if not audio_bytes:
        return jsonify({"success": False, "error": "Empty audio file received"}), 400

    if len(audio_bytes) > 4 * 1024 * 1024:
        return jsonify({
            "success": False,
            "error_type": "file_too_large",
            "error": "Audio file exceeds 4 MB limit."
        }), 400

    mimetype = audio_file.content_type or "audio/webm"

    try:
        success, transcript, error_type, error_msg = transcribe_audio(
            audio_bytes=audio_bytes,
            mime_type=mimetype,
            language_hint=language_hint,
            question_key=question_key
        )

        if not success:
            logger.warning(f"Audio transcription unsuccessful ({error_type}): {error_msg}")
            return jsonify({
                "success": False,
                "error_type": error_type or "transcription_error",
                "error": error_msg or "Failed to transcribe audio."
            }), 200

        logger.info(f"Transcribed audio for '{question_key}': '{transcript}'")

        matched_option = None
        if question_key and question_key != "chat":
            matched_option = match_voice_to_option(question_key, transcript)

        return jsonify({
            "success": True,
            "transcript": transcript,
            "matched": matched_option is not None,
            "option_value": matched_option,
            "question": question_key
        })
    except Exception as e:
        logger.error(f"Error during audio transcription: {e}")
        return jsonify({
            "success": False,
            "error_type": "server_error",
            "error": str(e)
        }), 500

@app.route("/recommend", methods=["POST"])
def form_recommend():
    """Form submission fallback for non-JS clients."""
    user_input = {
        "ram": request.form.get("ram", "4GB - 8GB"),
        "experience": request.form.get("experience", "Beginner"),
        "purpose": request.form.get("purpose", "General use"),
        "cpu": request.form.get("cpu", "Mid-range Quad Core (Intel i3/i5, AMD Ryzen 3/5)"),
        "storage": request.form.get("storage", "20GB - 50GB"),
        "preference": request.form.get("preference", "Easy to use"),
        "prev_experience": request.form.get("prev_experience", "None / First time")
    }

    result = calculate_recommendation(user_input)
    save_recommendation(user_input, result)
    
    recent_recs = get_recent_recommendations(limit=4)
    popularity = get_distro_popularity()
    all_distros = get_all_distros()

    return render_template(
        "index.html",
        result=result,
        recent_recs=recent_recs,
        popularity=popularity,
        total_distros=len(all_distros),
        distros=all_distros,
        submitted_input=user_input
    )

@app.route("/distros")
def distro_catalog():
    """Explore and search all distributions."""
    distros = get_all_distros()
    return render_template("distros.html", distros=distros)

@app.route("/distro/<distro_id>")
def distro_detail(distro_id):
    """Deep-dive profile page for a specific distribution."""
    distro = get_distro_by_id(distro_id)
    if not distro:
        return redirect(url_for("distro_catalog"))
    return render_template("distro_detail.html", distro=distro)

@app.route("/compare")
def compare():
    """Side-by-side comparison between 2 or 3 distros."""
    all_distros = get_all_distros()
    d1 = request.args.get("d1", "linux-mint")
    d2 = request.args.get("d2", "ubuntu")
    d3 = request.args.get("d3", "fedora")

    distro1 = get_distro_by_id(d1) or all_distros[0]
    distro2 = get_distro_by_id(d2) or (all_distros[1] if len(all_distros) > 1 else None)
    distro3 = get_distro_by_id(d3) if d3 else None

    return render_template(
        "compare.html",
        distros=all_distros,
        d1=distro1,
        d2=distro2,
        d3=distro3
    )

@app.route("/guide")
def guide():
    """Beginner's step-by-step launchpad into Linux."""
    return render_template("guide.html")

@app.route("/api/distros")
def api_distros():
    """JSON catalog endpoint."""
    return jsonify(get_all_distros())

if __name__ == "__main__":
    # Host on 0.0.0.0 for cross-device & container compatibility
    # use_reloader=False ensures single-process whisper model memory allocation
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
