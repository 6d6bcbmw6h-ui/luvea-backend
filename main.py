# =====================================================
# 🧠 LuvEA Backend (Final Linked Version)
# =====================================================
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse
import os, requests, shutil

app = FastAPI(title="LuvEA Backend - Linked to Gitpod Runner")

# --- CONFIGURATION ---
RUNNER_URL = "https://3000--019a0278-f0c0-7b4a-a077-b50c65ea7c58.eu-central-1-01.gitpod.dev"
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# =====================================================
# 🧠 ROUTES
# =====================================================

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


# =====================================================
# 📂 EA UPLOAD
# =====================================================
@app.post("/upload-ea/", response_class=HTMLResponse)
async def upload_ea(file: UploadFile = File(...)):
    try:
        path = os.path.join(UPLOAD_DIR, file.filename)
        with open(path, "wb") as f:
            f.write(await file.read())
        return f"<p>✅ Uploaded: {file.filename}</p><a href='/'>⬅️ Back</a>"
    except Exception as e:
        return HTMLResponse(f"<p>❌ Upload failed: {e}</p><a href='/'>⬅️ Back</a>")


# =====================================================
# ▶️ START EA
# =====================================================
@app.post("/start")
def start_ea():
    try:
        response = requests.post(f"{RUNNER_URL}/start", timeout=10)
        return {
            "status": "started ✅",
            "runner_url": RUNNER_URL,
            "response": response.text
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


# =====================================================
# ⏹ STOP EA
# =====================================================
@app.post("/stop")
def stop_ea():
    try:
        response = requests.post(f"{RUNNER_URL}/stop", timeout=10)
        return {
            "status": "stopped ✅",
            "runner_url": RUNNER_URL,
            "response": response.text
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
