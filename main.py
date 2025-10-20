from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import os, json, requests

app = FastAPI(title="LuvEA Cloud Backend")

# cartelle
os.makedirs("uploads", exist_ok=True)
os.makedirs("externs", exist_ok=True)

# ---- MODELLI DATI ----
class MT4Login(BaseModel):
    server: str
    login: str
    password: str

class ExternParams(BaseModel):
    ea_name: str
    params: dict

# ---- VARIABILI GLOBALI ----
ACCOUNTS = {}
RUNNER_URL = "https://luvea-runner.onrender.com"

# ---- INTERFACCIA BASE ----
@app.get("/", response_class=HTMLResponse)
def index():
    return """
    <h2>LuvEA Cloud 🧠</h2>
    <form action="/login" method="post">
        <input name="server" placeholder="MT4 Server"><br>
        <input name="login" placeholder="Account Number"><br>
        <input name="password" placeholder="Password" type="password"><br>
        <button type="submit">Access</button>
    </form>
    """

# ---- LOGIN ----
@app.post("/login")
def login_form(server: str = Form(...), login: str = Form(...), password: str = Form(...)):
    ACCOUNTS[login] = {"server": server, "password": password}
    return HTMLResponse(f"""
        <h3>✅ Connected to {server}</h3>
        <p>Account: {login}</p>
        <hr>
        <form action="/upload-ea/" enctype="multipart/form-data" method="post">
            <input type="file" name="file"><br>
            <button type="submit">Upload EA</button>
        </form><hr>
        <form action="/externs/" method="post">
            <input name="ea_name" placeholder="EA name"><br>
            <textarea name="params" placeholder='{{"LotsPercent":5,"StopLossPips":100}}'></textarea><br>
            <button type="submit">Save externs</button>
        </form><hr>
        <form action="/start" method="post"><button>▶️ Start EA</button></form>
        <form action="/stop" method="post"><button>⏹ Stop EA</button></form>
    """)

# ---- UPLOAD EA ----
@app.post("/upload-ea/")
async def upload_ea(file: UploadFile = File(...)):
    path = os.path.join("uploads", file.filename)
    with open(path, "wb") as f:
        f.write(await file.read())
    return HTMLResponse(f"<p>✅ Uploaded: {file.filename}</p><a href='/'>⬅️ Back</a>")

# ---- EXTERNS ----
@app.post("/externs/", response_class=HTMLResponse)
async def save_externs(ea_name: str = Form(...), params: str = Form(...)):
    try:
        data = json.loads(params)
    except:
        return "<p>⚠️ Invalid JSON format.</p><a href='/'>⬅️ Back</a>"
    with open(os.path.join("externs", f"{ea_name}.json"), "w") as f:
        json.dump(data, f)
    return f"<p>✅ Externs saved for {ea_name}</p><a href='/'>⬅️ Back</a>"

# ---- START / STOP ----
@app.post("/start")
def start_ea():
    try:
        r = requests.post(f"{RUNNER_URL}/start")
        return HTMLResponse(f"<p>{r.json()}</p><a href='/'>⬅️ Back</a>")
    except Exception as e:
        return HTMLResponse(f"<p>❌ Error contacting runner: {e}</p><a href='/'>⬅️ Back</a>")

@app.post("/stop")
def stop_ea():
    try:
        r = requests.post(f"{RUNNER_URL}/stop")
        return HTMLResponse(f"<p>{r.json()}</p><a href='/'>⬅️ Back</a>")
    except Exception as e:
        return HTMLResponse(f"<p>❌ Error contacting runner: {e}</p><a href='/'>⬅️ Back</a>")
