import os
import tempfile
import shutil
from typing import List

import pytest
from unittest.mock import patch, MagicMock
import uuid

# Assuming ingest_components.py is in the same directory or properly discoverable
# For testing purposes, we'll ensure the path is correct
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts")))
from scripts.ingest_components import find_component_files, generate_ats_for_components, validate_and_transform_ats
from schemas.component import ComponentCreate

class DummyATSModel:
    def __init__(self, name, serializable=True):
        self.componentName = name
        self.description = "desc"
        self.dependencies = ["react"]
        self.internalDependencies = []
        self.propsInterface = {}
        self.tags = ["ui"]
        self.rawCode = "code"
        self._serializable = serializable
    def model_dump(self):
        if self._serializable:
            return {
                "componentName": self.componentName,
                "description": self.description,
                "dependencies": self.dependencies,
                "internalDependencies": self.internalDependencies,
                "propsInterface": self.propsInterface,
                "tags": self.tags,
                "rawCode": self.rawCode,
            }
        else:
            # Not JSON serializable
            return {"bad": set([1,2,3])}

@pytest.fixture
def temp_component_dir():
    # Create a temporary directory structure for testing
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a component file
        os.makedirs(os.path.join(tmpdir, "src", "components"), exist_ok=True)
        with open(os.path.join(tmpdir, "src", "components", "Button.tsx"), "w") as f:
            f.write("// Button component")
        with open(os.path.join(tmpdir, "src", "components", "Input.jsx"), "w") as f:
            f.write("// Input component")
        
        # Create a non-component file
        with open(os.path.join(tmpdir, "src", "utils.ts"), "w") as f:
            f.write("// Utility file")
        
        # Create a nested directory with a component
        os.makedirs(os.path.join(tmpdir, "src", "nested", "deep"), exist_ok=True)
        with open(os.path.join(tmpdir, "src", "nested", "deep", "Header.tsx"), "w") as f:
            f.write("// Header component")
        
        yield tmpdir

def test_find_component_files_directory(temp_component_dir):
    found_files = find_component_files(temp_component_dir)
    expected_files = [
        os.path.abspath(os.path.join(temp_component_dir, "src", "components", "Button.tsx")),
        os.path.abspath(os.path.join(temp_component_dir, "src", "components", "Input.jsx")),
        os.path.abspath(os.path.join(temp_component_dir, "src", "nested", "deep", "Header.tsx")),
    ]
    
    # Sort both lists for consistent comparison
    found_files.sort()
    expected_files.sort()

    assert len(found_files) == len(expected_files)
    assert found_files == expected_files

def test_find_component_files_single_file(temp_component_dir):
    single_file_path = os.path.join(temp_component_dir, "src", "components", "Button.tsx")
    found_files = find_component_files(single_file_path)
    assert found_files == [os.path.abspath(single_file_path)]

def test_find_component_files_empty_directory():
    with tempfile.TemporaryDirectory() as tmpdir:
        found_files = find_component_files(tmpdir)
        assert found_files == []

def test_find_component_files_no_component_files():
    with tempfile.TemporaryDirectory() as tmpdir:
        with open(os.path.join(tmpdir, "README.md"), "w") as f:
            f.write("# Readme")
        with open(os.path.join(tmpdir, "main.py"), "w") as f:
            f.write("print('Hello')")
        found_files = find_component_files(tmpdir)
        assert found_files == []

def test_find_component_files_non_existent_path():
    non_existent_path = "/path/to/non/existent/directory_or_file"
    found_files = find_component_files(non_existent_path)
    assert found_files == []

@pytest.fixture
def temp_component_files():
    files = []
    with tempfile.TemporaryDirectory() as tmpdir:
        for i in range(3):
            file_path = os.path.join(tmpdir, f"Component{i}.tsx")
            with open(file_path, "w") as f:
                f.write(f"// Component {i}")
            files.append(file_path)
        yield files

def test_generate_ats_for_components_happy_path(temp_component_files):
    """All files produce valid ATSModel objects."""
    with patch("scripts.ingest_components.ATSCreator") as MockCreator:
        instance = MockCreator.return_value
        instance.create_ats_from_file.side_effect = [DummyATSModel(f"Component{i}") for i in range(3)]
        ats_list = generate_ats_for_components(temp_component_files)
        assert len(ats_list) == 3
        assert all(isinstance(ats, DummyATSModel) for ats in ats_list)

def test_generate_ats_for_components_partial_failure(temp_component_files):
    """Some files fail ATS generation (return None)."""
    with patch("scripts.ingest_components.ATSCreator") as MockCreator:
        instance = MockCreator.return_value
        # First succeeds, second fails, third succeeds
        instance.create_ats_from_file.side_effect = [DummyATSModel("A"), None, DummyATSModel("C")]
        ats_list = generate_ats_for_components(temp_component_files)
        assert len(ats_list) == 2
        assert all(isinstance(ats, DummyATSModel) for ats in ats_list)

def test_generate_ats_for_components_empty_input():
    """No files provided; should return empty list."""
    ats_list = generate_ats_for_components([])
    assert ats_list == []

def test_generate_ats_for_components_all_failures(temp_component_files):
    """All files fail ATS generation (return None)."""
    with patch("scripts.ingest_components.ATSCreator") as MockCreator:
        instance = MockCreator.return_value
        instance.create_ats_from_file.side_effect = [None, None, None]
        ats_list = generate_ats_for_components(temp_component_files)
        assert ats_list == []

def test_validate_and_transform_ats_happy_path():
    ats = DummyATSModel("Button")
    kit_id = uuid.uuid4()
    comp = validate_and_transform_ats(ats, kit_id)
    assert isinstance(comp, ComponentCreate)
    assert comp.name == "Button"
    assert comp.kit_id == kit_id
    assert comp.metadata["componentName"] == "Button"

def test_validate_and_transform_ats_missing_component_name():
    ats = DummyATSModel(None)
    kit_id = uuid.uuid4()
    with pytest.raises(ValueError, match="componentName"):
        validate_and_transform_ats(ats, kit_id)

def test_validate_and_transform_ats_invalid_kit_id():
    ats = DummyATSModel("Button")
    kit_id = "not-a-uuid"
    with pytest.raises(ValueError, match="kit_id"):
        validate_and_transform_ats(ats, kit_id)

def test_validate_and_transform_ats_non_serializable():
    ats = DummyATSModel("Button", serializable=False)
    kit_id = uuid.uuid4()
    with pytest.raises(ValueError, match="serializable"):
        validate_and_transform_ats(ats, kit_id)