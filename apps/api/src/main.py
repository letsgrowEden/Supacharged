from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db.db import supabase_client
from config.config import settings
from routers import auth

app = FastAPI(title="Supacharged API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])

# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint that verifies both API and database connectivity.
    Returns:
        dict: Status of the API and database connection
    """
    # Check if environment variables are set
    env_status = {
        "SUPABASE_URL_SET": bool(settings.SUPABASE_URL),
        "SUPABASE_KEY_SET": bool(settings.SUPABASE_KEY),
    }

    # If either environment variable is missing, return early
    if not all(env_status.values()):
        return {
            "status": "error",
            "message": "Missing required environment variables",
            "env_vars": env_status,
            "database": "not_connected",
        }

    try:
        # Test database connection
        # Test database connection by fetching a single record
        db_response = (
            supabase_client.table("design_kits").select("id").limit(1).execute()
        )
        db_status = {"status": "connected", "can_query": len(db_response.data) >= 0}
    except Exception as e:
        db_status = {"status": "error", "details": str(e)}

    return {"status": "healthy", "environment": "configured", "database": db_status}
