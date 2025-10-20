@app.post("/start")
def start_ea():
    try:
        # Read dynamic runner URL from Gitpod
        path = "/workspace/runner_url.txt"
        if not os.path.exists(path):
            raise Exception("runner_url.txt not found — run ./runner_boot.sh in Gitpod")

        with open(path, "r") as f:
            runner_url = f.read().strip()

        if not runner_url:
            raise Exception("Runner URL file empty")

        # Verify the runner is alive
        test = requests.get(f"{runner_url}/", timeout=5)
        if test.status_code != 200:
            raise Exception("Runner not responding")

        # Send the start command
        r = requests.post(f"{runner_url}/start", timeout=10)
        return {
            "status": "started ✅",
            "runner_url": runner_url,
            "response": r.text
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}
