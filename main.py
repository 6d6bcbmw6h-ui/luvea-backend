from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse
import os, requests

app = FastAPI(title="LuvEA Backend Minimal")

# --- SETTINGS ---
RUNNER_URL = "https://luvea-runner.onrender.com"
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- LOGIN PAGE ---
@app.get("/", response_class=HTMLResponse)
def index():
    return """
    <h2>🧠 LuvEA Cloud Login</h2>
    <form action="/login" method="post">
        <input name="server" placeholder="MT4 Server"><br>
        <input name="login" placeholder="Account Number"><br>
        <input name="password" placeholder="Password" type="password"><br>
        <button type="submit">Access</button>
    </form>
    """

# --- LOGIN HANDLER ---
@app.post("/login")
def login(server: str = Form(...), login: str = Form(...), password: str = Form(...)):
    html = f"""
    <h3>✅ Connected to {server}</h3>
    <p>Account: {login}</p><hr>

    <form action="/upload-ea/" enctype="multipart/form-data" method="post">
        <input type="file" name="file"><br>
        <button type="submit">Upload EA</button>
    </form><hr>

    <form action="/start" method="post"><button>▶️ Start EA</button></form>
    <form action="/stop" method="post"><button>⏹ Stop EA</button></form>
    """
    return HTMLResponse(html)

# --- UPLOAD EA ---
@app.post("/upload-ea/", response_class=HTMLResponse)
async def upload_ea(file: UploadFile = File(...)):
    path = os.path.join(UPLOAD_DIR, file.filename)
    with open(path, "wb") as f:
        f.write(await file.read())
    return f"<p>✅ Uploaded: {file.filename}</p><a href='/'>⬅️ Back</a>"

# --- START EA ---
@app.post("/start")
def start_ea():
    try:
        r = requests.post(f"{RUNNER_URL}/start")
        try:
            data = r.json()
        except:
            data = r.text or "Runner did not return JSON"
        return HTMLResponse(f"<p>▶️ {data}</p><a href='/'>⬅️ Back</a>")
    except Exception as e:
        return HTMLResponse(f"<p>❌ Error contacting runner: {e}</p><a href='/'>⬅️ Back</a>")

# --- STOP EA ---
@app.post("/stop")
def stop_ea():
    try:
        r = requests.post(f"{RUNNER_URL}/stop")
        try:
            data = r.json()
        except:
            data = r.text or "Runner did not return JSON"
        return HTMLResponse(f"<p>⏹ {data}</p><a href='/'>⬅️ Back</a>")
    except Exception as e:
        return HTMLResponse(f"<p>❌ Error contacting runner: {e}</p><a href='/'>⬅️ Back</a>")


# ========== LuvEA Runner Uploader ==========
from fastapi import UploadFile, File
import requests

# URL del tuo runner Gitpod (verifica che sia quello corretto)
RUNNER_URL = "https://5000-019a0278-f0c0-7b4a-a077-b50c65ea7c58.eu-central-1-01.gitpod.dev/upload-ea"

@app.post("/api/upload-ea")
async def upload_ea(file: UploadFile = File(...)):
    try:
        files = {"file": (file.filename, await file.read(), file.content_type)}
        r = requests.post(RUNNER_URL, files=files)
        return r.json()
    except Exception as e:
        return {"error": str(e)}



@app.post("/api/login")
async def login(data: dict):
    server = data.get("server")
    account = data.get("account")
    password = data.get("password")

    # qui puoi collegare al runner o solo loggare per test
    print(f"MT4 login attempt → Server: {server}, Account: {account}")
    
    return {"status": "ok", "server": server, "account": account}
