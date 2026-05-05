from fastapi import FastAPI

from .api.routes_report import router as report_router
from .api.routes_scan import router as scan_router
from .database import Base, engine
from .schemas import HealthResponse

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Smart Audit AI")
app.include_router(scan_router)
app.include_router(report_router)


@app.get('/health', response_model=HealthResponse)
def healthcheck():
    return HealthResponse(status='ok')
