# GeoPlot-Themes 🌍🎨

Stunning pre-designed map themes, custom geographic colormaps, and cartographic templates for **Matplotlib**, **Seaborn**, and **GeoPandas**.

Create beautiful, publication-ready map layouts instantly with proper scales, north arrows, and custom-styled legends.

---

## Features

### 🌟 Pre-designed Themes
- **`dark_matter`**: High-contrast neon cyan/magenta styling on a near-black grid background.
- **`retro_blueprint`**: Classic technical styling with blueprint navy background, white grids, and technical font borders.
- **`natgeo_minimalist`**: Elegant editorial style with neutral cream background, muted gray grid borders, and serif typography.

### 🎨 Custom Geographic Colormaps
- **`elevation`**: Muted greens transitioning through valleys, foothills, brown slopes, and white snowcaps.
- **`bathymetry`**: Deep oceanic blues transitioning to cyan and pale shoreline values.
- **`blueprint`**: Technical blue gradients matching the blueprint aesthetic.
- **`neon`**: striking cyberpunk dark-mode gradients (magenta, cyan, dark violet).
- **`editorial`**: Sage green, slate gray, charcoal, and warm cream gold.

### 📍 Built-in Cartographic Utilities
- **`plot_map()`**: High-level wrapper that configures borders, styles legends, applies themes/colormaps, and adds scales and north arrows.
- **`add_scale_bar()`**: Adds a scale bar that automatically calculates and rounds lengths in meters (for projected CRS) or degrees (for geographic CRS).
- **`add_north_arrow()`**: Adds a clean, customizable north arrow pointing upwards.

---

## Installation

Using `uv`:
```bash
uv pip install -e .
```
Or standard `pip`:
```bash
pip install -e .
```

---

## Quickstart

Use the high-level `plot_map` function to instantly render beautiful geographic data:

```python
import geopandas as gpd
import geoplot_themes as gpt
import matplotlib.pyplot as plt

# Load your GeoDataFrame (must have a valid CRS)
gdf = gpd.read_file("your_shapefile.shp")

# Plot using the Retro Blueprint theme
fig, ax = plt.subplots(figsize=(10, 8))
gpt.plot_map(
    gdf,
    column="your_data_column",
    theme="retro_blueprint",
    colormap="blueprint",
    ax=ax,
    title="Technical Project Layout",
    scale_bar=True,
    north_arrow=True
)
plt.show()
```

### Context Manager (Temporary Themes)
Style matplotlib plots temporarily without modifying global configurations:

```python
with gpt.use_theme("dark_matter"):
    # Any normal Matplotlib, Seaborn or GeoPandas plotting here 
    # will automatically inherit the Dark Matter style!
    gdf.plot(cmap="geoplot_neon", legend=True)
    plt.title("Temporary Dark Theme Map")
```

---

## API Reference Overview

- `set_theme(name: str)`: Apply a theme globally to `plt.rcParams`.
- `reset_theme()`: Revert style configurations to default matplotlib settings.
- `list_themes() -> list[str]`: List all available custom theme names.
- `use_theme(name: str)`: Context manager for temporary styling.
- `get_colormap(name: str)`: Get a custom Colormap object.
- `list_colormaps() -> list[str]`: List all available geographic colormaps.
- `plot_map(gdf, ...)`: Draw styled maps with comprehensive cartographic additions.


---

## R / ggplot2 Integration 📊🎨

`geoplot-themes` includes a robust, native R/ggplot2 mapping backend. This allows Python users to render highly professional, publication-ready maps using R, ggplot2, `sf`, `raster`, `ggrepel`, and `ggspatial` from within Python.

### Requirements
- **R** must be installed on your system (the package will automatically search in standard locations, registry keys, and your `PATH`).
- Python libraries: `geopandas`, `pandas`, `shapely`.

The package will automatically install any missing required R packages (`ggplot2`, `sf`, `raster`, `ggrepel`, `ggspatial`) to a local `.r_libs` folder inside the workspace.

### R / ggplot2 Quickstart

You can render combined maps featuring vector layers (shapefiles or GeoDataFrames), continuous raster layers (GeoTIFFs), and labeled point layers using `plot_map_r()`:

```python
import geoplot_themes as gpt

# Auto-detect R and install required R packages
gpt.ensure_r_packages()

# Render a professional map using R backend
gpt.plot_map_r(
    vector_data="your_neighborhoods.geojson",
    vector_column="population_density",
    raster_data="your_temperature.tif",
    points_data="your_frog_sites.csv",
    points_color_column="species_presence",
    points_label_column="site_name",
    theme="dark_matter",
    colormap="neon",
    title="Species Distribution & Heatmap",
    output_path="maps/professional_r_map.png"
)
```

### R API Reference Overview
- `find_rscript() -> str`: Locate the Rscript executable on Windows.
- `ensure_r_packages()`: Non-interactively check and install R package dependencies to a local `.r_libs` library folder.
- `plot_map_r(vector_data, raster_data, points_data, theme, colormap, ...)`: High-level Python wrapper to plot and save publication-quality maps using R/ggplot2.

---

## Running Tests

Run the test suite using `uv`:
```bash
uv run pytest
```
