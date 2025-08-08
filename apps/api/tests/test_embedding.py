import pytest
from unittest.mock import patch, MagicMock
from typing import List

# Ensure the path is correct for importing the embedding module
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "embedding")))

from embedding import generate_embedding, get_model


@pytest.fixture
def mock_sentence_transformer():
    with patch('embedding.SentenceTransformer') as MockSentenceTransformer:
        mock_instance = MockSentenceTransformer.return_value
        mock_instance.encode.return_value = [0.1, 0.2, 0.3]
        yield mock_instance

def test_generate_embedding_happy_path(mock_sentence_transformer):
    """Test that a valid string generates an embedding."""
    text = "This is a test sentence."
    embedding = generate_embedding(text)
    assert isinstance(embedding, List)
    assert len(embedding) == 3  # Based on our mock return value
    assert embedding == [0.1, 0.2, 0.3]

def test_generate_embedding_empty_string():
    """Test that an empty string raises a ValueError."""
    with pytest.raises(ValueError, match="non-empty string"):
        generate_embedding("")

def test_generate_embedding_non_string_input():
    """Test that non-string input raises a ValueError."""
    with pytest.raises(ValueError, match="non-empty string"):
        generate_embedding(123)

def test_generate_embedding_model_failure():
    """Test that a failure in the embedding model is handled."""
    with patch('embedding.get_model') as mock_get_model:
        mock_model_instance = MagicMock()
        mock_get_model.return_value = mock_model_instance
        mock_model_instance.encode.side_effect = Exception("Simulated model error")

        with pytest.raises(ValueError, match="Embedding generation failed"):
            generate_embedding("some text")