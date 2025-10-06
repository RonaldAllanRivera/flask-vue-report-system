from flask import Blueprint, jsonify, request

bp = Blueprint("invoices", __name__)


@bp.get("/invoices")
def list_invoices():
    # NOTE: Stub – return empty list
    return jsonify({"items": [], "total": 0})


@bp.post("/invoices")
def create_invoice():
    payload = request.get_json(silent=True) or {}
    # NOTE: Stub – would validate and persist
    return jsonify({"id": 1, **payload}), 201


@bp.get("/invoices/<int:invoice_id>")
def get_invoice(invoice_id: int):
    # NOTE: Stub – not found placeholder
    return jsonify({"id": invoice_id, "items": [], "total": 0}), 200


@bp.put("/invoices/<int:invoice_id>")
@bp.patch("/invoices/<int:invoice_id>")
def update_invoice(invoice_id: int):
    payload = request.get_json(silent=True) or {}
    # NOTE: Stub – would validate and update
    return jsonify({"id": invoice_id, **payload}), 200


@bp.delete("/invoices/<int:invoice_id>")
def delete_invoice(invoice_id: int):
    # NOTE: Stub – would delete
    return jsonify({"status": "deleted", "id": invoice_id}), 200


@bp.get("/invoices/<int:invoice_id>/pdf")
def get_invoice_pdf(invoice_id: int):
    # NOTE: Stub – will stream PDF later
    return jsonify({"status": "not_implemented", "id": invoice_id}), 501
