mode =  ['ai_mode','manual_mode','hybrid_mode']
default_mode = mode[0]
#hybrid logic later
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from slowapi import _rate_limit_exceeded_handler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import init_db
from routers import spots, auth
from routers.auth import limiter

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()  # creates the users table on first run
    yield

app = FastAPI(title="RoamDelhiNCR API", lifespan=lifespan)
app.state.limiter =limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(spots.router)
app.include_router(auth.router)


@app.get("/")
def root():
    return {"status": "ok"}
