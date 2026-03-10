from fastapi import FastAPI

from app.api.routes.auth import router as auth_router
from app.api.routes.notes import router as notes_router
from app.api.routes.pomodoro import router as pomodoro_router
from app.api.routes.study_sessions import router as study_sessions_router
from app.api.routes.subjects import router as subjects_router
from app.api.routes.tasks import router as tasks_router
from app.api.routes.users import router as users_router
from app.core.config.settings import settings


app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    version=settings.API_VERSION,
)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": f"{settings.APP_NAME} is alive"}


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(auth_router)
app.include_router(users_router)
app.include_router(subjects_router)
app.include_router(tasks_router)
app.include_router(study_sessions_router)
app.include_router(pomodoro_router)
app.include_router(notes_router)
