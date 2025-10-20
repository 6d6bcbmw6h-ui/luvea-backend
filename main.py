from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse
import os, requests, shutil

app = FastAPI(title="LuvEA Backend Minimal")

# --- SETTINGS ---
# ✅ Runner attivo su Gitpod (porta 3000)
RUNNER_URL = "https://3000-019a0278-f0c0-7b4a-a077-b50c65ea7c58.eu-central-1-01.gitpod.dev"
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

# --- UPLOAD EA (local) ---
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
@app.post("/api/upload-ea")
async def upload_ea_api(file: UploadFile = File(...)):
    try:
        files = {"file": (file.filename, await file.read(), file.content_type)}
        r = requests.post(f"{RUNNER_URL}/upload-ea", files=files)
        return r.json()
    except Exception as e:
        return {"error": str(e)}


# --- Connect MT4 directly from backend ---
@app.post("/api/connect-mt4")
async def api_connect(data: dict):
    try:
        r = requests.post(f"{RUNNER_URL}/connect-mt4", json=data)
        return r.json()
    except Exception as e:
        return {"error": str(e)}
