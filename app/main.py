from fastapi import FastAPI

from app.config.settings import get_settings
from app.contexts.identity.interfaces.api.routes import router as auth_router
from app.shared.body_limit import BodyLimitMiddleware


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(title=settings.app_name, debug=settings.debug)
    application.add_middleware(BodyLimitMiddleware)
    application.include_router(auth_router)

    @application.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return application


app = create_app()
