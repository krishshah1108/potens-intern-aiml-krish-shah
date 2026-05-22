"""Pytest fixtures — avoid ChromaDB/ONNX load during lightweight tests."""

import sys
from unittest.mock import MagicMock

# Prevent onnx/chromadb native crash on some Windows setups during unit tests
if "chromadb" not in sys.modules:
    chroma_mock = MagicMock()
    chroma_mock.PersistentClient.return_value.get_or_create_collection.return_value = MagicMock(
        count=0
    )
    sys.modules["chromadb"] = chroma_mock
    sys.modules["chromadb.config"] = MagicMock()
