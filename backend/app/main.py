from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from app.api.v1 import auth
from app.api.v1 import users
from app.api.v1 import departments
from app.api.v1 import permissions
app = FastAPI(title="PR System API", version="1.0.0")
Instrumentator(excluded_handlers=["/metrics"]).instrument(app).expose(app, include_in_schema=False)
app.include_router(auth.router, prefix="/api/v1")

app.include_router(users.router, prefix="/api/v1")
app.include_router(departments.router, prefix="/api/v1")
app.include_router(permissions.router, prefix="/api/v1")

# Разрешаем CORS для фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/v1/health")
async def health_check():
    return {"status": "ok"}