from __future__ import annotations

import csv
import datetime as dt
from io import TextIOWrapper
import re
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
    """Yield normalized CSV rows.

    Supports files with leading title/date lines (e.g., Google weekly exports) by
    skipping to the first delimited header line before constructing the reader.
    """
    text = TextIOWrapper(file_storage.stream, encoding="utf-8", errors="replace")
    content = text.read()
    lines = content.splitlines()

    # Determine delimiter if not provided
    if delimiter is None:
        sample = "\n".join(lines[:50])
        try:
            sniffed = csv.Sniffer().sniff(sample, delimiters=",;\t")
            delimiter = sniffed.delimiter
        except Exception:
            delimiter = ","

    # Find first plausible header line with the chosen delimiter
    header_idx = None
    for i, l in enumerate(lines):
        if delimiter in l:
            # quick heuristic: at least 2 columns
            try:
                cols = next(csv.reader([l], delimiter=delimiter))
            except Exception:
                continue
            if len(cols) >= 2:
                header_idx = i
                break
    if header_idx is None:
        # No header found; return empty iterator
        return []

    sliced = "\n".join(lines[header_idx:])
    reader = csv.DictReader(sliced.splitlines(), delimiter=delimiter)
    reader.fieldnames = [
        _normalize_header(h) for h in (reader.fieldnames or [])
    ]
    for row in reader:
        yield {k: (v.strip() if isinstance(v, str) else v) for k, v in row.items()}


_CURRENCY_RE = re.compile(r"[\s,\u00A0]")

def _parse_float(val: str | None) -> float | None:
    if val is None:
        return None
    if isinstance(val, (int, float)):
        try:
            return float(val)
        except Exception:
            return None
    s = str(val).strip()
    if not s:
        return None
    # Handle negatives in parentheses: (123.45) => -123.45
    negative = s.startswith("(") and s.endswith(")")
    if negative:
        s = s[1:-1]
    # Remove currency symbols and thousand separators
    s = s.replace("$", "").replace("€", "").replace("£", "")
    s = _CURRENCY_RE.sub("", s)
    # Remove trailing currency codes
    for code in ("USD", "EUR", "GBP", "usd", "eur", "gbp"):
        if s.endswith(code):
            s = s[: -len(code)].strip()
    try:
        num = float(s)
        return -num if negative else num
    except Exception:
        return None


def _parse_int(val: str | None) -> int | None:
    if val is None:
        return None
    if isinstance(val, (int, float)):
        try:
            return int(val)
        except Exception:
            return None
    s = str(val).strip()
    if not s:
        return None
    # Remove thousand separators and any currency-like residue
    s = _CURRENCY_RE.sub("", s)
    try:
        return int(s)
    except Exception:
        return None


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
            # Try multiple header variants
            account = (
                row.get("account")
                or row.get("account_name")
                or row.get("account_descriptive_name")
            )
            campaign = row.get("campaign") or row.get("campaign_name")
            if not campaign:
                for k in row.keys():
                    if "campaign" in k:
                        campaign = row.get(k)
                        break
            # Cost may appear as cost_(usd) or similar
            cost_s = row.get("cost")
            if cost_s is None:
                for k in row.keys():
                    if "cost" in k:
                        cost_s = row.get(k)
                        break
            if not campaign:
                continue
            cost = _parse_float(cost_s)
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
            leads = _parse_int(leads_s)
            revenue = _parse_float(revenue_s)
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

    if inserted == 0:
        # Provide a helpful error explaining likely header mismatch
        return (
            jsonify(
                {
                    "error": "no rows inserted; check CSV headers match expected fields",
                    "expected": {
                        "google": ["campaign", "cost"],
                        "binom-google": ["name", "revenue"],
                    }.get(source, []),
                    "status": "no_rows",
                    "source": source,
                }
            ),
            400,
        )

    return jsonify(
        {
            "status": "ok",
            "source": source,
            "upload_id": upload.id,
            "inserted": inserted,
            "date_from": str(date_from),
            "date_to": str(date_to),
            "report_type": report_type,
        }
    )


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
                func.count().label("row_count"),
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
                "count": r.row_count,
            }
            for r in db.execute(stmt)
        ]
    elif source == "binom-google":
        stmt = (
            select(
                BinomGoogleSpentData.date_from,
                BinomGoogleSpentData.date_to,
                BinomGoogleSpentData.report_type,
                func.count().label("row_count"),
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
                "count": r.row_count,
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
