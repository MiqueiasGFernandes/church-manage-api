from dependency_injector import containers, providers

from modules.organizations.application.use_cases.register_church import RegisterChurch
from modules.organizations.infrastructure.in_memory import (
    Argon2Hasher,
    InMemoryRegistrationRepository,
    InMemoryUnitOfWork,
    SystemClock,
    UuidGenerator,
)
from modules.organizations.infrastructure.persistence.database import PostgresDatabase
from modules.organizations.infrastructure.persistence.registration_repository import (
    SqlAlchemyRegistrationRepository,
)
from modules.organizations.infrastructure.persistence.unit_of_work import SqlAlchemyUnitOfWork


def build_postgres_register_church(
    database: PostgresDatabase,
    password_hasher: Argon2Hasher,
    id_generator: UuidGenerator,
    clock: SystemClock,
) -> RegisterChurch:
    session = database.create_session()
    repository = SqlAlchemyRegistrationRepository(session)
    return RegisterChurch(
        repository=repository,
        unit_of_work=SqlAlchemyUnitOfWork(session),
        password_hasher=password_hasher,
        id_generator=id_generator,
        clock=clock,
    )


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    config.persistence_backend.from_value("memory")
    config.database_url.from_value("")

    repository = providers.Singleton(InMemoryRegistrationRepository)
    unit_of_work = providers.Factory(InMemoryUnitOfWork, repository=repository)
    password_hasher = providers.Singleton(Argon2Hasher)
    id_generator = providers.Singleton(UuidGenerator)
    clock = providers.Singleton(SystemClock)
    in_memory_register_church = providers.Factory(
        RegisterChurch,
        repository=repository,
        unit_of_work=unit_of_work,
        password_hasher=password_hasher,
        id_generator=id_generator,
        clock=clock,
    )
    database = providers.Singleton(PostgresDatabase, database_url=config.database_url)
    postgres_register_church = providers.Factory(
        build_postgres_register_church,
        database=database,
        password_hasher=password_hasher,
        id_generator=id_generator,
        clock=clock,
    )
    register_church = providers.Selector(
        config.persistence_backend,
        memory=in_memory_register_church,
        postgresql=postgres_register_church,
    )
