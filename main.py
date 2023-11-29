import uvicorn
import logging
import logging.config

from fastapi import FastAPI, APIRouter
from fastapi_pagination import add_pagination
from sqladmin import Admin

from src.api.v1_handlers.auth import auth_router
from src.api.v1_handlers.role import role_router
from src.core.config import app_settings
from src.core.log_config import LOGGING
from database.session import engine

logging.config.dictConfig(LOGGING)
log = logging.getLogger("main")

app = FastAPI(title=app_settings.project_name)
admin = Admin(app, engine)
add_pagination(app)

main_router = APIRouter()

main_router.include_router(auth_router, tags=["Auth"])
main_router.include_router(role_router, tags=["Role"])

app.include_router(main_router)


if __name__ == "__main__":
    uvicorn.run("main:app",
                host="0.0.0.0",
                port=8000,
                reload=True,
                log_config=LOGGING,
                log_level=logging.getLevelName(app_settings.log_lvl))
