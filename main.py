import uvicorn
from fastapi import FastAPI, APIRouter

from users.handlers import users_roter, resume_router, vacansy_router

app = FastAPI(title="Поиск работы")

main_router = APIRouter()

main_router.include_router(users_roter)
main_router.include_router(resume_router, prefix="/resume", tags=["resume"])
main_router.include_router(vacansy_router, prefix="/vacansy", tags=["vacansy"])
app.include_router(main_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

