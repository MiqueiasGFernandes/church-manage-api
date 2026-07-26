from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, Uuid, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class ChurchModel(Base):
    __tablename__ = "churches"
    __table_args__ = (
        UniqueConstraint("slug", name="uq_churches_slug"),
        UniqueConstraint("document", name="uq_churches_document"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    official_name: Mapped[str] = mapped_column(String(150))
    display_name: Mapped[str] = mapped_column(String(100))
    document: Mapped[str | None] = mapped_column(String(14))
    institutional_email: Mapped[str] = mapped_column(String(254))
    institutional_phone: Mapped[str] = mapped_column(String(16))
    website: Mapped[str | None] = mapped_column(String(2048))
    slug: Mapped[str] = mapped_column(String(60))
    timezone: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(40))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class UserModel(Base):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("email", name="uq_users_email"),)

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    name: Mapped[str] = mapped_column(String(150))
    email: Mapped[str] = mapped_column(String(254))
    phone: Mapped[str] = mapped_column(String(16))
    password_hash: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(40))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class AddressModel(Base):
    __tablename__ = "addresses"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    church_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("churches.id", ondelete="CASCADE"), index=True
    )
    postal_code: Mapped[str] = mapped_column(String(16))
    street: Mapped[str] = mapped_column(String(200))
    number: Mapped[str] = mapped_column(String(30))
    complement: Mapped[str | None] = mapped_column(String(100))
    district: Mapped[str] = mapped_column(String(100))
    city: Mapped[str] = mapped_column(String(100))
    state: Mapped[str] = mapped_column(String(50))
    country: Mapped[str] = mapped_column(String(2))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class CongregationModel(Base):
    __tablename__ = "congregations"
    __table_args__ = (UniqueConstraint("church_id", "name", name="uq_congregations_name"),)

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    church_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("churches.id", ondelete="CASCADE"), index=True
    )
    address_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("addresses.id", ondelete="RESTRICT"), unique=True
    )
    name: Mapped[str] = mapped_column(String(150))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class ChurchMembershipModel(Base):
    __tablename__ = "church_memberships"
    __table_args__ = (
        UniqueConstraint("church_id", "user_id", name="uq_church_memberships_church_user"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    church_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("churches.id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    role: Mapped[str] = mapped_column(String(50))
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class ChurchSettingsModel(Base):
    __tablename__ = "church_settings"

    church_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("churches.id", ondelete="CASCADE"), primary_key=True
    )
    locale: Mapped[str] = mapped_column(String(10))
    currency: Mapped[str] = mapped_column(String(3))
    timezone: Mapped[str] = mapped_column(String(64))
    date_format: Mapped[str] = mapped_column(String(20))
    country: Mapped[str] = mapped_column(String(2))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
