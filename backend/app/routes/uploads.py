from __future__ import annotations

import csv
import datetime as dt
from io import TextIOWrapper
from typing import Iterable

from flask import Blueprint, jsonify, request, g
from sqlalchemy import select, func, delete

from app.models import (
    Upload,
    GoogleData,
    BinomGoogleSpentData,
)

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


def _parse_date(value: str) -> dt.date:
    return dt.date.fromisoformat(value)


def _normalize_header(h: str) -> str:
    return (h or "").strip().lower().replace(" ", "_")


def _iter_csv(file_storage, delimiter: str | None = None) -> Iterable[dict]:
    text = TextIOWrapper(file_storage.stream, encoding="utf-8", errors="replace")
    # Try to sniff delimiter if not provided
    if delimiter is None:
        sample = text.read(2048)
        text.seek(0)
        try:
            sniffed = csv.Sniffer().sniff(sample, delimiters=",;\t")
            delimiter = sniffed.delimiter
        except Exception:
            delimiter = ","
    reader = csv.DictReader(text, delimiter=delimiter)
    reader.fieldnames = [
        _normalize_header(h) for h in (reader.fieldnames or [])
    ]
    for row in reader:
        yield {k: (v.strip() if isinstance(v, str) else v) for k, v in row.items()}


@bp.post("/uploads/<source>")
def upload_source(source: str):
    table = _validate_source(source)
    if not table:
        return jsonify({"error": "invalid source"}), 400

    # Required meta
    date_from_s = request.form.get("date_from")
    date_to_s = request.form.get("date_to")
    report_type = request.form.get("report_type", "weekly")
    if not (date_from_s and date_to_s):
        return jsonify({"error": "date_from and date_to are required"}), 400
    try:
        date_from = _parse_date(date_from_s)
        date_to = _parse_date(date_to_s)
    except Exception:
        return jsonify({"error": "invalid date format, use YYYY-MM-DD"}), 400

    f = request.files.get("file")
    if not f:
        return jsonify({"error": "file is required (multipart/form-data)"}), 400

    db = g.db
    now = dt.datetime.now(dt.timezone.utc)

    # Create upload record
    upload = Upload(
        source_type=source,
        filename=f.filename or "upload.csv",
        checksum=None,
        uploaded_at=now,
    )
    db.add(upload)
    db.flush()  # allocate upload.id

    inserted = 0
    # Google CSV ingestion
    if source == "google":
        for row in _iter_csv(f):
            account = row.get("account") or row.get("account_name")
            campaign = row.get("campaign")
            cost_s = row.get("cost")
            if not campaign:
                continue
            try:
                cost = float(cost_s) if cost_s not in (None, "") else None
            except Exception:
                cost = None
            db.add(
                GoogleData(
                    account_name=account,
                    campaign=campaign,
                    cost=cost,
                    date_from=date_from,
                    date_to=date_to,
                    report_type=report_type,
                    upload_id=upload.id,
                )
            )
            inserted += 1
    elif source == "binom-google":
        # Binom exports typically use semicolon with quotes
        for row in _iter_csv(f, delimiter=";"):
            name = row.get("name")
            leads_s = row.get("leads")
            revenue_s = row.get("revenue")
            if not name:
                continue
            try:
                leads = int(leads_s) if leads_s not in (None, "") else None
            except Exception:
                leads = None
            try:
                revenue = float(revenue_s) if revenue_s not in (None, "") else None
            except Exception:
                revenue = None
            # Skip rows with non-positive revenue to match behavior
            if revenue is not None and revenue <= 0:
                continue
            db.add(
                BinomGoogleSpentData(
                    name=name,
                    leads=leads,
                    revenue=revenue,
                    date_from=date_from,
                    date_to=date_to,
                    report_type=report_type,
                    upload_id=upload.id,
                )
            )
            inserted += 1
    else:
        # Other sources to be implemented in Phase 3
        return jsonify({"status": "accepted", "source": source, "inserted": 0}), 202

    return jsonify({
        "status": "ok",
        "source": source,
        "upload_id": upload.id,
        "inserted": inserted,
        "date_from": str(date_from),
        "date_to": str(date_to),
        "report_type": report_type,
    })


@bp.get("/<source>/batches")
def list_batches(source: str):
    table = _validate_source(source)
    if not table:
        return jsonify({"error": "invalid source"}), 400

    db = g.db
    if source == "google":
        stmt = (
            select(
                GoogleData.date_from,
                GoogleData.date_to,
                GoogleData.report_type,
                func.count().label("count"),
            )
            .group_by(GoogleData.date_from, GoogleData.date_to, GoogleData.report_type)
            .order_by(GoogleData.date_from.desc())
            .limit(20)
        )
        rows = [
            {
                "date_from": str(r.date_from),
                "date_to": str(r.date_to),
                "report_type": r.report_type,
                "count": r.count,
            }
            for r in db.execute(stmt)
        ]
    elif source == "binom-google":
        stmt = (
            select(
                BinomGoogleSpentData.date_from,
                BinomGoogleSpentData.date_to,
                BinomGoogleSpentData.report_type,
                func.count().label("count"),
            )
            .group_by(
                BinomGoogleSpentData.date_from,
                BinomGoogleSpentData.date_to,
                BinomGoogleSpentData.report_type,
            )
            .order_by(BinomGoogleSpentData.date_from.desc())
            .limit(20)
        )
        rows = [
            {
                "date_from": str(r.date_from),
                "date_to": str(r.date_to),
                "report_type": r.report_type,
                "count": r.count,
            }
            for r in db.execute(stmt)
        ]
    else:
        # Future sources
        rows = []

    return jsonify({"source": source, "batches": rows})


@bp.delete("/<source>")
def delete_source_data(source: str):
    table = _validate_source(source)
    if not table:
        return jsonify({"error": "invalid source"}), 400
    report_type = request.args.get("report_type")
    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")

    db = g.db
    where = []
    if report_type:
        # applied per model below
        pass
    if source == "google":
        stmt = delete(GoogleData)
        if date_from:
            stmt = stmt.where(GoogleData.date_from == _parse_date(date_from))
        if date_to:
            stmt = stmt.where(GoogleData.date_to == _parse_date(date_to))
        if report_type:
            stmt = stmt.where(GoogleData.report_type == report_type)
        res = db.execute(stmt)
    elif source == "binom-google":
        stmt = delete(BinomGoogleSpentData)
        if date_from:
            stmt = stmt.where(BinomGoogleSpentData.date_from == _parse_date(date_from))
        if date_to:
            stmt = stmt.where(BinomGoogleSpentData.date_to == _parse_date(date_to))
        if report_type:
            stmt = stmt.where(BinomGoogleSpentData.report_type == report_type)
        res = db.execute(stmt)
    else:
        return jsonify({"status": "no_op", "source": source}), 200

    return jsonify({"status": "deleted", "rows": getattr(res, "rowcount", None)})
