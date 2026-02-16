from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy import inspect

from app.core.database import Base, engine
from app.models import Lead, VisitedLink  # noqa: F401
from app.routers import dashboard_router, leads_router


def ensure_schema():
    inspector = inspect(engine)
    is_sqlite = engine.url.get_backend_name() == "sqlite"

    if is_sqlite and inspector.has_table("leads"):
        lead_columns = {column["name"] for column in inspector.get_columns("leads")}
        if "visited_link_id" not in lead_columns:
            # Hard-migration guard: legacy DBs are incompatible with the new schema.
            Base.metadata.drop_all(bind=engine)

    Base.metadata.create_all(bind=engine)


ensure_schema()

app = FastAPI(title="CareerOS")
app.mount("/static", StaticFiles(directory="app/ui/static"), name="static")

app.include_router(dashboard_router)
app.include_router(leads_router)
