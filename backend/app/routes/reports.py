from flask import Blueprint, jsonify, request

bp = Blueprint("reports", __name__)


@bp.get("/reports/google-binom")
def google_binom_report():
    # Query params: report_type=weekly|monthly, date_from=YYYY-MM-DD, date_to=YYYY-MM-DD
    report_type = request.args.get("report_type", "weekly")
    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")
    roi_last_mode = request.args.get("roi_last_mode", "full")  # full|cohort
    # NOTE: Stub response – implement service logic in Phase 2
    return jsonify({
        "report": "google-binom",
        "report_type": report_type,
        "date_from": date_from,
        "date_to": date_to,
        "roi_last_mode": roi_last_mode,
        "rows": [],
        "account_summaries": [],
        "summary": {"spend": 0, "revenue": 0, "pl": 0, "roi": None, "roi_last": None},
    })


@bp.get("/reports/rumble-binom")
def rumble_binom_report():
    # Query params: report_type=daily|weekly|monthly, date_from=YYYY-MM-DD, date_to=YYYY-MM-DD
    report_type = request.args.get("report_type", "weekly")
    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")
    # NOTE: Stub response – implement service logic in Phase 3
    return jsonify({
        "report": "rumble-binom",
        "report_type": report_type,
        "date_from": date_from,
        "date_to": date_to,
        "rows": [],
        "account_summaries": [],
        "summary": {"spend": 0, "revenue": 0, "pl": 0, "roi": None},
    })
