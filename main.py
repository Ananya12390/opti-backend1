from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from database import engine, Base, get_db
from routers import auth, users, assets, roles, stats
import seed


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create all tables then seed on first run
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    seed.seed_database(db)
    yield


app = FastAPI(
    title="VaultGuard API",
    description="Role-Based Access Control asset management system",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ─────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(assets.router)
app.include_router(roles.router)
app.include_router(stats.router)
