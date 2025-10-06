from __future__ import annotations

import datetime as dt
from typing import Optional

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Upload(Base):
    __tablename__ = "uploads"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_type: Mapped[str] = mapped_column(String(50), index=True)
    filename: Mapped[str] = mapped_column(String(255))
    checksum: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    uploaded_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), index=True)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class _BaseDataset:
    id: Mapped[int] = mapped_column(primary_key=True)
    date_from: Mapped[dt.date] = mapped_column(Date, index=True)
    date_to: Mapped[dt.date] = mapped_column(Date, index=True)
    report_type: Mapped[str] = mapped_column(String(16), index=True)
    upload_id: Mapped[int] = mapped_column(ForeignKey("uploads.id", ondelete="CASCADE"))
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class GoogleData(_BaseDataset, Base):
    __tablename__ = "google_data"

    account_name: Mapped[Optional[str]] = mapped_column(String(255))
    campaign: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    cost: Mapped[Optional[float]] = mapped_column(Numeric(14, 2))


class RumbleData(_BaseDataset, Base):
    __tablename__ = "rumble_data"

    campaign: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    spend: Mapped[Optional[float]] = mapped_column(Numeric(14, 2))
    cpm: Mapped[Optional[float]] = mapped_column(Numeric(14, 2))


class BinomRumbleSpentData(_BaseDataset, Base):
    __tablename__ = "binom_rumble_spent_data"

    name: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    leads: Mapped[Optional[int]] = mapped_column(Integer)
    revenue: Mapped[Optional[float]] = mapped_column(Numeric(14, 2))


class BinomGoogleSpentData(_BaseDataset, Base):
    __tablename__ = "binom_google_spent_data"

    name: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    leads: Mapped[Optional[int]] = mapped_column(Integer)
    revenue: Mapped[Optional[float]] = mapped_column(Numeric(14, 2))


class RumbleCampaignData(_BaseDataset, Base):
    __tablename__ = "rumble_campaign_data"

    name: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    cpm: Mapped[Optional[float]] = mapped_column(Numeric(14, 2))
    daily_limit: Mapped[Optional[float]] = mapped_column(Numeric(14, 2))
