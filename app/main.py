from fastapi import FastAPI
from app.routes.health import router as health_router
from app.routes.pastes import router as pastes_router

app = FastAPI()

app.include_router(health_router)
app.include_router(pastes_router)

@app.get("/")
def home():
    return {"message": "Pastebin Lite API"}
