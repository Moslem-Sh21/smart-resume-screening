from fastapi import FastAPI

from apps.api.routers.health import router as health_router
from apps.api.routers.system import router as system_router
from resume_screening import __version__
from resume_screening.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=__version__,
    description=(
        "Human-in-the-loop platform for matching technical resumes "
        "to job descriptions and generating evidence-grounded fit explanations."
    ),
)

app.include_router(health_router)
app.include_router(system_router)


