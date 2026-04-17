
from flask import Blueprint, jsonify, request
from app.AI.agent.agent import UserAssistantAgent

assistant_bp = Blueprint("assistant", __name__, url_prefix="/api/assistant")

agent = UserAssistantAgent()

@assistant_bp.post("/ask")
def ask():
    payload = request.get_json(silent=True) or {}

    username = str(payload.get("username") or "").strip()
    question = str(payload.get("question") or "").strip()

    if not question:
        return jsonify({"message": "问题不能为空"}), 400

    try:
        answer = agent.ask(question=question, username=username)
        return jsonify({"answer": answer})
    except Exception:
        return jsonify({"message": "系统繁忙，请稍后再试"}), 500
