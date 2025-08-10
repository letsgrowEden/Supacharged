from fastapi import APIRouter, Response
from starlette.responses import RedirectResponse
from config.config import settings 
import httpx

router = APIRouter()

@router.get("/auth/github/login")
async def login(response: Response):
    return RedirectResponse(url=f"https://github.com/login/oauth/authorize?client_id={settings.GITHUB_CLIENT_ID}")

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
        response = await client.post("https://github.com/login/oauth/access_token", params=params, headers=headers)

    response_json = response.json()
    access_token = response_json.get("access_token")

    # 2. Use the access token to get user info from GitHub
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.github.com/user", headers=headers)

    user_data = response.json()

    # 3. TODO: Find or create the user in our Supabase DB
    # user = await find_or_create_user(user_data)

    # 4. TODO: Create a JWT session token for our own app
    # session_token = create_session_token(user.id)

    # 5. For now, just return the GitHub user data
    return {"github_user": user_data}