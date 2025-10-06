from __future__ import annotations

import datetime as dt
import re
from collections import defaultdict
from typing import Dict, Tuple

from flask import Blueprint, jsonify, request, g
from sqlalchemy import select, func

from app.models import GoogleData, BinomGoogleSpentData

bp = Blueprint("reports", __name__)


def _parse_date(value: str) -> dt.date:
    return dt.date.fromisoformat(value)


def _norm(s: str | None) -> str:
    if not s:
        return ""
    s = s.lower().strip()
    # remove non-alnum
    return re.sub(r"[^a-z0-9]", "", s)


@bp.get("/reports/google-binom")
def google_binom_report():
    # Query params: report_type=weekly|monthly, date_from=YYYY-MM-DD, date_to=YYYY-MM-DD
    report_type = request.args.get("report_type", "weekly")
    date_from_s = request.args.get("date_from")
    date_to_s = request.args.get("date_to")
    roi_last_mode = request.args.get("roi_last_mode", "full")  # full|cohort

    if not (date_from_s and date_to_s):
        return jsonify({"error": "date_from and date_to are required"}), 400

    try:
        date_from = _parse_date(date_from_s)
        date_to = _parse_date(date_to_s)
    except Exception:
        return jsonify({"error": "invalid date format, use YYYY-MM-DD"}), 400

    db = g.db

    # Aggregate Google spend by campaign
    g_stmt = (
        select(
            GoogleData.campaign,
            func.sum(GoogleData.cost).label("spend"),
        )
        .where(
            GoogleData.date_from == date_from,
            GoogleData.date_to == date_to,
            GoogleData.report_type == report_type,
        )
        .group_by(GoogleData.campaign)
    )

    # Aggregate Binom revenue/leads by name
    b_stmt = (
        select(
            BinomGoogleSpentData.name,
            func.sum(BinomGoogleSpentData.revenue).label("revenue"),
            func.sum(BinomGoogleSpentData.leads).label("leads"),
        )
        .where(
            BinomGoogleSpentData.date_from == date_from,
            BinomGoogleSpentData.date_to == date_to,
            BinomGoogleSpentData.report_type == report_type,
        )
        .group_by(BinomGoogleSpentData.name)
    )

    google_rows = list(db.execute(g_stmt))
    binom_rows = list(db.execute(b_stmt))

    # Build maps by normalized key
    g_map: Dict[str, Tuple[str, float]] = {}
    for campaign, spend in google_rows:
        key = _norm(campaign)
        if not key:
            continue
        g_map[key] = (campaign or "", float(spend or 0))

    b_map: Dict[str, Tuple[str, float, int]] = {}
    for name, revenue, leads in binom_rows:
        key = _norm(name)
        if not key:
            continue
        b_map[key] = (name or "", float(revenue or 0), int(leads or 0))

    # Join
    seen = set()
    rows = []
    total_spend = 0.0
    total_revenue = 0.0
    for key, (campaign, spend) in g_map.items():
        name = campaign
        revenue = 0.0
        leads = 0
        if key in b_map:
            _bname, brevenue, bleads = b_map[key]
            revenue = brevenue
            leads = bleads
            name = _bname or campaign
            seen.add(key)
        pl = (revenue - spend)
        roi = (revenue / spend * 100.0) if spend and revenue else (0.0 if spend else None)
        rows.append(
            {
                "campaign": campaign,
                "name": name,
                "spend": round(spend, 2),
                "revenue": round(revenue, 2),
                "pl": round(pl, 2),
                "roi": (round(roi, 2) if roi is not None else None),
                "leads": leads,
            }
        )
        total_spend += spend or 0.0
        total_revenue += revenue or 0.0

    # Include Binom-only rows to preserve totals
    for key, (bname, brevenue, bleads) in b_map.items():
        if key in seen:
            continue
        rows.append(
            {
                "campaign": None,
                "name": bname,
                "spend": 0.0,
                "revenue": round(brevenue or 0.0, 2),
                "pl": round((brevenue or 0.0), 2),
                "roi": None,
                "leads": bleads or 0,
            }
        )
        total_revenue += brevenue or 0.0

    summary = {
        "spend": round(total_spend, 2),
        "revenue": round(total_revenue, 2),
        "pl": round(total_revenue - total_spend, 2),
        "roi": (round((total_revenue / total_spend * 100.0), 2) if total_spend else None),
        "roi_last": None,  # computed when prior period is implemented
    }

    # Optional: could add account_summaries if account data is present
    return jsonify(
        {
            "report": "google-binom",
            "report_type": report_type,
            "date_from": str(date_from),
            "date_to": str(date_to),
            "roi_last_mode": roi_last_mode,
            "rows": rows,
            "account_summaries": [],
            "summary": summary,
        }
    )


@bp.get("/reports/rumble-binom")
def rumble_binom_report():
    # Still a stub for Phase 3
    report_type = request.args.get("report_type", "weekly")
    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")
    return jsonify(
        {
            "report": "rumble-binom",
            "report_type": report_type,
            "date_from": date_from,
            "date_to": date_to,
            "rows": [],
            "account_summaries": [],
            "summary": {"spend": 0, "revenue": 0, "pl": 0, "roi": None},
        }
    )
