# =====================================================
# 🧠 LuvEA Backend - FastAPI bridge to Gitpod Runner
# =====================================================
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse
import os, requests, shutil

app = FastAPI(title="LuvEA Backend Minimal")

# --- SETTINGS ---
RUNNER_FILE_PATH = "/workspace/runner_url.txt"  # where Gitpod saves the URL
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


# =====================================================
#  🔁 UNIVERSAL /start ENDPOINT - AUTO CONNECT TO GITPOD
# =====================================================
@app.post("/start")
def start_ea():
    try:
        # Read runner URL from file written by Gitpod
        if not os.path.exists(RUNNER_FILE_PATH):
            raise Exception("runner_url.txt not found — run ./runner_boot.sh in Gitpod first.")

        with open(RUNNER_FILE_PATH, "r") as f:
            runner_url = f.read().strip()

        if not runner_url:
            raise Exception("runner_url.txt is empty")

        # Verify runner is reachable
        ping = requests.get(f"{runner_url}/", timeout=5)
        if ping.status_code != 200:
            raise Exception(f"Runner not responding: {ping.status_code}")

        # Start EA on runner
        r = requests.post(f"{runner_url}/start", timeout=10)
        return {
            "status": "started ✅",
            "runner_url": runner_url,
            "response": r.text
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


# --- STOP EA ---
@app.post("/stop")
def stop_ea():
    try:
        with open(RUNNER_FILE_PATH, "r") as f:
            runner_url = f.read().strip()
        r = requests.post(f"{runner_url}/stop", timeout=5)
        return {"status": "stopped ✅", "response": r.text}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# --- UPLOAD EA ---
@app.post("/upload-ea/", response_class=HTMLResponse)
async def upload_ea(file: UploadFile = File(...)):
    path = os.path.join(UPLOAD_DIR, file.filename)
    with open(path, "wb") as f:
        f.write(await file.read())
    return f"<p>✅ Uploaded: {file.filename}</p><a href='/'>⬅️ Back</a>"
