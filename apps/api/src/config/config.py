from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # This tells Pydantic to load variables from a .env file
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    SUPABASE_URL: str
    SUPABASE_KEY: str
    GEMINI_API_KEY: str
    GITHUB_CLIENT_ID: str
    GITHUB_CLIENT_SECRET: str


# Create a single, reusable instance of the settings
settings = Settings()
