from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from routers import auth, posts
from models.database import engine, Base

# FastAPI app
app = FastAPI()

@app.on_event("startup")
async def startup():
    FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")
    Base.metadata.create_all(bind=engine)  # Ensure tables are created

app.include_router(auth.router)
app.include_router(posts.router)
