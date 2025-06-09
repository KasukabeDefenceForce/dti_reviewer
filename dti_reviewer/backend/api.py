from flask import Blueprint, request, jsonify
from tasks import query_experts_task
from celery.result import AsyncResult
from celery_app import celery

api_bp = Blueprint("api", __name__)

@api_bp.route('/search', methods=['POST'])
def search():
    """
    Search for experts based on a research abstract.
    
    The endpoint processes the input query and returns a ranked list of experts
    whose work most closely matches the research abstract.
    """
    data = request.get_json()
    query = data.get("query", None)
    if query is None:
        return (
            jsonify(message="Missing 'query' parameter", results=[]),
            400,
        )
    query = query.strip()
    if not query:
        return (
            jsonify(message="Query cannot be empty", results=[]),
            400,
        )
    if len(query) < 3:
        return (
            jsonify(message="Query too short. Minimum 3 characters", results=[]),
            400,
        )

    try:
        celery_task = query_experts_task.delay(query, top_n=25)
        return (
            jsonify(
                message="Task submitted",
                task_id=celery_task.id,
            ),
            202,
        )
    except Exception as e:
        return jsonify(message="Server error enqueuing task", task_id=None), 500
    
@api_bp.route("/status/<task_id>", methods=["GET"])
def task_status(task_id):
    async_result = AsyncResult(task_id, app=celery)
    state = async_result.state

    # Base response always includes the state
    resp = {"state": state}

    if state == "PENDING":
        return jsonify(resp), 202

    if state == "PROGRESS":
        resp["percent"] = async_result.info.get("percent", 0)
        return jsonify(resp), 202

    if state == "SUCCESS":
        resp["results"] = async_result.result
        return jsonify(resp), 200
    resp["message"] = str(async_result.info)
    return jsonify(resp), 500
