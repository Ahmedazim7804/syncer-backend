from dependency_injector import containers, providers
from src.core.database import Database
from src.core.config import Config
from src.services import AuthService
from src.repository import AuthRepository


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "src.api.v1.endpoints.auth",
            "src.api.v1.endpoints.me",
        ]
    )

    db = providers.Singleton(Database, db_url=Config.DB_URL)

    auth_repository = providers.Factory(AuthRepository, db_factory=db.provided.session)

    auth_service = providers.Factory(AuthService, auth_repository=auth_repository)
