from flask import Blueprint, jsonify, request

bp = Blueprint("uploads", __name__)

ALLOWED_SOURCES = {
    "google": "google_data",
    "rumble": "rumble_data",
    "binom-rumble": "binom_rumble_spent_data",
    "binom-google": "binom_google_spent_data",
    "rumble-campaign": "rumble_campaign_data",
}


def _validate_source(source: str) -> str | None:
    return ALLOWED_SOURCES.get(source)


@bp.post("/uploads/<source>")
def upload_source(source: str):
    table = _validate_source(source)
    if not table:
        return jsonify({"error": "invalid source"}), 400
    # NOTE: Stub only – implement CSV/JSON parsing and persistence in Phase 1
    return jsonify({"status": "accepted", "source": source}), 202


@bp.get("/<source>/batches")
def list_batches(source: str):
    table = _validate_source(source)
    if not table:
        return jsonify({"error": "invalid source"}), 400
    # NOTE: Stub response
    return jsonify({
        "source": source,
        "batches": [
            {"uploaded_at": "2025-10-06", "report_type": "weekly", "count": 0}
        ],
    })


@bp.delete("/<source>")
def delete_source_data(source: str):
    table = _validate_source(source)
    if not table:
        return jsonify({"error": "invalid source"}), 400
    # Optional query params: uploaded_at=YYYY-MM-DD, report_type=daily|weekly|monthly
    _uploaded_at = request.args.get("uploaded_at")
    _report_type = request.args.get("report_type")
    # NOTE: Stub only – implement delete logic in Phase 1
    return jsonify({
        "status": "queued",
        "source": source,
        "uploaded_at": _uploaded_at,
        "report_type": _report_type,
    })
