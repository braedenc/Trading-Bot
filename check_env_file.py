import os
import pathlib

# Get the project root
project_root = pathlib.Path(__file__).resolve().parent
env_path = project_root / ".env"

print(f"Looking for .env at: {env_path}")
print(f"File exists: {env_path.exists()}")

if env_path.exists():
    with open(env_path, 'r') as f:
        content = f.read()
        print("Raw .env contents:")
        print(repr(content))
        print("\nLines:")
        for i, line in enumerate(content.split('\n'), 1):
            print(f"Line {i}: {repr(line)}")
else:
    print("No .env file found!") 