from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.exc import OperationalError
from sqlalchemy import text
from sqlalchemy.orm import Session
import redis

from app.database import db
from app.core.cache import redis_client
from app.api.public.flags import router as flags_router
from app.api.public.configs import router as configs_router
from app.api.admin.features import router as admin_features_router
from app.api.admin.configs import router as admin_configs_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/health")
async def health():
    return {"Status": "Healthy"}

@app.get("/health/redis")
async def health_redis():
    try:
        redis_client.ping()
        return {"Redis": "Healthy"}
    except redis.exceptions.ConnectionError:
        raise HTTPException(status_code=500, detail={
            "Redis": "Unhealthy",
            "Error": redis.exceptions.ConnectionError.__name__
        })

@app.get("/health/postgres")
def health_postgres(db: Session = Depends(db.get_db)):
    try:
        db.execute(text("SELECT 1"))
        db.close()
        return {"Postgres": "Healthy"}
    except OperationalError:
        raise HTTPException(status_code=500, detail={
            "Postgres": "Unhealthy",
            "Error": OperationalError.__name__
        })

app.include_router(flags_router)
app.include_router(configs_router)
app.include_router(admin_features_router)
app.include_router(admin_configs_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
