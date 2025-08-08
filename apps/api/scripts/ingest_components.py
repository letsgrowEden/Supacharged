import os
import logging
from typing import List, Optional
from uuid import UUID
from agents.ats_creator import ATSCreator, ATSModel
from schemas.component import ComponentCreate

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

"""
Module for discovering React component files and generating their Abstract Technical Specification (ATS)
using the ATSCreator agent. Follows project protocols for structure, logging, and error handling.
"""

def find_component_files(path: str) -> List[str]:
    """
    Identifies React component source files (.tsx, .jsx) within a given path.
    The path can be a single file or a directory.
    Logs key steps for traceability.

    Args:
        path: The path to a component file or a directory containing components.

    Returns:
        A list of absolute paths to the React component files.
    """
    component_files = []
    logger.info(f"Starting search for component files in: {path}")
    if not os.path.exists(path):
        logger.warning(f"Path does not exist: {path}")
        return []
    if os.path.isfile(path):
        if path.endswith(('.tsx', '.jsx')):
            logger.info(f"Found component file: {path}")
            component_files.append(os.path.abspath(path))
        else:
            logger.info(f"File is not a component (.tsx/.jsx): {path}")
    elif os.path.isdir(path):
        logger.info(f"Traversing directory: {path}")
        for root, _, files in os.walk(path):
            for file in files:
                if file.endswith(('.tsx', '.jsx')):
                    file_path = os.path.abspath(os.path.join(root, file))
                    logger.info(f"Found component file: {file_path}")
                    component_files.append(file_path)
    else:
        logger.warning(f"Path is neither a file nor a directory: {path}")
    logger.info(f"Total component files found: {len(component_files)}")
    return component_files

def generate_ats_for_components(component_paths: List[str]) -> List[ATSModel]:
    """
    For each component file path, generate its ATS using the ATSCreator agent.
    Logs the process and collects valid ATSModel objects.

    Args:
        component_paths: List of absolute paths to component files.

    Returns:
        List of valid ATSModel objects (one per successfully processed component).
    """
    ats_creator = ATSCreator()
    ats_results = []
    for path in component_paths:
        logger.info(f"Generating ATS for: {path}")
        try:
            ats = ats_creator.create_ats_from_file(path)
            if ats is not None:
                logger.info(f"ATS generation successful for: {path}")
                ats_results.append(ats)
            else:
                logger.warning(f"ATS generation failed for: {path}")
        except Exception as e:
            logger.error(f"Exception during ATS generation for {path}: {e}")
    logger.info(f"Total ATS objects generated: {len(ats_results)}")
    return ats_results

def validate_and_transform_ats(
    ats: ATSModel, kit_id: UUID, category: Optional[str] = None
) -> ComponentCreate:
    """
    Validates and transforms an ATSModel into a ComponentCreate object for Supabase upload.
    - Maps ATS fields to the schema fields.
    - Ensures required fields are present and of correct type.
    - Embeds the full ATS as the 'metadata' field.
    - Raises ValueError if validation fails.

    Args:
        ats: The ATSModel object from the ATS agent.
        kit_id: The UUID of the design kit this component belongs to.
        category: Optional category for the component.

    Returns:
        ComponentCreate object ready for upload.
    """
    if not ats.componentName or not isinstance(ats.componentName, str):
        raise ValueError("ATS output missing or invalid 'componentName'.")
    if not isinstance(kit_id, UUID):
        raise ValueError("kit_id must be a valid UUID.")
    # Optionally, check that all ATS fields are JSON serializable (metadata)
    import json
    try:
        json.dumps(ats.model_dump())
    except Exception as e:
        raise ValueError(f"ATS output is not JSON serializable: {e}")
    return ComponentCreate(
        kit_id=kit_id,
        name=ats.componentName,
        category=category,
        metadata=ats.model_dump(),
        embedding=None  # To be filled in later if needed
    )

if __name__ == "__main__":
    # For demonstration, assuming components are in supacharged/packages/ui/components/ui/
    components_base_path = "/Users/atango/Documents/supacharged/supacharged/packages/ui/components/ui/"
    logger.info(f"Searching for components in: {components_base_path}")
    found_components = find_component_files(components_base_path)
    if found_components:
        logger.info("Generating ATS for discovered components...")
        ats_list = generate_ats_for_components(found_components)
        logger.info(f"ATS generation complete. {len(ats_list)} ATS objects created.")
    else:
        logger.info("No component files found.")