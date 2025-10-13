import subprocess
import sys
from pathlib import Path


def main():
    """
    Start the streamlit app as a subprocess running the "streamlit run" command.
    Used by the UV project-script `devops_final_frontend`
    """
    app_file = Path(__file__).absolute().parent / "view.py"
    cmd = [sys.executable, "-m", "streamlit", "run", app_file, "--server.port", "8501"]

    try:
        with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1) as proc:
            for line in proc.stdout:
                print(line, end="")
    except KeyboardInterrupt:
        proc.terminate()
        proc.wait()
