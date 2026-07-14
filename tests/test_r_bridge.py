"""Tests for the Python-to-R bridge module."""

import os
import pytest
from unittest import mock
import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon
import geoplot_themes as gpt
from geoplot_themes.r_bridge import (
    find_r_home,
    verify_r_environment,
    check_r_installation,
    check_r_packages,
    install_missing_r_packages,
    REQUIRED_R_PACKAGES,
)

def test_find_rscript():
    """Verify that we can locate the Rscript executable."""
    try:
        path = gpt.find_rscript()
        assert os.path.exists(path)
        assert "Rscript" in path
    except FileNotFoundError:
        # If R is not installed on the running environment, skip
        pytest.skip("R is not installed on the system")

def test_ensure_r_packages():
    """Test that we can run the package check/installation routine."""
    try:
        gpt.find_rscript()
    except FileNotFoundError:
        pytest.skip("R is not installed on the system")
        
    # Run the check (should succeed and print status)
    gpt.ensure_r_packages()

def test_plot_map_r(tmp_path):
    """Test plotting vector and points using the R backend."""
    try:
        gpt.find_rscript()
    except FileNotFoundError:
        pytest.skip("R is not installed on the system")

    # Generate mock vector data
    p1 = Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])
    p2 = Polygon([(10, 10), (20, 10), (20, 20), (10, 20)])
    gdf = gpd.GeoDataFrame({"val": [5.0, 10.0]}, geometry=[p1, p2], crs="EPSG:3857")

    # Generate mock points data
    pts_df = pd.DataFrame({
        "longitude": [5.0, 15.0],
        "latitude": [5.0, 15.0],
        "name": ["Point A", "Point B"],
        "class": [1, 2]
    })

    # Render map using R backend
    out_img = str(tmp_path / "map_test_r.png")
    result_path = gpt.plot_map_r(
        vector_data=gdf,
        vector_column="val",
        points_data=pts_df,
        points_color_column="class",
        points_label_column="name",
        theme="dark_matter",
        colormap="neon",
        title="R Mapping Test",
        output_path=out_img,
        scale_bar=True,
        north_arrow=True
    )

    assert result_path == out_img
    assert os.path.exists(out_img)
    assert os.path.getsize(out_img) > 0

# --- MOCK TESTS FOR Automatic Dependency Management ---

def test_missing_r_installation():
    """Test environment behavior when R is missing."""
    with mock.patch("geoplot_themes.r_bridge.find_r_home", side_effect=FileNotFoundError("R not found")):
        # Temporarily reset verification state
        with mock.patch("geoplot_themes.r_bridge._R_ENV_VERIFIED", False):
            # Verify R installation check returns False
            assert check_r_installation() is False
            
            # verify_r_environment should raise a user-friendly RuntimeError
            with pytest.raises(RuntimeError, match="R environment verification failed"):
                verify_r_environment()

def test_check_r_packages_all_installed():
    """Test behavior when all required packages are already installed."""
    with mock.patch("geoplot_themes.r_bridge.verify_r_environment") as mock_verify:
        with mock.patch("rpy2.robjects.r", return_value=[]) as mock_r:
            missing = check_r_packages()
            assert missing == []
            mock_verify.assert_called_once()

def test_check_r_packages_partial_installed():
    """Test behavior when packages are partially installed."""
    mock_installed = ["ggplot2", "sf"]
    mock_missing = [p for p in REQUIRED_R_PACKAGES if p not in mock_installed]
    with mock.patch("geoplot_themes.r_bridge.verify_r_environment"):
        with mock.patch("rpy2.robjects.r", return_value=mock_missing):
            missing = check_r_packages()
            assert set(missing) == set(mock_missing)

def test_install_missing_r_packages_fresh():
    """Test installation when all packages are missing (fresh machine)."""
    with mock.patch("geoplot_themes.r_bridge.verify_r_environment"):
        # First check returns all packages as missing, second check returns empty (installed)
        with mock.patch("geoplot_themes.r_bridge.check_r_packages", side_effect=[REQUIRED_R_PACKAGES, []]) as mock_check:
            with mock.patch("rpy2.robjects.packages.importr") as mock_importr:
                # Reset checked flag
                with mock.patch("geoplot_themes.r_bridge._R_PACKAGES_CHECKED", False):
                    install_missing_r_packages()
                    # Verify check was called twice (before & after install)
                    assert mock_check.call_count == 2
                    mock_importr.assert_called_with("utils")

def test_install_missing_r_packages_failure():
    """Test installer failure where packages remain missing after install."""
    with mock.patch("geoplot_themes.r_bridge.verify_r_environment"):
        # First check returns missing, second check also returns missing (failure)
        with mock.patch("geoplot_themes.r_bridge.check_r_packages", return_value=["ggplot2"]):
            with mock.patch("rpy2.robjects.packages.importr"):
                with mock.patch("geoplot_themes.r_bridge._R_PACKAGES_CHECKED", False):
                    with pytest.raises(RuntimeError, match="Verification failed.*ggplot2"):
                        install_missing_r_packages()

def test_install_missing_r_packages_offline():
    """Test installer behavior under offline conditions."""
    with mock.patch("geoplot_themes.r_bridge.verify_r_environment"):
        with mock.patch("geoplot_themes.r_bridge.check_r_packages", return_value=["ggplot2"]):
            # Mock importr to fail (simulating no internet or package load issues)
            with mock.patch("rpy2.robjects.packages.importr", side_effect=Exception("Connection timed out")):
                with mock.patch("geoplot_themes.r_bridge._R_PACKAGES_CHECKED", False):
                    with pytest.raises(RuntimeError, match="Connection timed out"):
                        install_missing_r_packages()
