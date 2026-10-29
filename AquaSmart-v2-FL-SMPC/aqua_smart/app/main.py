"""
AquaSmart Flask application factory.
The ML model is loaded by run.py BEFORE create_app() is called.
"""
import logging
from flask import Flask, jsonify, send_from_directory, send_file
from app.config import FRONTEND_DIR, APP_VERSION

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)


def create_app():
    app = Flask(__name__, static_folder=None)
    app.config["JSON_SORT_KEYS"] = False

    @app.route("/")
    def index():
        return send_file(FRONTEND_DIR / "index.html")

    @app.route("/static/<path:filename>")
    def static_files(filename):
        return send_from_directory(FRONTEND_DIR / "static", filename)

    @app.route("/health")
    def health():
        return jsonify({"status": "ok", "version": APP_VERSION})

    from app.routers.predict   import predict_bp
    from app.routers.dashboard import dashboard_bp
    from app.routers.chat      import chat_bp
    from app.routers.federated import federated_bp

    app.register_blueprint(predict_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(federated_bp)

    return app
