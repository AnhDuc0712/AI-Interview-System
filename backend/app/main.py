from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.error_handlers import register_exception_handlers
from app.middleware.auth import AuthenticationContextMiddleware
from app.services.cv_ingestion import get_cv_ingestion_service
from app.services.user_sync import get_user_sync_service


@asynccontextmanager
async def lifespan(_: FastAPI):
    await get_user_sync_service().ensure_indexes()
    await get_cv_ingestion_service().ensure_ready()
    yield


app = FastAPI(title=settings.app_name, version='0.1.0', lifespan=lifespan)
origins = [
    "http://localhost:4173",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://192.168.1.41:4173",
    "http://172.16.18.171:4173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AuthenticationContextMiddleware)
register_exception_handlers(app)

app.include_router(api_router, prefix='/api/v1')


@app.get('/health')
async def root():
    return {'status': 'ok'}
