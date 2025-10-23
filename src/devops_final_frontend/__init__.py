"""DevOps Final Frontend - LLM Generator

This is a minimalist frontend, written using Streamlit, for the project backend.
"""

import subprocess
import sys
from pathlib import Path

from devops_final_frontend.config import create_secrets_file


def main(*args):
    """
    Start the streamlit app as a subprocess running the "streamlit run" command.
    Used by the UV project-script `devops_final_frontend`
    """

    create_secrets_file()

    app_file = Path(__file__).absolute().parent / "view.py"
    cmd = [sys.executable, "-m", "streamlit", "run", app_file, "--server.port", "8501", *args]

    try:
        with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1) as proc:
            for line in proc.stdout:
                print(line, end="")
    except KeyboardInterrupt:
        proc.terminate()
        proc.wait()
