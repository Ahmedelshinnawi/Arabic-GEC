from supabase import Client, create_client

from app.config import get_settings

settings = get_settings()


supabase: Client = create_client(settings.supabase_url, settings.supabase_key)


CORRECTIONS_TABLE = "corrections"
