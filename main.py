import uvicorn
import logging
import logging.config

from fastapi import FastAPI, APIRouter
from fastapi_pagination import add_pagination
from sqladmin import Admin

from src.resume.handlers import resume_router
from src.vacansy.handlers import vacansy_router
from src.users.router import users_roter
from src.core.config import app_settings
from core.log_config import LOGGING
from database.session import engine


app = FastAPI(title=app_settings.project_name)
admin = Admin(app, engine)
add_pagination(app)

main_router = APIRouter()

main_router.include_router(users_roter)
main_router.include_router(resume_router, prefix="/resume", tags=["resume"])
main_router.include_router(vacansy_router, prefix="/vacansy", tags=["vacansy"])
app.include_router(main_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
