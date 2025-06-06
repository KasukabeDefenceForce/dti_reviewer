from flask import Blueprint, request, jsonify
from app import similarity_engine

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
        results_df = similarity_engine.query_experts(query, top_n=25)
    except Exception:
        return (
            jsonify(message="Server error processing query", results=[]),
            500,
        )
    records = results_df.to_dict(orient="records")
    if not records:
        return (
            jsonify(message="No results found", results=[]),
            200,
        )

    return (
        jsonify(message="Success", results=records),
        200,
    )