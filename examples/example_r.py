"""Example script demonstrating how to use the R/ggplot2 backend in GeoPlot-Themes."""

import os
import subprocess
import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon
import numpy as np

import geoplot_themes as gpt

def generate_mock_vector_data() -> gpd.GeoDataFrame:
    """Generate mock neighborhood grid data."""
    polygons = []
    values = []
    for x in range(8):
        for y in range(8):
            x_min, y_min = 149.07 + x * 0.015, -35.31 + y * 0.01
            x_max, y_max = 149.07 + (x + 1) * 0.015, -35.31 + (y + 1) * 0.01
            p = Polygon([(x_min, y_min), (x_max, y_min), (x_max, y_max), (x_min, y_max)])
            polygons.append(p)
            # Central gradient
            dist = np.sqrt((x - 3.5)**2 + (y - 3.5)**2)
            values.append(int(100 - dist * 20 + np.random.randint(-5, 5)))
    return gpd.GeoDataFrame({"density": values}, geometry=polygons, crs="EPSG:4326")

def generate_mock_points_data() -> pd.DataFrame:
    """Generate mock point/site locations."""
    return pd.DataFrame({
        "site_code": ["ANU004", "ANU018", "ANU022", "HAN100", "MOL200", "COK100"],
        "longitude": [149.11, 149.12, 149.13, 149.15, 149.09, 149.16],
        "latitude": [-35.28, -35.27, -35.29, -35.26, -35.30, -35.28],
        "depth": ["deep", "shallow", "deep", "shallow", "deep", "shallow"]
    })

def generate_mock_raster_file(rscript_path: str, output_path: str, lib_dir: str) -> None:
    """Run a small R script to write a mock GeoTIFF raster file."""
    output_path_clean = output_path.replace("\\", "/")
    lib_dir_clean = lib_dir.replace("\\", "/")
    r_code = f"""
    .libPaths(c("{lib_dir_clean}", .libPaths()))
    library(raster)
    # Define a grid corresponding to Canberra coordinates
    r <- raster(ncols=15, nrows=15, xmn=149.07, xmx=149.19, ymn=-35.31, ymx=-35.25)
    # Fill with a temperature gradient (warmer towards top-right)
    xy <- xyFromCell(r, 1:ncell(r))
    values(r) <- 5.5 + (xy[,1] - 149.07)*10 - (xy[,2] + 35.31)*10 + runif(ncell(r), -0.5, 0.5)
    crs(r) <- "+proj=longlat +datum=WGS84 +no_defs"
    writeRaster(r, filename="{output_path_clean}", format="GTiff", overwrite=TRUE)
    """
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".R", delete=False) as f:
        f.write(r_code)
        script_name = f.name
    try:
        subprocess.run([rscript_path, script_name], check=True, capture_output=True)
    finally:
        if os.path.exists(script_name):
            os.remove(script_name)

def main():
    print("Checking for R installation...")
    try:
        rscript_path = gpt.find_rscript()
        print(f"Rscript found: {rscript_path}")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("R is required to run the R mapping backend. Skipping example.")
        return

    # Set up local R libraries
    pkg_dir = os.path.dirname(os.path.abspath(gpt.__file__))
    lib_dir = os.path.join(os.path.dirname(os.path.dirname(pkg_dir)), ".r_libs")
    
    print("\nEnsuring required R packages are installed...")
    gpt.ensure_r_packages(rscript_path=rscript_path, lib_dir=lib_dir)

    print("\nGenerating mock data...")
    gdf_vec = generate_mock_vector_data()
    df_pts = generate_mock_points_data()
    
    output_dir = "maps"
    os.makedirs(output_dir, exist_ok=True)
    raster_path = os.path.join(output_dir, "mock_temp_raster.tif")
    
    print("Creating mock raster file using R...")
    generate_mock_raster_file(rscript_path, raster_path, lib_dir)
    print(f"Raster saved: {raster_path}")

    # 1. Dark Matter theme (combining Raster, Vector, and Points) - Landscape layout with locator inset
    print("\n1. Rendering map with 'dark_matter' theme...")
    out_dark = os.path.join(output_dir, "map_dark_matter_r.png")
    gpt.plot_map_r(
        vector_data=gdf_vec,
        vector_column="density",
        raster_data=raster_path,
        points_data=df_pts,
        points_color_column="depth",
        points_label_column="site_code",
        theme="dark_matter",
        colormap="neon",
        title="Canberra Microclimate & Density Analysis",
        subtitle="Urban Heat Island Intensity & Resident Survey Locations",
        author="Antigravity Cartography Lab",
        data_source="ACT Spatial Data & Landsat Open Archive",
        date="July 2026",
        scale_bar_style="dark",
        north_arrow_style="dark_neon",
        orientation="landscape",
        inset=True,
        output_path=out_dark,
        rscript_path=rscript_path,
        lib_dir=lib_dir
    )
    print(f"Saved: {out_dark}")

    # 2. Retro Blueprint theme (combining Vector and Points) - Square Technical layout
    print("\n2. Rendering map with 'retro_blueprint' theme...")
    out_blueprint = os.path.join(output_dir, "map_retro_blueprint_r.png")
    gpt.plot_map_r(
        vector_data=gdf_vec,
        vector_column="density",
        points_data=df_pts,
        points_color_column="depth",
        theme="retro_blueprint",
        colormap="blueprint",
        title="Canberra Engineering Layout Plan",
        subtitle="Topographical Network Grid & Drainage Level Surveys",
        author="Lead Principal GIS Engineer",
        data_source="Internal Topographic CAD Repository V3",
        date="2026-07-12",
        scale_bar_style="blueprint",
        north_arrow_style="blueprint",
        orientation="square",
        output_path=out_blueprint,
        rscript_path=rscript_path,
        lib_dir=lib_dir
    )
    print(f"Saved: {out_blueprint}")

    # 3. National Geographic Minimalist theme (combining Raster and Points) - Portrait Editorial layout with inset
    print("\n3. Rendering map with 'map_natgeo_minimalist_r.png'...")
    out_natgeo = os.path.join(output_dir, "map_natgeo_minimalist_r.png")
    gpt.plot_map_r(
        raster_data=raster_path,
        points_data=df_pts,
        points_color_column="depth",
        points_label_column="site_code",
        theme="natgeo_minimalist",
        colormap="elevation",
        title="Editorial Geography of Canberra",
        subtitle="Muted elevation profiles with wildlife observation points",
        author="National Geographic Society / Cartography Dept",
        data_source="Geoscience Australia Data Center",
        date="12 July 2026",
        scale_bar_style="natgeo",
        north_arrow_style="natgeo",
        orientation="portrait",
        inset=True,
        output_path=out_natgeo,
        rscript_path=rscript_path,
        lib_dir=lib_dir
    )
    print(f"Saved: {out_natgeo}")

    print("\nAll R/ggplot2 maps generated successfully under 'maps/'!")

if __name__ == "__main__":
    main()
