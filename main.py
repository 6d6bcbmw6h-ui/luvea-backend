from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse
import os, requests, shutil

app = FastAPI(title="LuvEA Backend Cloud")

# --- SETTINGS ---
RUNNER_BASE = "https://5000-019a0278-f0c0-7b4a-a077-b50c65ea7c58.eu-central-1-01.gitpod.dev"
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

    <form action="/api/upload-ea" enctype="multipart/form-data" method="post">
        <input type="file" name="file"><br>
        <button type="submit">Upload EA</button>
    </form><hr>

    <form action="/api/start" method="post"><button>▶️ Start EA</button></form>
    <form action="/api/stop" method="post"><button>⏹ Stop EA</button></form>
    """
    return HTMLResponse(html)

# --- CONNECT MT4 (API) ---
@app.post("/api/connect-mt4")
async def api_connect(data: dict):
    r = requests.post(f"{RUNNER_BASE}/connect-mt4", json=data)
    return r.json()

# --- UPLOAD EA (dal sito al runner) ---
@app.post("/api/upload-ea")
async def upload_ea_backend(file: UploadFile = File(...)):
    try:
        files = {"file": (file.filename, await file.read(), file.content_type)}
        r = requests.post(f"{RUNNER_BASE}/upload-ea", files=files)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

# --- START EA ---
@app.post("/api/start")
def start_ea():
    try:
        r = requests.post(f"{RUNNER_BASE}/start")
        return {"status": "started", "response": r.text}
    except Exception as e:
        return {"error": str(e)}

# --- STOP EA ---
@app.post("/api/stop")
def stop_ea():
    try:
        r = requests.post(f"{RUNNER_BASE}/stop")
        return {"status": "stopped", "response": r.text}
    except Exception as e:
        return {"error": str(e)}

# --- TEST PAGE (optional) ---
@app.get("/test", response_class=HTMLResponse)
def test_page():
    return "<h3>✅ LuvEA Backend online</h3><p>Ready to link with MT4 runner</p>"
