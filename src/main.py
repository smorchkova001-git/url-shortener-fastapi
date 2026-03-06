from fastapi import FastAPI
from src.auth.users import auth_backend, fastapi_users
from src.auth.schemas import UserCreate, UserRead
from src.core.database import engine
from src.auth.db import Base as AuthBase
from src.links.router import router as links_router
from src.links.redirect import router as redirect_router
from src.links.models import Link
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from src.core.cache import init_cache
from fastapi_cache import FastAPICache

@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    await init_cache()
    yield
    await FastAPICache.clear()

app = FastAPI(title="URL Shortener", lifespan=lifespan)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

@app.get("/")
async def root():
    return {"message": "URL Shortener API"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/setup-db")
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(AuthBase.metadata.create_all)
    return {"message": "Tables created successfully"}

app.include_router(redirect_router) 
app.include_router(links_router, prefix="/links")