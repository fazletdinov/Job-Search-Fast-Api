import uvicorn
import logging.config

from fastapi import FastAPI, APIRouter
from fastapi_pagination import add_pagination

from src.api.v1_handlers.auth import auth_router
from src.api.v1_handlers.role import role_router
from src.core.config import settings
from src.core.log_config import LOGGING

logging.config.dictConfig(LOGGING)
log = logging.getLogger("main")

app = FastAPI(title=settings.app.project_name)

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
                log_level=logging.getLevelName(settings.app.log_lvl))
