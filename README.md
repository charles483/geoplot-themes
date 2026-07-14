# GeoPlot-Themes 🌍🎨

<p align="center">
  <img src="https://charles483.github.io/geoplot-themes/logo.png" alt="GeoPlot-Themes Logo" width="320"/>
</p>

<p align="center">
  <strong>Stunning pre-designed map themes, custom geographic colormaps, and cartographic templates for Matplotlib, Seaborn, and GeoPandas.</strong>
</p>

<p align="center">
  <a href="https://pypi.org/project/geoplot-themes/"><img src="https://img.shields.io/pypi/v/geoplot-themes.svg" alt="PyPI Version"/></a>
  <a href="https://pypi.org/project/geoplot-themes/"><img src="https://img.shields.io/pypi/pyversions/geoplot-themes.svg" alt="Python Versions"/></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"/></a>
  <a href="https://github.com/psf/black"><img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code Style: Black"/></a>
</p>

---

`geoplot-themes` bridges the gap between Python's data processing ecosystem (`GeoPandas`, `Shapely`, `Pandas`) and R's layout rendering engine (`ggplot2`, `ggspatial`, `ggnewscale`). Create publication-quality, aesthetically gorgeous maps instantly without spent hours tweaking grid lines, legend alignment, or north arrow coordinates.

## 🌟 Visual Showcase

### Handcrafted Cartographic Themes

| `natgeo_minimalist` (Cream/Editorial) | `retro_blueprint` (Classic Technical) | `dark_matter` (Neon/Dark Mode) |
| :---: | :---: | :---: |
| <img src="https://charles483.github.io/geoplot-themes/erosion_natgeo_minimalist_landscape.png" width="260" alt="NatGeo Minimalist"/> | <img src="https://charles483.github.io/geoplot-themes/erosion_retro_blueprint_landscape.png" width="260" alt="Retro Blueprint"/> | <img src="https://charles483.github.io/geoplot-themes/erosion_dark_matter_landscape.png" width="260" alt="Dark Matter"/> |

### Complex Vector Overlays with Independent Legends
A base raster (elevation/erosion) layered with multiple separate vector shapefiles (wetlands and rivers), featuring automatically styled, independent, conflict-free scales:
<p align="center">
  <img src="https://charles483.github.io/geoplot-themes/swamp_overlay_map.png" alt="Swamp and River Overlays Map" width="550"/>
</p>

---

## 🚀 Key Features

* **Pre-designed Themes**: Instantly switch visual aesthetics (`natgeo_minimalist`, `dark_matter`, `retro_blueprint`) without altering your plotting code.
* **Geographic Colormaps**: Built-in, science-backed palettes optimized for terrain (`elevation`), oceanography (`bathymetry`), technical grids (`blueprint`), and digital screens (`neon`).
* **Conflict-Free Legends**: Stack infinite shapefile layers (polygons, lines, points) with independent, color-coordinated legends.
* **Auto-Orientation & Fit**: Calculates data bounding boxes dynamically (`orientation="auto"`) to yield tightly cropped maps without margins or white padding.
* **Floating Inset Maps**: Sub-coordinate map inserts that automatically render a global or country-level context and draw a reference box of your zoom location.
* **Automatic Label Repulsion**: Non-overlapping text labels powered by `ggrepel` that cleanly connect text back to point coordinates.

---

## 📦 Installation

To install `geoplot-themes` with `uv` (recommended):
```bash
uv add geoplot-themes
```
Or via standard `pip`:
```bash
pip install geoplot-themes
```

---

## 📚 Documentation

For full documentation, including Quickstart guides, API reference, and detailed Design reference, please visit our official website:

**[https://charles483.github.io/geoplot-themes/](https://charles483.github.io/geoplot-themes/)**

---

## 🤝 Contributing & Support

Contributions are welcome! Please read the [Contributing Guidelines](CONTRIBUTING.md) and submit Pull Requests.

For questions, issues, or feedback, please contact us at **info@perurgeospatial.com**.

*Created and maintained by Perur Geospatial Solutions.*
