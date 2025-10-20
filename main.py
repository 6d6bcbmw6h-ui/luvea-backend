from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from typing import Optional
import os

app = FastAPI(title="LuvEA Cloud Runner")

class Account(BaseModel):
    server: str
    login: str
    password: str
    label: Optional[str] = None

@app.get("/")
def root():
    return {"msg": "Welcome to LuvEA Cloud Runner"}

@app.post("/accounts")
def create_account(acc: Account):
    # Qui in futuro connetteremo Azure agent
    return {"status": "Account saved", "server": acc.server, "login": acc.login}

@app.post("/bots/upload")
def upload_bot(file: UploadFile = File(...)):
    path = os.path.join("uploads", file.filename)
    os.makedirs("uploads", exist_ok=True)
    with open(path, "wb") as f:
        f.write(file.file.read())
    return {"uploaded": file.filename}
