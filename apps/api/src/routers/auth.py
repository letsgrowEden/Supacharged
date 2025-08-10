from fastapi import APIRouter, Response, HTTPException
from starlette.responses import RedirectResponse
from config.config import settings 
import httpx
import logging

# It's good practice to get the logger for the current module
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/auth/github/login")
async def login():
    # The scope requests the user's public profile and email
    scope = "read:user user:email"
    return RedirectResponse(
        url=f"https://github.com/login/oauth/authorize?client_id={settings.GITHUB_CLIENT_ID}&scope={scope}"
    )


@router.get("/auth/github/callback")
async def github_callback(code: str):
    # 1. Exchange the code for an access token from GitHub
    params = {
        "client_id": settings.GITHUB_CLIENT_ID,
        "client_secret": settings.GITHUB_CLIENT_SECRET,
        "code": code,
    }
    headers = {"Accept": "application/json"}
    
    async with httpx.AsyncClient() as client:
        token_response = await client.post("https://github.com/login/oauth/access_token", params=params, headers=headers)

    if token_response.status_code != 200:
        logger.error(f"Failed to get access token: {token_response.text}")
        raise HTTPException(status_code=400, detail="Failed to exchange code for access token.")

    token_data = token_response.json()
    access_token = token_data.get("access_token")

    if not access_token:
        logger.error(f"Access token not found in response: {token_data}")
        raise HTTPException(status_code=400, detail="Access token not found in GitHub response.")

    # 2. Use the access token to get the main user profile
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as client:
        user_response = await client.get("https://api.github.com/user", headers=headers)

    if user_response.status_code != 200:
        logger.error(f"Failed to get user data from GitHub: {user_response.text}")
        raise HTTPException(status_code=400, detail="Failed to get user data from GitHub.")

    user_data = user_response.json()
    
    # --- LOGGING FOR DEBUGGING ---
    logger.info(f"Successfully fetched user data from GitHub: {user_data}")
    # -----------------------------

    # Gracefully handle cases where name or email might be null due to privacy settings
    if not user_data.get("name"):
        user_data["name"] = user_data.get("login") # Use username as a fallback

    # 3. TODO: Find or create the user in our Supabase DB using the user_data
    # user = await find_or_create_user(user_data)

    # 4. TODO: Create a JWT session token for our own app
    # session_token = create_session_token(user.id)

    # 5. For now, just return the enriched GitHub user data
    return {"github_user": user_data}