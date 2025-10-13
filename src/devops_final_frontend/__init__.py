import subprocess
import sys
from pathlib import Path


def main():
    app_file = Path(__file__).absolute().parent / "view.py"
    cmd = [sys.executable, "-m", "streamlit", "run", app_file, "--server.port", "8501"]

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        for line in proc.stdout:
            print(line, end="")
    except KeyboardInterrupt:
        proc.terminate()
        proc.wait()