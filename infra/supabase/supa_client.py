import os, asyncio
from supabase import create_client, Client

class SupabaseClient:
    """Tiny wrapper for risk_limits refresh."""

    def __init__(self) -> None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
        self.sb: Client = create_client(url, key)

    async def fetch_risk_limits(self) -> list[dict]:
        loop = asyncio.get_running_loop()
        # supabase-py is blocking; off-load to default executor
        return await loop.run_in_executor(
            None,
            lambda: self.sb.table("risk_limits").select("*").execute().data
        ) or [] 