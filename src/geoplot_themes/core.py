"""Core theme styling definitions and functions for Matplotlib."""

import matplotlib.pyplot as plt
from contextlib import contextmanager
from typing import Dict, Any, List, Generator

# Define style parameters for each theme
THEME_PARAMS: Dict[str, Dict[str, Any]] = {
    "dark_matter": {
        "figure.facecolor": "#090a0f",
        "axes.facecolor": "#090a0f",
        "text.color": "#d1d2d6",
        "axes.labelcolor": "#d1d2d6",
        "xtick.color": "#4d4f5c",
        "ytick.color": "#4d4f5c",
        "axes.grid": True,
        "grid.color": "#1f212d",
        "grid.linestyle": ":",
        "grid.linewidth": 0.8,
        "font.family": "sans-serif",
        "font.sans-serif": ["Inter", "DejaVu Sans", "Helvetica", "Arial", "sans-serif"],
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.spines.left": False,
        "axes.spines.bottom": False,
        "image.cmap": "geoplot_neon",
    },
    "retro_blueprint": {
        "figure.facecolor": "#0a2342",
        "axes.facecolor": "#0a2342",
        "text.color": "#ffffff",
        "axes.labelcolor": "#ffffff",
        "xtick.color": "#2c5282",
        "ytick.color": "#2c5282",
        "axes.grid": True,
        "grid.color": "#1a365d",
        "grid.linestyle": "-",
        "grid.linewidth": 0.6,
        "font.family": "monospace",
        "font.monospace": ["Courier New", "DejaVu Sans Mono", "Consolas", "monospace"],
        "axes.spines.top": True,
        "axes.spines.right": True,
        "axes.spines.left": True,
        "axes.spines.bottom": True,
        "axes.edgecolor": "#3182ce",
        "axes.linewidth": 1.0,
        "image.cmap": "geoplot_blueprint",
    },
    "natgeo_minimalist": {
        "figure.facecolor": "#fbf9f3",
        "axes.facecolor": "#fbf9f3",
        "text.color": "#1c1c1c",
        "axes.labelcolor": "#1c1c1c",
        "xtick.color": "#c4c2ba",
        "ytick.color": "#c4c2ba",
        "axes.grid": True,
        "grid.color": "#eadecf",
        "grid.linestyle": "--",
        "grid.linewidth": 0.5,
        "font.family": "serif",
        "font.serif": ["Georgia", "Times New Roman", "DejaVu Serif", "serif"],
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.spines.left": False,
        "axes.spines.bottom": False,
        "image.cmap": "geoplot_editorial",
    }
}

def set_theme(name: str) -> None:
    """Apply a custom geographic style theme globally to matplotlib.rcParams.
    
    Parameters
    ----------
    name : str
        The name of the theme to apply (e.g., 'dark_matter', 'retro_blueprint', 'natgeo_minimalist').
        
    Raises
    ------
    ValueError
        If the theme name is not recognized.
    """
    cleaned_name = name.lower().strip().replace(" ", "_")
    if cleaned_name not in THEME_PARAMS:
        raise ValueError(
            f"Theme '{name}' not found. "
            f"Available themes are: {list(THEME_PARAMS.keys())}"
        )
    
    # Apply settings
    plt.rcParams.update(THEME_PARAMS[cleaned_name])

def reset_theme() -> None:
    """Reset matplotlib style configurations to standard defaults."""
    plt.rcdefaults()

def list_themes() -> List[str]:
    """Get a list of all available theme names."""
    return list(THEME_PARAMS.keys())

@contextmanager
def use_theme(name: str) -> Generator[None, None, None]:
    """Context manager to apply a theme temporarily.
    
    Parameters
    ----------
    name : str
        The theme to apply during the execution block.
        
    Example
    -------
    >>> with use_theme('dark_matter'):
    ...     # plot operations here will be styled with dark_matter theme
    ...     pass
    """
    # Cache all current params
    original_params = plt.rcParams.copy()
    try:
        set_theme(name)
        yield
    finally:
        plt.rcParams.update(original_params)
