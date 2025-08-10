import logging
from supabase import create_client, Client
from config.config import settings
from typing import List
from schemas.ats import ATSModel

logger = logging.getLogger(__name__)

class SupabaseUploader:
    """Handles all interactions with the Supabase database."""

    def __init__(self):
        """
        Initializes the Supabase client using credentials from the environment.
        Ensures a secure connection without hardcoding keys.
        """
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            logger.error("Supabase URL or Key is not configured.")
            raise ValueError("Supabase credentials must be set in the environment.")
        
        self.client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        logger.info("Supabase client initialized successfully.")

    def upload_ats(self, ats_data: ATSModel, kit_id: str, embedding: List[float] = None) -> None:
        """
        Uploads a single component's ATS data to the 'components' table.

        This method uses `upsert`, which will insert a new row or update an
        existing one if a component with the same `componentName` already exists.
        This prevents creating duplicate entries.

        Args:
            ats_data: A validated Pydantic model containing the component's ATS.

        Raises:
            Exception: If the upload to Supabase fails.
        """
        table_name = "components"
        # Transform the ATSModel into the structure of the 'components' table.
        # This is a critical step to ensure the data we send matches the database schema.
        component_data = {
            "name": ats_data.componentName,
            "kit_id": kit_id,
            "metadata": ats_data.model_dump(),  # Nest the entire ATS object in the metadata field
            "embedding": embedding
        }

        try:
            logger.info(f"Uploading ATS for component: {ats_data.componentName} to table '{table_name}'.")
            
            # We specify `on_conflict='name'` to tell Supabase to use the 'name' column
            # to identify and update existing records, preventing duplicates.
            response = self.client.table(table_name).upsert(component_data, on_conflict="kit_id,name").execute()
            
            logger.info(f"Successfully uploaded ATS for {ats_data.componentName}.")
            logger.debug(f"Supabase response: {response}")

        except Exception as e:
            logger.error(f"Failed to upload ATS for {ats_data.componentName}. Error: {e}")
            # Re-raise the exception to allow the caller to handle it.
            raise
