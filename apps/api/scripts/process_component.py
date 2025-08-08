# Standard library imports
import logging
import os
import sys

# This block modifies the Python path to allow for absolute imports from the project root.
# It must be placed before project-specific imports.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Project-specific imports
from agents.ats_creator import ATSCreator
from services.supabase_uploader import SupabaseUploader
from embedding import generate_embedding 

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_and_upload(file_path: str):
    """
    Processes a single component file: reads its content, generates ATS,
    creates an embedding, and uploads it to Supabase.
    """
    logger.info(f"--- Starting to process component: {file_path} ---")

    try:
        # 1. Initialize Services
        ats_creator = ATSCreator()
        supabase_uploader = SupabaseUploader()

        # 2. Generate ATS from the component file
        logger.info("Generating ATS from component file...")
        ats_data = ats_creator.create_ats_from_file(file_path)
        logger.info(f"Successfully generated ATS for: {ats_data.componentName}")

        # 4. Generate Embedding
        logger.info("Generating embedding from component description...")
        embedding = generate_embedding(ats_data.description)
        logger.info(f"Generated embedding of dimension: {len(embedding)}")

        # 5. Upload to Supabase
        logger.info("Ensuring 'Test Design Kit' exists for upload...")
        kit_data = {"name": "Test Design Kit", "description": "A kit for testing purposes."}
        kit_response = supabase_uploader.client.table("design_kits").upsert(kit_data, on_conflict="name").execute()
        kit_id = kit_response.data[0]['id']
        logger.info(f"Using kit_id: {kit_id}")

        logger.info("Uploading component data and embedding to Supabase...")
        supabase_uploader.upload_ats(ats_data=ats_data, kit_id=kit_id, embedding=embedding)

        logger.info("\n✅ --- Component processing and upload completed successfully! ---")

    except FileNotFoundError:
        logger.error(f"Error: The file was not found at {file_path}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    # We will replace this with the actual path to the reel component
    # Set the full path to the component we want to process.
    component_file_path = "/Users/atango/Documents/supacharged/supacharged/packages/ui/components/ui/button.tsx" 
    process_and_upload(component_file_path)
