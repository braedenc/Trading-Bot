import os
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("TWELVE_DATA_KEY")

print(f"Key length: {len(key) if key else 0}")
print(f"Key: '{key}'")
print(f"Key bytes: {list(key.encode()) if key else []}")
print(f"Key repr: {repr(key)}")

# Test with key stripped of whitespace
if key:
    stripped_key = key.strip()
    print(f"Stripped key: '{stripped_key}'")
    print(f"Stripped length: {len(stripped_key)}") 