"""Tests for the core themes module."""

import pytest
import matplotlib.pyplot as plt
import geoplot_themes as gpt

def test_list_themes():
    """Verify that we can list custom themes."""
    themes = gpt.list_themes()
    assert isinstance(themes, list)
    assert "dark_matter" in themes
    assert "retro_blueprint" in themes
    assert "natgeo_minimalist" in themes

def test_set_theme_valid():
    """Test that setting a valid theme modifies rcParams."""
    gpt.reset_theme()
    original_facecolor = plt.rcParams["figure.facecolor"]
    
    # Apply theme
    gpt.set_theme("dark_matter")
    assert plt.rcParams["figure.facecolor"] == "#090a0f"
    assert plt.rcParams["text.color"] == "#d1d2d6"
    
    # Reset
    gpt.reset_theme()
    assert plt.rcParams["figure.facecolor"] == original_facecolor

def test_set_theme_invalid():
    """Test that invalid theme names raise ValueError."""
    with pytest.raises(ValueError, match="Theme 'unknown_theme' not found"):
        gpt.set_theme("unknown_theme")

def test_use_theme_context_manager():
    """Test that the context manager temporarily applies a theme."""
    gpt.reset_theme()
    original_facecolor = plt.rcParams["figure.facecolor"]
    
    with gpt.use_theme("retro_blueprint"):
        assert plt.rcParams["figure.facecolor"] == "#0a2342"
        assert plt.rcParams["text.color"] == "#ffffff"
        
    # Verify rollback
    assert plt.rcParams["figure.facecolor"] == original_facecolor
