"""initial_schema

Revision ID: 20251006_140930
Revises: 
Create Date: 2025-10-06 14:09:30

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20251006_140930"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "uploads",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_type", sa.String(length=50), index=True, nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("checksum", sa.String(length=64), nullable=True),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    def dataset_columns():
        return [
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("date_from", sa.Date(), nullable=False),
            sa.Column("date_to", sa.Date(), nullable=False),
            sa.Column("report_type", sa.String(length=16), nullable=False),
            sa.Column("upload_id", sa.Integer(), sa.ForeignKey("uploads.id", ondelete="CASCADE"), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        ]

    # google_data
    op.create_table(
        "google_data",
        *dataset_columns(),
        sa.Column("account_name", sa.String(length=255)),
        sa.Column("campaign", sa.String(length=255)),
        sa.Column("cost", sa.Numeric(14, 2)),
    )
    op.create_index("ix_google_data_campaign", "google_data", ["campaign"])  # helpful join key
    op.create_index("ix_google_data_date", "google_data", ["date_from", "date_to", "report_type"])  # composite

    # rumble_data
    op.create_table(
        "rumble_data",
        *dataset_columns(),
        sa.Column("campaign", sa.String(length=255)),
        sa.Column("spend", sa.Numeric(14, 2)),
        sa.Column("cpm", sa.Numeric(14, 2)),
    )
    op.create_index("ix_rumble_data_campaign", "rumble_data", ["campaign"])  # helpful join key
    op.create_index("ix_rumble_data_date", "rumble_data", ["date_from", "date_to", "report_type"])  # composite

    # binom_rumble_spent_data
    op.create_table(
        "binom_rumble_spent_data",
        *dataset_columns(),
        sa.Column("name", sa.String(length=255)),
        sa.Column("leads", sa.Integer()),
        sa.Column("revenue", sa.Numeric(14, 2)),
    )
    op.create_index("ix_binom_rumble_spent_name", "binom_rumble_spent_data", ["name"])  # helpful join key
    op.create_index(
        "ix_binom_rumble_spent_date",
        "binom_rumble_spent_data",
        ["date_from", "date_to", "report_type"],
    )

    # binom_google_spent_data
    op.create_table(
        "binom_google_spent_data",
        *dataset_columns(),
        sa.Column("name", sa.String(length=255)),
        sa.Column("leads", sa.Integer()),
        sa.Column("revenue", sa.Numeric(14, 2)),
    )
    op.create_index("ix_binom_google_spent_name", "binom_google_spent_data", ["name"])  # helpful join key
    op.create_index(
        "ix_binom_google_spent_date",
        "binom_google_spent_data",
        ["date_from", "date_to", "report_type"],
    )

    # rumble_campaign_data
    op.create_table(
        "rumble_campaign_data",
        *dataset_columns(),
        sa.Column("name", sa.String(length=255)),
        sa.Column("cpm", sa.Numeric(14, 2)),
        sa.Column("daily_limit", sa.Numeric(14, 2)),
    )
    op.create_index("ix_rumble_campaign_name", "rumble_campaign_data", ["name"])  # helpful join key
    op.create_index(
        "ix_rumble_campaign_date",
        "rumble_campaign_data",
        ["date_from", "date_to", "report_type"],
    )

    # invoices
    op.create_table(
        "invoices",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("bill_to", sa.Text()),
        sa.Column("invoice_date", sa.Date(), nullable=False),
        sa.Column("invoice_number", sa.String(length=32), nullable=False, unique=True),
        sa.Column("notes", sa.Text()),
        sa.Column("total", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_invoices_invoice_date", "invoices", ["invoice_date"])  # queries

    op.create_table(
        "invoice_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("invoice_id", sa.Integer(), sa.ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False),
        sa.Column("item", sa.String(length=255), nullable=False),
        sa.Column("quantity", sa.Numeric(12, 2), nullable=False, server_default="1"),
        sa.Column("rate", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False, server_default="0"),
    )
    op.create_index("ix_invoice_items_invoice_id", "invoice_items", ["invoice_id"])  # fast lookup

    op.create_table(
        "invoice_sequences",
        sa.Column("year", sa.Integer(), primary_key=True),
        sa.Column("seq", sa.Integer(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("invoice_sequences")
    op.drop_index("ix_invoice_items_invoice_id", table_name="invoice_items")
    op.drop_table("invoice_items")
    op.drop_index("ix_invoices_invoice_date", table_name="invoices")
    op.drop_table("invoices")

    op.drop_index("ix_rumble_campaign_date", table_name="rumble_campaign_data")
    op.drop_index("ix_rumble_campaign_name", table_name="rumble_campaign_data")
    op.drop_table("rumble_campaign_data")

    op.drop_index("ix_binom_google_spent_date", table_name="binom_google_spent_data")
    op.drop_index("ix_binom_google_spent_name", table_name="binom_google_spent_data")
    op.drop_table("binom_google_spent_data")

    op.drop_index("ix_binom_rumble_spent_date", table_name="binom_rumble_spent_data")
    op.drop_index("ix_binom_rumble_spent_name", table_name="binom_rumble_spent_data")
    op.drop_table("binom_rumble_spent_data")

    op.drop_index("ix_rumble_data_date", table_name="rumble_data")
    op.drop_index("ix_rumble_data_campaign", table_name="rumble_data")
    op.drop_table("rumble_data")

    op.drop_index("ix_google_data_date", table_name="google_data")
    op.drop_index("ix_google_data_campaign", table_name="google_data")
    op.drop_table("google_data")

    op.drop_table("uploads")
