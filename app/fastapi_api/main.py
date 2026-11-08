from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.fastapi_api.routers import compress, decompress, tasks

app = FastAPI(title="Zhi-Zip Web API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(compress.router)
app.include_router(decompress.router)
app.include_router(tasks.router)


@app.get("/")
async def root():
    return {"service": "zhi-zip-api", "docs": "/docs"}
