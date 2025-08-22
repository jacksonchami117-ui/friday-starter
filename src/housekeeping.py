import os, time, datetime as dt, shutil

def _state_dir():
    return os.environ.get("STATE_DIR","./state")

def _outputs_dir():
    p = os.path.join(_state_dir(), "outputs")
    os.makedirs(p, exist_ok=True)
    return p

def start_housekeeping_thread():
    import threading
    def run():
        while True:
            cutoff = dt.datetime.utcnow() - dt.timedelta(days=int(os.getenv("CLEAN_DAYS","14")))
            for root, _, files in os.walk("state/outputs"):
                for f in files:
                    path = os.path.join(root, f)
                    if dt.datetime.utcfromtimestamp(os.path.getmtime(path)) < cutoff: 
                        os.remove(path)
            time.sleep(86400)
    threading.Thread(target=run, daemon=True).start()
