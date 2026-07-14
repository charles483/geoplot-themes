"""GeoPlot-Themes: Stunning map themes and styling templates for Matplotlib, Seaborn, and GeoPandas."""

import matplotlib
from .colors import get_colormap, list_colormaps, get_palette, COLORMAPS
from .core import set_theme, reset_theme, list_themes, use_theme
from .geo import plot_map, add_scale_bar, add_north_arrow
from .r_bridge import (
    plot_map_r,
    find_rscript,
    ensure_r_packages,
    find_r_home,
    verify_r_environment,
    check_r_installation,
    check_r_packages,
    install_missing_r_packages,
)

# Register custom colormaps into Matplotlib's global colormap registry
# so they can be referenced globally by string name (e.g. cmap='geoplot_neon')
for cmap_name, cmap_obj in COLORMAPS.items():
    if hasattr(matplotlib, "colormaps"):
        try:
            matplotlib.colormaps.register(cmap_obj)
            # Also register with the raw name for convenience (e.g., 'elevation')
            import copy
            raw_cmap_obj = copy.copy(cmap_obj)
            raw_cmap_obj.name = cmap_name
            matplotlib.colormaps.register(raw_cmap_obj)
        except ValueError:
            # Already registered
            pass
    else:
        # Legacy support for older matplotlib versions
        import matplotlib.cm as colormap_registry
        try:
            colormap_registry.register_cmap(name=cmap_obj.name, cmap=cmap_obj)
            colormap_registry.register_cmap(name=cmap_name, cmap=cmap_obj)
        except ValueError:
            pass

__all__ = [
    "set_theme",
    "reset_theme",
    "list_themes",
    "use_theme",
    "get_colormap",
    "list_colormaps",
    "get_palette",
    "plot_map",
    "add_scale_bar",
    "add_north_arrow",
    "plot_map_r",
    "find_rscript",
    "ensure_r_packages",
    "find_r_home",
    "verify_r_environment",
    "check_r_installation",
    "check_r_packages",
    "install_missing_r_packages",
]
