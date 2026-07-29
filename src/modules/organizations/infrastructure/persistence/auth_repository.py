from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.organizations.application.repositories.auth_repository import (
    EmailVerificationRecord,
    PasswordResetRecord,
    SecurityAuditEvent,
    SessionRecord,
)
from modules.organizations.domain.model import (
    ChurchId,
    ChurchMembership,
    ChurchRole,
    EmailAddress,
    MembershipId,
    MembershipStatus,
    PhoneNumber,
    User,
    UserId,
    UserStatus,
)
from modules.organizations.infrastructure.persistence.models import (
    ChurchMembershipModel,
    ConsumedRefreshTokenModel,
    EmailVerificationTokenModel,
    PasswordResetTokenModel,
    SecurityAuditEventModel,
    SessionModel,
    UserModel,
)


class SqlAlchemyAuthRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _user(model: UserModel) -> User:
        return User(
            UserId(model.id),
            model.name,
            EmailAddress(model.email),
            PhoneNumber(model.phone),
            model.password_hash,
            UserStatus(model.status),
            model.created_at,
            model.email_verified_at,
            model.last_login_at,
            model.password_changed_at,
        )

    @staticmethod
    def _membership(model: ChurchMembershipModel) -> ChurchMembership:
        return ChurchMembership(
            MembershipId(model.id),
            ChurchId(model.church_id),
            UserId(model.user_id),
            ChurchRole(model.role),
            model.joined_at,
            MembershipStatus(model.status),
        )

    async def find_user_by_email(self, email: EmailAddress) -> User | None:
        model = await self._session.scalar(select(UserModel).where(UserModel.email == email.value))
        return self._user(model) if model is not None else None

    async def find_user_by_id(self, user_id: UUID) -> User | None:
        model = await self._session.get(UserModel, user_id)
        return self._user(model) if model is not None else None

    async def save_user(self, user: User) -> None:
        model = await self._session.get(UserModel, user.id.value)
        assert model is not None
        model.password_hash = user.password_hash
        model.status, model.email_verified_at, model.last_login_at, model.password_changed_at = (
            user.status.value,
            user.email_verified_at,
            user.last_login_at,
            user.password_changed_at,
        )

    async def memberships_for_user(self, user_id: UUID) -> tuple[ChurchMembership, ...]:
        models = (
            await self._session.scalars(
                select(ChurchMembershipModel).where(ChurchMembershipModel.user_id == user_id)
            )
        ).all()
        return tuple(self._membership(model) for model in models)

    async def save_membership(self, membership: ChurchMembership) -> None:
        model = await self._session.get(ChurchMembershipModel, membership.id.value)
        assert model is not None
        model.status = membership.status.value

    async def add_email_verification(
        self, user_id: UUID, token_hash: str, expires_at: datetime
    ) -> None:
        self._session.add(
            EmailVerificationTokenModel(
                id=uuid4(), user_id=user_id, token_hash=token_hash, expires_at=expires_at
            )
        )

    async def _find_email_verification_model(
        self, token_hash: str
    ) -> EmailVerificationTokenModel | None:
        return await self._session.scalar(
            select(EmailVerificationTokenModel).where(
                EmailVerificationTokenModel.token_hash == token_hash
            )
        )

    async def find_email_verification(self, token_hash: str) -> EmailVerificationRecord | None:
        model = await self._find_email_verification_model(token_hash)
        if model is None:
            return None
        return EmailVerificationRecord(
            model.user_id, model.token_hash, model.expires_at, model.used_at
        )

    async def use_email_verification(self, token_hash: str, used_at: datetime) -> None:
        model = await self._find_email_verification_model(token_hash)
        assert model is not None
        model.used_at = used_at

    async def add_session(
        self,
        session_id: UUID,
        user_id: UUID,
        refresh_hash: str,
        created_at: datetime,
        expires_at: datetime,
    ) -> None:
        self._session.add(
            SessionModel(
                id=session_id,
                user_id=user_id,
                refresh_token_hash=refresh_hash,
                created_at=created_at,
                expires_at=expires_at,
            )
        )

    @staticmethod
    def _session_record(model: SessionModel) -> SessionRecord:
        return SessionRecord(
            model.id,
            model.user_id,
            model.refresh_token_hash,
            model.created_at,
            model.expires_at,
            model.revoked_at,
        )

    async def find_session_by_refresh(self, refresh_hash: str) -> SessionRecord | None:
        model = await self._session.scalar(
            select(SessionModel).where(SessionModel.refresh_token_hash == refresh_hash)
        )
        return self._session_record(model) if model is not None else None

    async def find_session_by_id(self, session_id: UUID) -> SessionRecord | None:
        model = await self._session.get(SessionModel, session_id)
        return self._session_record(model) if model is not None else None

    async def rotate_session(
        self, session_id: UUID, refresh_hash: str, expires_at: datetime
    ) -> None:
        model = await self._session.get(SessionModel, session_id)
        assert model is not None
        model.refresh_token_hash, model.expires_at = refresh_hash, expires_at

    async def revoke_session(self, session_id: UUID, revoked_at: datetime) -> None:
        model = await self._session.get(SessionModel, session_id)
        assert model is not None
        model.revoked_at = revoked_at

    async def add_consumed_refresh_token(
        self, session_id: UUID, token_hash: str, consumed_at: datetime
    ) -> None:
        self._session.add(
            ConsumedRefreshTokenModel(
                session_id=session_id, token_hash=token_hash, consumed_at=consumed_at
            )
        )

    async def find_session_id_by_consumed_refresh(self, token_hash: str) -> UUID | None:
        return await self._session.scalar(
            select(ConsumedRefreshTokenModel.session_id).where(
                ConsumedRefreshTokenModel.token_hash == token_hash
            )
        )

    async def add_audit_event(self, event: SecurityAuditEvent) -> None:
        self._session.add(
            SecurityAuditEventModel(
                id=uuid4(),
                event_type=event.event_type,
                occurred_at=event.occurred_at,
                actor_user_id=event.actor_user_id,
                target_user_id=event.target_user_id,
                church_id=event.church_id,
                session_id=event.session_id,
            )
        )

    async def sessions_for_user(self, user_id: UUID) -> tuple[SessionRecord, ...]:
        models = (
            await self._session.scalars(select(SessionModel).where(SessionModel.user_id == user_id))
        ).all()
        return tuple(self._session_record(model) for model in models)

    async def invalidate_email_verifications(self, user_id: UUID, invalidated_at: datetime) -> None:
        models = (
            await self._session.scalars(
                select(EmailVerificationTokenModel).where(
                    EmailVerificationTokenModel.user_id == user_id,
                    EmailVerificationTokenModel.used_at.is_(None),
                )
            )
        ).all()
        for model in models:
            model.used_at = invalidated_at

    async def add_password_reset(
        self, user_id: UUID, token_hash: str, expires_at: datetime
    ) -> None:
        self._session.add(
            PasswordResetTokenModel(
                id=uuid4(), user_id=user_id, token_hash=token_hash, expires_at=expires_at
            )
        )

    async def _find_password_reset_model(self, token_hash: str) -> PasswordResetTokenModel | None:
        return await self._session.scalar(
            select(PasswordResetTokenModel).where(PasswordResetTokenModel.token_hash == token_hash)
        )

    async def find_password_reset(self, token_hash: str) -> PasswordResetRecord | None:
        model = await self._find_password_reset_model(token_hash)
        if model is None:
            return None
        return PasswordResetRecord(model.user_id, model.token_hash, model.expires_at, model.used_at)

    async def use_password_reset(self, token_hash: str, used_at: datetime) -> None:
        model = await self._find_password_reset_model(token_hash)
        assert model is not None
        model.used_at = used_at
