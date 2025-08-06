from supabase import create_client, Client
from config.config import settings

# Initialize the Supabase client with our secure credentials
supabase_client: Client = create_client(
    supabase_url=settings.SUPABASE_URL,
    supabase_key=settings.SUPABASE_KEY
)