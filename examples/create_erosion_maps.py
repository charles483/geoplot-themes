import os
import geoplot_themes as gpt

raster_path = r"G:\Final_Erosion\erosion_probability_2014.tif"
output_dir = "maps"
os.makedirs(output_dir, exist_ok=True)

print(f"Verifying existence of raster: {raster_path}")
if not os.path.exists(raster_path):
    print(f"Error: File '{raster_path}' does not exist or is not readable.")
    exit(1)

# Define the list of themes, colormaps, and orientations
configurations = [
    # (theme, colormap)
    ("natgeo_minimalist", "elevation"),
    ("dark_matter", "neon"),
    ("retro_blueprint", "blueprint")
]
orientations = ["landscape", "portrait"]
author_name = "Perur Geospatial Solutions"

print(f"\nStarting map generation for all themes with author: '{author_name}'...")

for theme, colormap in configurations:
    for orient in orientations:
        filename = f"erosion_{theme}_{orient}.png"
        out_path = os.path.join(output_dir, filename)
        print(f"\n- Rendering theme: '{theme}' | orientation: '{orient}'...")
        try:
            gpt.plot_map_r(
                raster_data=raster_path,
                theme=theme,
                colormap=colormap,
                title=f"Erosion Probability (2014) - {theme.replace('_', ' ').title()}",
                subtitle=f"Susceptibility Index Modeling and Soil Runoff Risk ({orient.title()} Layout)",
                author=author_name,
                data_source="Regional Soil Stability Surveys",
                date="July 2026",
                scale_bar_style="minimal" if theme == "natgeo_minimalist" else ("dark" if theme == "dark_matter" else "blueprint"),
                north_arrow_style="natgeo" if theme == "natgeo_minimalist" else ("dark_neon" if theme == "dark_matter" else "blueprint"),
                orientation=orient,
                show_coords=True,
                output_path=out_path
            )
            print(f"  Saved: {out_path}")
        except Exception as e:
            print(f"  Failed to render mapping combination: {e}")

print("\nMap generation complete for all combinations!")
