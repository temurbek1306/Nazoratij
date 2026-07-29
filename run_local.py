from dotenv import load_dotenv
import os
import subprocess

load_dotenv()
subprocess.run(["python", "github_runner.py"])
