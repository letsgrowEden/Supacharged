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

    # 2. Use the access token to get the main user profile
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as client:
        user_response = await client.get("https://api.github.com/user", headers=headers)
        emails_response = await client.get("https://api.github.com/user/emails", headers=headers)

    user_data = user_response.json()
    emails_data = emails_response.json()

    # Find the primary email address
    primary_email = next((email['email'] for email in emails_data if email['primary']), None)
    user_data['email'] = primary_email

    # 3. TODO: Find or create the user in our Supabase DB using the user_data
    # user = await find_or_create_user(user_data)

    # 4. TODO: Create a JWT session token for our own app
    # session_token = create_session_token(user.id)

    # 5. For now, just return the enriched GitHub user data
    return {"github_user": user_data}
