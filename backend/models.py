from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


def utc_now():
    return datetime.now(timezone.utc)


class Claim(Base):
    __tablename__ = "claims"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    original_text: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_text: Mapped[str] = mapped_column(Text, nullable=False)
    subject: Mapped[str | None] = mapped_column(Text, nullable=True)
    event: Mapped[str | None] = mapped_column(Text, nullable=True)
    location: Mapped[str | None] = mapped_column(Text, nullable=True)
    claim_date: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    evidence = relationship(
        "Evidence",
        back_populates="claim",
        cascade="all, delete-orphan",
    )

    verifications = relationship(
        "Verification",
        back_populates="claim",
        cascade="all, delete-orphan",
    )


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    url: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    domain: Mapped[str | None] = mapped_column(String(255), nullable=True)
    publisher: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    author: Mapped[str | None] = mapped_column(String(255), nullable=True)
    publication_date: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    discovered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    evidence = relationship(
        "Evidence",
        back_populates="source",
        cascade="all, delete-orphan",
    )


class Evidence(Base):
    __tablename__ = "evidence"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    claim_id: Mapped[int] = mapped_column(
        ForeignKey("claims.id"),
        nullable=False,
        index=True,
    )
    source_id: Mapped[int] = mapped_column(
        ForeignKey("sources.id"),
        nullable=False,
        index=True,
    )
    evidence_text: Mapped[str] = mapped_column(Text, nullable=False)
    relationship: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    relevance: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    claim = relationship(
        "Claim",
        back_populates="evidence",
    )

    source = relationship(
        "Source",
        back_populates="evidence",
    )


class Verification(Base):
    __tablename__ = "verifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    claim_id: Mapped[int] = mapped_column(
        ForeignKey("claims.id"),
        nullable=False,
        index=True,
    )
    verdict: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    confidence: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    verified_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    claim = relationship(
        "Claim",
        back_populates="verifications",
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    identifier: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )


class Usage(Base):
    __tablename__ = "usage"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_identifier: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    usage_date: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        index=True,
    )
    verification_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
