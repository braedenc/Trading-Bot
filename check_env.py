from dotenv import load_dotenv, dotenv_values, find_dotenv
import os, pprint, pathlib, sys

print("find_dotenv():", find_dotenv())
print("dotenv_values():")
pprint.pp(dotenv_values())

load_dotenv()           # load .env into the current process

print("TWELVE_DATA_KEY:", os.getenv("TWELVE_DATA_KEY") or "[MISSING]") 