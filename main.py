from fastapi import FastAPI
from database import engine
import models
import routers

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(routers.router)


@app.get("/")
def home():
    return {"message": "User Management System API."}
