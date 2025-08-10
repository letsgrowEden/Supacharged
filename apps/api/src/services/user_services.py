from db.db import supabase_client
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

async def find_or_create_user(github_user_data: dict):
    """
    Finds a user in the database by their GitHub ID. If the user doesn't exist,
    it creates a new user record.
    """
    github_id = github_user_data.get("id")
    email = github_user_data.get("email")
    name = github_user_data.get("name")
    avatar_url = github_user_data.get("avatar_url")

    if not github_id or not email:
        raise HTTPException(status_code=400, detail="Missing GitHub ID or email.")

    try:
        # 1. Check if the user already exists in our auth table
        response = supabase_client.auth.admin.get_user_by_id(github_id)

        if response.data:
            logger.info(f"User found with GitHub ID: {github_id}")
            return response.data[0]
        else:
            logger.info(f"User not found. Creating new user for GitHub ID: {github_id}")
            
            
        # If the above line doesn't throw an error, the user exists.
        # Note: Supabase might not support getting user by custom ID directly this way.
        # A more robust method is to query a public 'profiles' table.
        # For now, let's assume a profiles table.
        
        # A better approach: Query a 'profiles' table we control.
        # Let's create a public table named 'profiles' with a 'github_id' column.
        
        # First, try to find the user profile.
        profile_response = supabase_client.table('profiles').select('*').eq('github_id', github_id).execute()

        if profile_response.data:
            print(f"User found with GitHub ID: {github_id}")
            return profile_response.data[0]
        else:
            # 2. If user does not exist, create them
            print(f"User not found. Creating new user for GitHub ID: {github_id}")
            
            # We need to create a user in auth.users and a profile in public.profiles
            # For simplicity in the MVP, let's assume we are just creating a profile.
            # In a full implementation, you'd use supabase.auth.admin.create_user()
            
            new_profile_data = {
                'github_id': github_id,
                'email': email,
                'name': name,
                'avatar_url': avatar_url
            }
            
            insert_response = supabase_client.table('profiles').insert(new_profile_data).execute()
            
            if insert_response.data:
                return insert_response.data[0]
            else:
                raise HTTPException(status_code=500, detail="Failed to create user profile.")

    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")