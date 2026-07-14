"""Custom geographic-focused colormaps and color palettes."""

from typing import List, Dict
import matplotlib.colors as mcolors
from matplotlib.colors import LinearSegmentedColormap

# Raw hex-code palettes for different theme styles
PALETTES: Dict[str, List[str]] = {
    "elevation": [
        "#1b4332",  # Deep forest (sea level/plains)
        "#2d6a4f",  # Forest
        "#40916c",  # Light green
        "#d8f3dc",  # Valley/lowland (pale yellowish green)
        "#eed7a1",  # Foothills (dry tan)
        "#a98467",  # Mountain slopes (light brown)
        "#7f5539",  # Peaks (dark brown)
        "#f4f1de",  # Glaciers/snowcaps
    ],
    "bathymetry": [
        "#03045e",  # Abyssal (deepest navy)
        "#0077b6",  # Deep ocean
        "#00b4d8",  # Sea blue
        "#90e0ef",  # Shallow aqua
        "#caf0f8",  # Shoreline (very light cyan)
    ],
    "blueprint": [
        "#0a2540",  # Dark blueprint base
        "#113f67",  # Technical blue
        "#38598b",  # Grid blue
        "#87a7b3",  # Muted steel
        "#e7eaf6",  # Draft paper white
    ],
    "neon": [
        "#0f0c1b",  # Deep night sky
        "#31114b",  # Dark violet
        "#8a2be2",  # Neon purple
        "#ff007f",  # Hot pink
        "#00ffff",  # Neon cyan
    ],
    "editorial": [
        "#2b2d42",  # Charcoal text/border
        "#8d99ae",  # Slate gray
        "#edf2f4",  # Editorial white/beige
        "#c5a059",  # Cream gold
        "#3a5a40",  # Sage/olive green
    ]
}

# Generate Matplotlib colormaps from palettes
COLORMAPS: Dict[str, LinearSegmentedColormap] = {}
for name, colors in PALETTES.items():
    COLORMAPS[name] = LinearSegmentedColormap.from_list(f"geoplot_{name}", colors)

def get_colormap(name: str) -> LinearSegmentedColormap:
    """Retrieve a custom geographic colormap by name.
    
    Parameters
    ----------
    name : str
        The name of the colormap (e.g., 'elevation', 'bathymetry', 'blueprint', 'neon', 'editorial').
        
    Returns
    -------
    matplotlib.colors.LinearSegmentedColormap
        The requested Matplotlib colormap.
        
    Raises
    ------
    ValueError
        If the colormap name is not recognized.
    """
    cleaned_name = name.lower().strip()
    if cleaned_name not in COLORMAPS:
        raise ValueError(
            f"Colormap '{name}' not found. "
            f"Available colormaps are: {list(COLORMAPS.keys())}"
        )
    return COLORMAPS[cleaned_name]

def list_colormaps() -> List[str]:
    """Get a list of all available custom colormap names."""
    return list(COLORMAPS.keys())

def get_palette(name: str) -> List[str]:
    """Retrieve the raw hex-code color list for a palette.
    
    Parameters
    ----------
    name : str
        The name of the palette.
        
    Returns
    -------
    list of str
        List of hex color codes.
        
    Raises
    ------
    ValueError
        If the palette name is not recognized.
    """
    cleaned_name = name.lower().strip()
    if cleaned_name not in PALETTES:
        raise ValueError(
            f"Palette '{name}' not found. "
            f"Available palettes are: {list(PALETTES.keys())}"
        )
    return PALETTES[cleaned_name]
