from fastapi import FastAPI

from app.container import Container
from modules.organizations.application.use_cases.register_church import RegisterChurch
from modules.organizations.presentation.http import (
    HANDLED_ERRORS,
    get_register_church,
    registration_error_handler,
    router,
)


def create_app() -> FastAPI:
    container = Container()

    async def resolve_register_church() -> RegisterChurch:
        return container.register_church()

    application = FastAPI(title="Church Manage API", version="0.1.0")
    application.include_router(router)
    application.dependency_overrides[get_register_church] = resolve_register_church
    for error_type in HANDLED_ERRORS:
        application.add_exception_handler(error_type, registration_error_handler)
    return application


app = create_app()
