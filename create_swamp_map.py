import os
import geoplot_themes as gpt

def main():
    print("Testing map with multiple vector overlays (swamp and river)...")
    
    raster_file = r"G:\GIS4.1\Project\others\swamp\Objective2\Carbon_Sequestration\ensembe\ensemble_carbon_2025.tif"
    
    extra_vectors = [
        {
            "data": r"G:\GIS4.1\Project\others\swamp\swamp.shp",
            "name": "Wetlands",
            "fill": "#2d5a27",
            "color": "NA",
            "alpha": 0.6
        },
        {
            "data": r"G:\GIS4.1\Project\others\swamp\river.shp",
            "name": "Rivers",
            "color": "#1f78b4",
            "linewidth": 1.2
        }
    ]
    
    output_path = os.path.join(os.getcwd(), "maps", "swamp_overlay_map.png")
    
    gpt.plot_map_r(
        raster_data=raster_file,
        extra_vectors=extra_vectors,
        theme="natgeo_minimalist",
        colormap="elevation",
        title="Erosion Probability with Wetlands & Rivers",
        subtitle="Example using extra_vectors feature",
        output_path=output_path,
        show_coords=False,
        scale_bar=True,
        north_arrow=True,
        orientation="auto",
        author="Perur Geospatial Solutions",
        inset_map=r"G:\GIS4.1\Project\others\swamp\river.shp"
    )
    
    print(f"Map successfully generated and saved to: {output_path}")

if __name__ == "__main__":
    main()
