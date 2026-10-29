"""
AquaSmart — web server entry point.
Flask + Waitress (pure-Python WSGI, no asyncio).

Critical rules for Windows Python 3.13:
  - Load numpy/sklearn model FIRST in the main thread
  - Do NOT call logging.basicConfig() (StreamHandler to stderr crashes waitress)
  - Do NOT import send_file / send_from_directory from flask
  - Do NOT open a socket for port-check before model loading
"""
import sys, os, mimetypes
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

PORT = 8000

print("=" * 55)
print("  AquaSmart — Intelligent Fish Feeding System")
print(f"  http://localhost:{PORT}")
print("=" * 55)
print()

# 1. Load numpy model first (must be main thread, before waitress socket setup)
print("Loading ML model…")
from app.services import ml_service
from app.services.federated import get_server as _fl_init
ml_service.load_model()
_fl_init()
print(f"Model ready: {ml_service._model_meta.get('model', '?')}\n")

# 2. Import routers
from app.routers.predict   import predict_bp
from app.routers.dashboard import dashboard_bp
from app.routers.chat      import chat_bp
from app.routers.federated import federated_bp

# 3. Build Flask app  (only Flask + jsonify — no send_file, no logging.basicConfig)
from flask import Flask, jsonify
from app.config import FRONTEND_DIR, APP_VERSION

flask_app = Flask(__name__, static_folder=None)
flask_app.register_blueprint(predict_bp)
flask_app.register_blueprint(dashboard_bp)
flask_app.register_blueprint(chat_bp)
flask_app.register_blueprint(federated_bp)


def _read_file(path):
    """Serve a static file without importing flask.send_file."""
    mime, _ = mimetypes.guess_type(str(path))
    try:
        with open(path, "rb") as fh:
            body = fh.read()
        from flask import make_response
        resp = make_response(body)
        resp.headers["Content-Type"] = mime or "application/octet-stream"
        resp.headers["Cache-Control"] = "no-store"   # always serve the current files, never a cached copy
        return resp
    except FileNotFoundError:
        return make_response("Not found", 404)


@flask_app.route("/")
def index():
    return _read_file(FRONTEND_DIR / "index.html")


@flask_app.route("/static/<path:filename>")
def static_files(filename):
    return _read_file(FRONTEND_DIR / "static" / filename)


@flask_app.route("/health")
def health():
    return jsonify({"status": "ok", "version": APP_VERSION})


# 4. Start Waitress  (no logging.basicConfig before this point)
from waitress import serve
print(f"Serving frontend from: {FRONTEND_DIR}")
print(f"Server running at http://localhost:{PORT}  (Ctrl+C to stop)\n")
serve(flask_app, host="0.0.0.0", port=PORT, threads=4)
