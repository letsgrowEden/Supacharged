import logging
from services.supabase_uploader import SupabaseUploader
from schemas.ats import ATSModel, PropDetail

# Configure basic logging to see the output from the uploader
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_supabase_test():
    """
    Tests the Supabase upload functionality with a sample ATSModel object.
    """
    logger.info("--- Starting Supabase Upload Test ---")

    # 1. Create a sample ATSModel object to simulate real data.
    # This represents the output you'd get from the ATSCreator.
    sample_ats = ATSModel(
        componentName="TestCard",
        description="A card component for displaying test information.",
        dependencies=["react", "@mui/material"],
        internalDependencies=[],
        propsInterface={
            "title": PropDetail(type="string", isOptional=False, options=None),
            "content": PropDetail(type="string", isOptional=True, options=None),
        },
        tags=["test", "card", "ui"],
        rawCode="export const TestCard = () => <div>Test</div>;"
    )

    try:
        # 2. Instantiate the uploader.
        # This will automatically connect to Supabase using your .env settings.
        uploader = SupabaseUploader()

        # 3. Call the upload method.
        logger.info(f"Attempting to upload ATS for: {sample_ats.componentName}")
        # In a real application, we must ensure the parent record (the design kit) exists
        # before creating a child record (the component).
        logger.info("Ensuring 'Test Design Kit' exists...")
        kit_data = {
            "name": "Test Design Kit",
            "description": "A kit for testing purposes."
        }
        # Use the uploader's client to upsert the kit, ensuring it exists.
        kit_response = uploader.client.table("design_kits").upsert(kit_data, on_conflict="name").execute()
        kit_id = kit_response.data[0]['id']
        logger.info(f"Using kit_id: {kit_id}")

        uploader.upload_ats(sample_ats, kit_id=kit_id)

        logger.info("\n✅ --- Supabase Upload Test Completed Successfully! ---")
        logger.info("Check the 'components' table in your Supabase project to verify the data.")

    except ValueError as e:
        # This will catch configuration errors (e.g., missing .env variables)
        logger.error(f"Configuration Error: {e}")
    except Exception as e:
        # This will catch any other errors during the upload process.
        logger.error(f"An unexpected error occurred during the upload test: {e}")

if __name__ == "__main__":
    run_supabase_test()
