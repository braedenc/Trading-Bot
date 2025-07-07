from dotenv import load_dotenv
import os
import pathlib

project_root = pathlib.Path(__file__).resolve().parent
print("Current working directory:", os.getcwd())
print("Files in cwd:", os.listdir())
load_dotenv(dotenv_path=project_root / ".env")
print("TWELVE_DATA_KEY:", os.getenv("TWELVE_DATA_KEY")) 