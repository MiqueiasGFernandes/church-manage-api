from dependency_injector import containers, providers

from modules.organizations.application.use_cases.register_church import RegisterChurch
from modules.organizations.infrastructure.in_memory import (
    Argon2Hasher,
    InMemoryEventPublisher,
    InMemoryRegistrationRepository,
    InMemoryUnitOfWork,
    SystemClock,
    UuidGenerator,
)


class Container(containers.DeclarativeContainer):
    repository = providers.Singleton(InMemoryRegistrationRepository)
    unit_of_work = providers.Factory(InMemoryUnitOfWork, repository=repository)
    password_hasher = providers.Singleton(Argon2Hasher)
    id_generator = providers.Singleton(UuidGenerator)
    clock = providers.Singleton(SystemClock)
    event_publisher = providers.Singleton(InMemoryEventPublisher)
    register_church = providers.Factory(
        RegisterChurch,
        repository=repository,
        unit_of_work=unit_of_work,
        password_hasher=password_hasher,
        id_generator=id_generator,
        clock=clock,
        event_publisher=event_publisher,
    )
