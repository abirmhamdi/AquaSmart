from flask import Blueprint, request, jsonify
from app.services.chatbot import get_response

chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/api/chat", methods=["POST"])
def chat():
    d   = request.get_json(force=True)
    msg = d.get("message", "")
    return jsonify(get_response(msg))
