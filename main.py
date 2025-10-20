# =====================================================
# 🧠 LuvEA Backend - Self-Healing Version (2025 Final)
# =====================================================
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse
import os, requests, shutil, subprocess

app = FastAPI(title="LuvEA Backend Autonomous")

# --- CONFIG ---
WORKSPACE_FILE = "/workspace/runner_url.txt"
STATIC_FALLBACK_URL = "https://3000--019a0278-f0c0-7b4a-a077-b50c65ea7c58.eu-central-1-01.gitpod.dev"
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# =====================================================
# 🧠 AUTO-DETECT FUNCTION
# =====================================================
def get_runner_url():
    """
    Try to read /workspace/runner_url.txt.
    If missing, auto-detect Gitpod URL via gp CLI or fallback.
    """
    try:
        if os.path.exists(WORKSPACE_FILE):
            with open(WORKSPACE_FILE, "r") as f:
                url = f.read().strip()
                if url:
                    return url
        # Try Gitpod CLI if available
        try:
            url = subprocess.getoutput("gp url 3000").strip()
            if url.startswith("https://"):
                os.makedirs(os.path.dirname(WORKSPACE_FILE), exist_ok=True)
                with open(WORKSPACE_FILE, "w") as f:
                    f.write(url)
                return url
        except Exception:
            pass
        # Fallback if everything else fails
        return STATIC_FALLBACK_URL
    except Exception as e:
        return STATIC_FALLBACK_URL


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


@app.post("/start")
def start_ea():
    try:
        runner_url = get_runner_url()
        if not runner_url:
            raise Exception("Could not resolve runner URL")
        # ping + start
        requests.get(runner_url + "/", timeout=5)
        r = requests.post(runner_url + "/start", timeout=10)
        return {
            "status": "started ✅",
            "runner_url": runner_url,
            "response": r.text
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/stop")
def stop_ea():
    try:
        runner_url = get_runner_url()
        r = requests.post(runner_url + "/stop", timeout=5)
        return {"status": "stopped ✅", "response": r.text}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/upload-ea/", response_class=HTMLResponse)
async def upload_ea(file: UploadFile = File(...)):
    path = os.path.join(UPLOAD_DIR, file.filename)
    with open(path, "wb") as f:
        f.write(await file.read())
    return f"<p>✅ Uploaded: {file.filename}</p><a href='/'>⬅️ Back</a>"
