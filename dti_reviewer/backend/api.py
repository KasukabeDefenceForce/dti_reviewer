import logging
from flask import Blueprint, request, jsonify
from tasks import query_experts_task
from celery.result import AsyncResult
from celery_app import celery

# Set up logger for this module
logger = logging.getLogger(__name__)

api_bp = Blueprint("api", __name__)


@api_bp.route("/search", methods=["POST"])
def search():
    """
    Search for experts based on a research abstract.
    The endpoint processes the input query and returns a ranked list of experts
    whose work most closely matches the research abstract.
    """
    client_ip = request.environ.get("HTTP_X_FORWARDED_FOR", request.remote_addr)
    logger.info(f"Search request received from {client_ip}")

    try:
        data = request.get_json()
        logger.debug(f"Request data received: {data}")

        query = data.get("query", None) if data else None

        if query is None:
            logger.warning(f"Missing query parameter in request from {client_ip}")
            return (
                jsonify(message="Missing 'query' parameter", results=[]),
                400,
            )

        query = query.strip()
        logger.debug(f"Query after stripping: '{query}' (length: {len(query)})")

        if not query:
            logger.warning(f"Empty query received from {client_ip}")
            return (
                jsonify(message="Query cannot be empty", results=[]),
                400,
            )

        if len(query) < 3:
            logger.warning(
                f"Query too short from {client_ip}: '{query}' (length: {len(query)})"
            )
            return (
                jsonify(message="Query too short. Minimum 3 characters", results=[]),
                400,
            )

        logger.info(
            f"Processing valid query from {client_ip}: '{query[:100]}{'...' if len(query) > 100 else ''}'"
        )

        celery_task = query_experts_task.delay(query, top_n=25)
        task_id = celery_task.id

        logger.info(
            f"Celery task {task_id} submitted successfully for query from {client_ip}"
        )

        return (
            jsonify(
                message="Task submitted",
                task_id=task_id,
            ),
            202,
        )

    except Exception as e:
        logger.error(
            f"Error processing search request from {client_ip}: {str(e)}", exc_info=True
        )
        return jsonify(message="Server error enqueuing task", task_id=None), 500


@api_bp.route("/status/<task_id>", methods=["GET"])
def task_status(task_id):
    """
    Get the status of a submitted task.
    """
    client_ip = request.environ.get("HTTP_X_FORWARDED_FOR", request.remote_addr)
    logger.info(f"Status check for task {task_id} from {client_ip}")

    try:
        async_result = AsyncResult(task_id, app=celery)
        state = async_result.state

        logger.debug(f"Task {task_id} state: {state}")

        # Base response always includes the state
        resp = {"state": state}

        if state == "PENDING":
            logger.debug(f"Task {task_id} is pending")
            return jsonify(resp), 202

        if state == "PROGRESS":
            percent = async_result.info.get("percent", 0)
            resp["percent"] = percent
            logger.debug(f"Task {task_id} in progress: {percent}%")
            return jsonify(resp), 202

        if state == "SUCCESS":
            result_count = len(async_result.result) if async_result.result else 0
            resp["results"] = async_result.result
            logger.info(
                f"Task {task_id} completed successfully with {result_count} results"
            )
            return jsonify(resp), 200

        # Handle failure states (FAILURE, RETRY, REVOKED, etc.)
        error_info = str(async_result.info) if async_result.info else "Unknown error"
        resp["message"] = error_info
        logger.error(f"Task {task_id} failed with state {state}: {error_info}")
        return jsonify(resp), 500

    except Exception as e:
        logger.error(
            f"Error checking status for task {task_id} from {client_ip}: {str(e)}",
            exc_info=True,
        )
        return jsonify(
            {"state": "ERROR", "message": "Error retrieving task status"}
        ), 500
