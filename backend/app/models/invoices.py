from __future__ import annotations

import datetime as dt
from typing import Optional

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    bill_to: Mapped[Optional[str]] = mapped_column(Text)
    invoice_date: Mapped[dt.date] = mapped_column(Date, index=True)
    invoice_number: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    total: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    items: Mapped[list["InvoiceItem"]] = relationship(
        back_populates="invoice", cascade="all, delete-orphan"
    )


class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    invoice_id: Mapped[int] = mapped_column(ForeignKey("invoices.id", ondelete="CASCADE"), index=True)
    item: Mapped[str] = mapped_column(String(255))
    quantity: Mapped[float] = mapped_column(Numeric(12, 2), default=1)
    rate: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    amount: Mapped[float] = mapped_column(Numeric(14, 2), default=0)

    invoice: Mapped[Invoice] = relationship(back_populates="items")


class InvoiceSequence(Base):
    __tablename__ = "invoice_sequences"

    year: Mapped[int] = mapped_column(Integer, primary_key=True)
    seq: Mapped[int] = mapped_column(Integer, nullable=False)
