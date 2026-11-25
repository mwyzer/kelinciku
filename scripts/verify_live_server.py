import subprocess
import sys
import time
import urllib.request

print("Menjalankan uvicorn server FastAPI di background port 8000...")
proc = subprocess.Popen([
    sys.executable, "-m", "uvicorn", "app.main:app",
    "--app-dir", "backend",
    "--host", "127.0.0.1",
    "--port", "8000"
])

time.sleep(2)
try:
    with urllib.request.urlopen("http://127.0.0.1:8000/api/v1/health") as response:
        print("HTTP Health Response:", response.status, response.read().decode('utf-8'))
finally:
    proc.terminate()
    print("Test server shutdown.")
