"""Basic tests for Engram."""

import pytest
from pathlib import Path


def test_import():
    """Test that engram can be imported."""
    import engram
    assert engram.__version__ == "0.1.0"


def test_cli_exists():
    """Test that CLI module exists."""
    from engram import cli
    assert hasattr(cli, 'main')


def test_device_detection():
    """Test GPU device detection."""
    from engram.cli import get_device
    device = get_device()
    assert device in ["cpu", "mps", "cuda"]
