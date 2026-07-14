"""Example script demonstrating how to use GeoPlot-Themes to style maps."""

import os
import geopandas as gpd
from shapely.geometry import Polygon
import matplotlib.pyplot as plt
import numpy as np

import geoplot_themes as gpt

def generate_mock_geographic_data() -> gpd.GeoDataFrame:
    """Generate a clean, offline mock GeoDataFrame representing a grid city.
    
    The values represent a concentric density gradient (e.g. population density).
    """
    polygons = []
    values = []
    
    # Generate an 8x8 grid of neighborhoods
    for x in range(8):
        for y in range(8):
            # Create a square polygon representing a city block/tract
            # Coordinates represent a metric projection grid (e.g., in meters)
            x_min, y_min = x * 1000, y * 1000
            x_max, y_max = (x + 1) * 1000, (y + 1) * 1000
            
            p = Polygon([(x_min, y_min), (x_max, y_min), (x_max, y_max), (x_min, y_max)])
            polygons.append(p)
            
            # Central business district density model (peak in center)
            dist_from_center = np.sqrt((x - 3.5)**2 + (y - 3.5)**2)
            density = max(10, int(500 - dist_from_center * 110 + np.random.randint(-20, 20)))
            values.append(density)
            
    # Create GeoDataFrame with a metric Projected CRS (e.g. EPSG:3857 - Web Mercator)
    gdf = gpd.GeoDataFrame({"density": values}, geometry=polygons, crs="EPSG:3857")
    return gdf

def main():
    print("Generating mock geographic data...")
    gdf = generate_mock_geographic_data()
    
    # Ensure output directory exists for maps
    output_dir = "maps"
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Plot using Dark Matter theme
    print("\nPlotting map with 'dark_matter' theme...")
    fig, ax = plt.subplots(figsize=(8, 8))
    gpt.plot_map(
        gdf,
        column="density",
        theme="dark_matter",
        colormap="neon",
        ax=ax,
        title="Urban Population Density - Dark Matter Theme",
        legend=True,
        scale_bar=True,
        north_arrow=True,
        edgecolor="#1c1c24",
        linewidth=0.5
    )
    dark_map_path = os.path.join(output_dir, "map_dark_matter.png")
    plt.savefig(dark_map_path, dpi=150, bbox_inches="tight")
    print(f"Saved: {dark_map_path}")
    plt.close()
    
    # 2. Plot using Retro Blueprint theme
    print("Plotting map with 'retro_blueprint' theme...")
    fig, ax = plt.subplots(figsize=(8, 8))
    gpt.plot_map(
        gdf,
        column="density",
        theme="retro_blueprint",
        colormap="blueprint",
        ax=ax,
        title="Technical Blueprint Layout",
        legend=True,
        scale_bar=True,
        north_arrow=True,
        show_coords=True,
        edgecolor="#3182ce",
        linewidth=0.8
    )
    blueprint_map_path = os.path.join(output_dir, "map_retro_blueprint.png")
    plt.savefig(blueprint_map_path, dpi=150, bbox_inches="tight")
    print(f"Saved: {blueprint_map_path}")
    plt.close()
    
    # 3. Plot using National Geographic Minimalist theme
    print("Plotting map with 'natgeo_minimalist' theme...")
    fig, ax = plt.subplots(figsize=(8, 8))
    gpt.plot_map(
        gdf,
        column="density",
        theme="natgeo_minimalist",
        colormap="elevation",
        ax=ax,
        title="Editorial Geography - Minimalist Theme",
        legend=True,
        scale_bar=True,
        north_arrow=True,
        edgecolor="#e3e1d9",
        linewidth=0.5
    )
    natgeo_map_path = os.path.join(output_dir, "map_natgeo_minimalist.png")
    plt.savefig(natgeo_map_path, dpi=150, bbox_inches="tight")
    print(f"Saved: {natgeo_map_path}")
    plt.close()
    
    print("\nAll maps plotted successfully!")
    print(f"Checkout the output images under '{output_dir}/'")

if __name__ == "__main__":
    main()
