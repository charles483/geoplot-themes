"""Tests for the geopandas plotting helper module."""

import pytest
import geopandas as gpd
from shapely.geometry import Polygon
import matplotlib.pyplot as plt
import geoplot_themes as gpt

@pytest.fixture
def mock_projected_gdf() -> gpd.GeoDataFrame:
    """Create a mock GeoDataFrame in a projected coordinate system (meters)."""
    p1 = Polygon([(0, 0), (1000, 0), (1000, 1000), (0, 1000)])
    p2 = Polygon([(1000, 1000), (2000, 1000), (2000, 2000), (1000, 2000)])
    return gpd.GeoDataFrame({"val": [1, 2]}, geometry=[p1, p2], crs="EPSG:3857")

@pytest.fixture
def mock_geographic_gdf() -> gpd.GeoDataFrame:
    """Create a mock GeoDataFrame in WGS84 coordinates (degrees)."""
    p1 = Polygon([(-74, 40), (-73, 40), (-73, 41), (-74, 41)])
    return gpd.GeoDataFrame({"val": [10]}, geometry=[p1], crs="EPSG:4326")

def test_plot_map_projected(mock_projected_gdf):
    """Test plotting with a projected CRS, including theme application and scale bar."""
    fig, ax = plt.subplots()
    returned_ax = gpt.plot_map(
        mock_projected_gdf,
        column="val",
        theme="dark_matter",
        colormap="neon",
        ax=ax,
        scale_bar=True,
        north_arrow=True
    )
    
    assert returned_ax is ax
    
    # Check that scale bar artist was added (AnchoredSizeBar is added to artists)
    artists = returned_ax.artists
    assert len(artists) > 0
    
    # Check that north arrow annotation was added (stored in ax.texts)
    texts = returned_ax.texts
    assert any(t.get_text() == "N" for t in texts)
    
    plt.close(fig)

def test_plot_map_geographic(mock_geographic_gdf):
    """Test plotting with a geographic CRS."""
    fig, ax = plt.subplots()
    returned_ax = gpt.plot_map(
        mock_geographic_gdf,
        theme="natgeo_minimalist",
        colormap="elevation",
        ax=ax,
        scale_bar=True,
        north_arrow=True
    )
    
    assert returned_ax is ax
    
    # Verify elements are present
    assert len(returned_ax.artists) > 0
    assert any(t.get_text() == "N" for t in returned_ax.texts)
    
    plt.close(fig)

def test_plot_map_naive_crs_error(mock_geographic_gdf):
    """Test that plot_map raises a ValueError if the input GeoDataFrame has no CRS but a target crs is specified."""
    naive_gdf = mock_geographic_gdf.copy()
    naive_gdf.crs = None
    
    with pytest.raises(ValueError, match="Cannot reproject GeoDataFrame to target CRS because the input GeoDataFrame has no CRS set."):
        gpt.plot_map(naive_gdf, crs="EPSG:3857")

def test_geographic_scale_bar_latitude_correction():
    """Verify that scale bar values are adjusted by latitude (cosine correction)."""
    # Create two GeoDataFrames at different latitudes but with the exact same span (0.5 degrees)
    # 1. Near the Equator (latitude 0)
    p_eq = Polygon([(-10, 0), (-9.5, 0), (-9.5, 0.5), (-10, 0.5)])
    gdf_eq = gpd.GeoDataFrame({"val": [1]}, geometry=[p_eq], crs="EPSG:4326")
    
    # 2. Near 60 degrees latitude
    p_60 = Polygon([(-10, 60), (-9.5, 60), (-9.5, 60.5), (-10, 60.5)])
    gdf_60 = gpd.GeoDataFrame({"val": [1]}, geometry=[p_60], crs="EPSG:4326")
    
    # Call add_scale_bar directly on geographic axes (bypassing plot_map auto-UTM)
    fig1, ax1 = plt.subplots()
    ax1.set_xlim(-10, -9.5)
    ax1.set_ylim(0, 0.5)
    gpt.add_scale_bar(ax1, gdf_eq, loc="lower right")
    texts_eq = [t.get_text() for t in ax1.texts]
    plt.close(fig1)
    
    fig2, ax2 = plt.subplots()
    ax2.set_xlim(-10, -9.5)
    ax2.set_ylim(60, 60.5)
    gpt.add_scale_bar(ax2, gdf_60, loc="lower right")
    texts_60 = [t.get_text() for t in ax2.texts]
    plt.close(fig2)
    
    # Find the scale labels containing km/m
    label_eq = [t for t in texts_eq if "km" in t or "m" in t][0]
    label_60 = [t for t in texts_60 if "km" in t or "m" in t][0]
    
    # The equator label should be larger (~11 km) than the 60 degree label (~6 km)
    # due to the cosine shrinkage of longitude degrees at high latitudes.
    assert "11 km" in label_eq
    assert "6 km" in label_60

