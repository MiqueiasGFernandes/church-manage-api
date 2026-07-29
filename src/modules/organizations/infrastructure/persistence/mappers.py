from uuid import uuid4

from modules.organizations.domain.model import (
    Church,
    ChurchMembership,
    ChurchSettings,
    Congregation,
    User,
)
from modules.organizations.infrastructure.persistence.models import (
    AddressModel,
    ChurchMembershipModel,
    ChurchModel,
    ChurchSettingsModel,
    CongregationModel,
    UserModel,
)


class RegistrationMapper:
    @staticmethod
    def church_to_model(church: Church) -> ChurchModel:
        return ChurchModel(
            id=church.id.value,
            official_name=church.official_name.value,
            display_name=church.display_name.value,
            document=church.document.value if church.document is not None else None,
            institutional_email=church.institutional_email.value,
            institutional_phone=church.institutional_phone.value,
            website=church.website,
            slug=church.slug.value,
            timezone=church.timezone.value,
            status=church.status.value,
            created_at=church.created_at,
        )

    @staticmethod
    def user_to_model(user: User) -> UserModel:
        return UserModel(
            id=user.id.value,
            name=user.name,
            email=user.email.value,
            phone=user.phone.value,
            password_hash=user.password_hash,
            status=user.status.value,
            created_at=user.created_at,
            email_verified_at=user.email_verified_at,
            last_login_at=user.last_login_at,
            password_changed_at=user.password_changed_at,
        )

    @staticmethod
    def congregation_to_models(
        congregation: Congregation,
    ) -> tuple[AddressModel, CongregationModel]:
        address_id = uuid4()
        address = congregation.address
        address_model = AddressModel(
            id=address_id,
            church_id=congregation.church_id.value,
            postal_code=address.postal_code,
            street=address.street,
            number=address.number,
            complement=address.complement,
            district=address.district,
            city=address.city,
            state=address.state,
            country=address.country,
        )
        congregation_model = CongregationModel(
            id=congregation.id.value,
            church_id=congregation.church_id.value,
            address_id=address_id,
            name=congregation.name,
            created_at=congregation.created_at,
        )
        return address_model, congregation_model

    @staticmethod
    def membership_to_model(membership: ChurchMembership) -> ChurchMembershipModel:
        return ChurchMembershipModel(
            id=membership.id.value,
            church_id=membership.church_id.value,
            user_id=membership.user_id.value,
            role=membership.role.value,
            status=membership.status.value,
            joined_at=membership.joined_at,
        )

    @staticmethod
    def settings_to_model(settings: ChurchSettings) -> ChurchSettingsModel:
        return ChurchSettingsModel(
            church_id=settings.church_id.value,
            locale=settings.locale,
            currency=settings.currency,
            timezone=settings.timezone.value,
            date_format=settings.date_format,
            country=settings.country,
        )
