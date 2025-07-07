from dotenv import load_dotenv
import os

load_dotenv()

print("URL:", os.getenv("SUPABASE_URL") or "[MISSING]")
key_service = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
key_anon = os.getenv("SUPABASE_ANON_KEY")
print("Service Role Key:", (key_service[:8] + "...") if key_service else "[MISSING]")
print("Anon Key:", (key_anon[:8] + "...") if key_anon else "[MISSING]") 