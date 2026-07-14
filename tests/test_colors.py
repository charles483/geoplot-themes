"""Tests for the colors and colormaps module."""

import pytest
import matplotlib.colors as mcolors
import geoplot_themes as gpt

def test_list_colormaps():
    """Verify that we can list custom colormaps."""
    cmaps = gpt.list_colormaps()
    assert isinstance(cmaps, list)
    assert "elevation" in cmaps
    assert "bathymetry" in cmaps
    assert "blueprint" in cmaps
    assert "neon" in cmaps

def test_get_colormap_valid():
    """Test retrieval of valid custom colormaps."""
    cmap = gpt.get_colormap("elevation")
    assert isinstance(cmap, mcolors.Colormap)
    assert cmap.name == "geoplot_elevation"
    
    # Check case-insensitivity and trim spaces
    cmap_case = gpt.get_colormap("  NeOn  ")
    assert cmap_case.name == "geoplot_neon"

def test_get_colormap_invalid():
    """Test that invalid colormap names raise ValueError."""
    with pytest.raises(ValueError, match="Colormap 'invalid_cmap' not found"):
        gpt.get_colormap("invalid_cmap")

def test_get_palette_valid():
    """Test retrieval of raw hex palettes."""
    palette = gpt.get_palette("editorial")
    assert isinstance(palette, list)
    assert len(palette) > 0
    assert all(c.startswith("#") for c in palette)

def test_get_palette_invalid():
    """Test that invalid palette names raise ValueError."""
    with pytest.raises(ValueError, match="Palette 'invalid_palette' not found"):
        gpt.get_palette("invalid_palette")
