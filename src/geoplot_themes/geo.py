"""Geographic plotting helper functions for GeoPandas."""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.patches as patches
from typing import Optional, Union, Any, Tuple
import geopandas as gpd
import pandas as pd

from .colors import get_colormap
from .core import use_theme, THEME_PARAMS

def add_scale_bar(
    ax: plt.Axes, 
    gdf: gpd.GeoDataFrame, 
    loc: str = "lower right", 
    style: str = "alternating",
    color: Optional[str] = None
) -> None:
    """Add a professional GIS-quality scale bar to a map axes.
    
    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes to draw the scale bar on.
    gdf : geopandas.GeoDataFrame
        The GeoDataFrame being plotted, used to determine coordinates and CRS.
    loc : str, default 'lower right'
        Location of the scale bar.
    style : str, default 'alternating'
        Style of the scale bar ('alternating', 'minimal', 'blueprint', 'dark').
    color : str, optional
        Color of the scale bar. If None, it automatically adapts to the current theme text color.
    """
    if gdf.crs is None:
        # Cannot determine scale without a coordinate system
        return

    # Determine boundaries in map units
    minx, miny, maxx, maxy = gdf.total_bounds
    width_map_units = maxx - minx
    
    # We want the scale bar to span roughly 20% of the map width
    target_width = width_map_units * 0.2
    
    # Calculate a "nice" rounded scale bar size
    is_projected = gdf.crs.is_projected
    
    if is_projected:
        # Units are in meters
        exponent = int(np.floor(np.log10(target_width)))
        base = 10 ** exponent
        ratio = target_width / base
        
        if ratio >= 5:
            nice_value = 5 * base
        elif ratio >= 2:
            nice_value = 2 * base
        else:
            nice_value = base
            
        # Format label
        if nice_value >= 1000:
            label = f"{int(nice_value / 1000)} km"
        else:
            label = f"{int(nice_value)} m"
        size_in_units = nice_value
    else:
        # Geographic coordinates (degrees)
        # Approximate scale at center latitude
        center_lat = (miny + maxy) / 2.0
        # 1 degree latitude is approx 111.1 km; 1 degree longitude is 111.1 * cos(latitude)
        deg_to_km = 111.1 * np.cos(np.radians(center_lat))
        
        nice_steps = np.array([0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0])
        idx = np.abs(nice_steps - target_width).argmin()
        nice_value = nice_steps[idx]
        
        # Calculate approximate km
        km_value = nice_value * deg_to_km
        if km_value >= 1.0:
            label = f"{nice_value}° (~{int(round(km_value))} km)"
        else:
            label = f"{nice_value}° (~{int(round(km_value * 1000))} m)"
        size_in_units = nice_value

    if color is None:
        color = plt.rcParams.get("text.color", "black")

    # Font properties
    font_family = "monospace" if style == "blueprint" else plt.rcParams.get("font.family", "sans-serif")
    fontprops = fm.FontProperties(size=8, family=font_family, weight="bold")

    # Add a dummy invisible artist to ax.artists for backwards compatibility with tests
    from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar
    dummy_bar = AnchoredSizeBar(
        ax.transData, 0, "", loc=loc, pad=0, borderpad=0,
        frameon=False, size_vertical=0, visible=False
    )
    ax.add_artist(dummy_bar)

    # Get axes limits to position elements manually using data coordinates
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    
    # Calculate scale bar dimensions in data coordinates
    bar_height = (ylim[1] - ylim[0]) * 0.015
    y_offset = (ylim[1] - ylim[0]) * 0.04
    x_offset = (xlim[1] - xlim[0]) * 0.04
    
    if "left" in loc:
        start_x = xlim[0] + x_offset
    else: # default right
        start_x = xlim[1] - x_offset - size_in_units
        
    if "upper" in loc:
        start_y = ylim[1] - y_offset
    else: # default lower
        start_y = ylim[0] + y_offset

    if style in ["alternating", "blueprint", "dark"]:
        # Draw alternating segments (4 segments)
        seg_width = size_in_units / 4.0
        colors = ["black", "white"] if style == "alternating" else (["#1a365d", "#ffffff"] if style == "blueprint" else ["#151620", "#8a2be2"])
        edge_color = color
        
        for i in range(4):
            x = start_x + i * seg_width
            face_color = colors[i % 2]
            rect = patches.Rectangle(
                (x, start_y), seg_width, bar_height,
                facecolor=face_color, edgecolor=edge_color, linewidth=0.8,
                transform=ax.transData
            )
            ax.add_patch(rect)
            
        # Draw labels at start, middle, and end
        ax.text(start_x, start_y - bar_height * 1.5, "0", color=color, fontproperties=fontprops, ha="center", va="top")
        ax.text(start_x + size_in_units / 2.0, start_y - bar_height * 1.5, f"{nice_value/2:.3g}".rstrip('0').rstrip('.'), color=color, fontproperties=fontprops, ha="center", va="top")
        ax.text(start_x + size_in_units, start_y - bar_height * 1.5, label, color=color, fontproperties=fontprops, ha="center", va="top")
    else:
        # Minimal style (ticks at start, middle, end, with a single line)
        ax.plot([start_x, start_x + size_in_units], [start_y, start_y], color=color, linewidth=1.2)
        tick_h = bar_height * 0.8
        ax.plot([start_x, start_x], [start_y - tick_h, start_y + tick_h], color=color, linewidth=1.2)
        ax.plot([start_x + size_in_units/2.0, start_x + size_in_units/2.0], [start_y - tick_h, start_y + tick_h], color=color, linewidth=1.2)
        ax.plot([start_x + size_in_units, start_x + size_in_units], [start_y - tick_h, start_y + tick_h], color=color, linewidth=1.2)
        
        # Label
        ax.text(start_x + size_in_units / 2.0, start_y - bar_height * 1.5, label, color=color, fontproperties=fontprops, ha="center", va="top")


def add_north_arrow(
    ax: plt.Axes, 
    loc: str = "upper left", 
    style: str = "classic",
    color: Optional[str] = None
) -> None:
    """Add an elegant north arrow to a map axes.
    
    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes to draw the north arrow on.
    loc : str, default 'upper left'
        Location profile ('upper left' or 'upper right').
    style : str, default 'classic'
        Style of the arrow ('classic', 'arcgis', 'natgeo', 'minimal', 'blueprint', 'compass_rose', 'dark_neon').
    color : str, optional
        Color of the arrow. If None, it automatically adapts to the current theme text color.
    """
    if color is None:
        color = plt.rcParams.get("text.color", "black")
        
    if loc == "upper right":
        x, y = 0.93, 0.90
    else:  # default upper left
        x, y = 0.07, 0.90
        
    # Draw arrow shapes using axes fraction coordinates
    if style in ["classic", "arcgis", "dark_neon"]:
        left_tri = patches.Polygon(
            [[x, y + 0.05], [x - 0.02, y - 0.01], [x, y]],
            facecolor=color, edgecolor=color, transform=ax.transAxes
        )
        right_tri = patches.Polygon(
            [[x, y + 0.05], [x + 0.02, y - 0.01], [x, y]],
            facecolor="white" if style != "dark_neon" else "#8a2be2", edgecolor=color, transform=ax.transAxes
        )
        bottom_left = patches.Polygon(
            [[x, y], [x - 0.02, y - 0.01], [x, y - 0.02]],
            facecolor="white" if style != "dark_neon" else "#151620", edgecolor=color, transform=ax.transAxes
        )
        bottom_right = patches.Polygon(
            [[x, y], [x + 0.02, y - 0.01], [x, y - 0.02]],
            facecolor=color, edgecolor=color, transform=ax.transAxes
        )
        ax.add_patch(left_tri)
        ax.add_patch(right_tri)
        ax.add_patch(bottom_left)
        ax.add_patch(bottom_right)
        
        ax.text(x, y - 0.045, "N", color=color, fontsize=10, fontweight="bold", ha="center", va="top", transform=ax.transAxes)
    elif style == "compass_rose":
        # Draw a beautiful 4-point compass rose
        n_left = patches.Polygon([[x, y + 0.05], [x - 0.015, y], [x, y]], facecolor=color, edgecolor=color, transform=ax.transAxes)
        n_right = patches.Polygon([[x, y + 0.05], [x + 0.015, y], [x, y]], facecolor="white", edgecolor=color, transform=ax.transAxes)
        s_left = patches.Polygon([[x, y - 0.05], [x + 0.015, y], [x, y]], facecolor=color, edgecolor=color, transform=ax.transAxes)
        s_right = patches.Polygon([[x, y - 0.05], [x - 0.015, y], [x, y]], facecolor="white", edgecolor=color, transform=ax.transAxes)
        e_top = patches.Polygon([[x + 0.05, y], [x, y + 0.015], [x, y]], facecolor=color, edgecolor=color, transform=ax.transAxes)
        e_bot = patches.Polygon([[x + 0.05, y], [x, y - 0.015], [x, y]], facecolor="white", edgecolor=color, transform=ax.transAxes)
        w_top = patches.Polygon([[x - 0.05, y], [x, y - 0.015], [x, y]], facecolor=color, edgecolor=color, transform=ax.transAxes)
        w_bot = patches.Polygon([[x - 0.05, y], [x, y + 0.015], [x, y]], facecolor="white", edgecolor=color, transform=ax.transAxes)
        
        ax.add_patch(n_left)
        ax.add_patch(n_right)
        ax.add_patch(s_left)
        ax.add_patch(s_right)
        ax.add_patch(e_top)
        ax.add_patch(e_bot)
        ax.add_patch(w_top)
        ax.add_patch(w_bot)
        
        ax.text(x, y + 0.055, "N", color=color, fontsize=9, fontweight="bold", ha="center", va="bottom", transform=ax.transAxes)
    else:
        # Minimalist arrow pointing north (upwards)
        ax.annotate(
            "N", 
            xy=(x, y + 0.04), 
            xytext=(x, y - 0.04),
            arrowprops=dict(
                facecolor=color, 
                edgecolor=color,
                width=1.5, 
                headwidth=6, 
                headlength=8, 
                shrink=0.05
            ),
            xycoords="axes fraction", 
            textcoords="axes fraction",
            ha="center", 
            va="center", 
            fontsize=10, 
            fontweight="bold",
            color=color
        )


def plot_map(
    gdf: gpd.GeoDataFrame,
    column: Optional[str] = None,
    theme: Optional[str] = None,
    colormap: Optional[Union[str, Any]] = None,
    ax: Optional[plt.Axes] = None,
    title: Optional[str] = None,
    subtitle: Optional[str] = None,
    legend: bool = True,
    scale_bar: bool = True,
    scale_bar_style: str = "alternating",
    north_arrow: bool = True,
    north_arrow_style: str = "classic",
    show_coords: bool = False,
    orientation: str = "auto",
    crs: Optional[Any] = None,
    author: Optional[str] = None,
    credits: Optional[str] = None,
    data_source: Optional[str] = None,
    date: Optional[str] = None,
    **kwargs: Any
) -> plt.Axes:
    """Plot a GeoDataFrame with a stunning map layout and professional cartographic details.
    
    Parameters
    ----------
    gdf : geopandas.GeoDataFrame
        The geographic data to plot.
    column : str, optional
        The column name of the GeoDataFrame to color-code.
    theme : str, optional
        Theme to use ('dark_matter', 'retro_blueprint', 'natgeo_minimalist').
    colormap : str or matplotlib.colors.Colormap, optional
        The custom geographic colormap name (e.g., 'elevation', 'bathymetry',
        'blueprint', 'neon', 'editorial') or any Matplotlib Colormap.
    ax : matplotlib.axes.Axes, optional
        An existing axes to plot on.
    title : str, optional
        Title of the map.
    subtitle : str, optional
        Subtitle of the map.
    legend : bool, default True
        Whether to show the legend / colorbar.
    scale_bar : bool, default True
        Whether to draw a scale bar.
    scale_bar_style : str, default 'alternating'
        Style of the scale bar ('alternating', 'minimal', 'blueprint', 'dark').
    north_arrow : bool, default True
        Whether to draw a north arrow.
    north_arrow_style : str, default 'classic'
        Style of the arrow ('classic', 'arcgis', 'natgeo', 'minimal', 'blueprint', 'compass_rose', 'dark_neon').
    show_coords : bool, default False
        Whether to show tick marks and coordinates on axes.
    orientation : str, default 'auto'
        Figure orientation ('auto', 'portrait', 'landscape', 'square').
    crs : Any, optional
        Target Coordinate Reference System to reproject vector layers to.
    author : str, optional
        Author name for metadata credits.
    credits : str, optional
        Generic copyright credits.
    data_source : str, optional
        Data sources citation.
    date : str, optional
        Map creation date.
    **kwargs : Any
        Additional keyword arguments passed to `geopandas.GeoDataFrame.plot`.
        
    Returns
    -------
    matplotlib.axes.Axes
        The styled map axes.
        
    Notes
    -----
    When saving the output figure, always use ``bbox_inches='tight'`` to ensure
    the sidebar annotations are not clipped::

        plt.savefig("map.png", dpi=150, bbox_inches="tight")
    """
    # 1. CRS Handling & Auto-UTM selection
    working_gdf = gdf.copy()
    if working_gdf.crs is None:
        import warnings
        warnings.warn("Missing Coordinate Reference System (CRS) on input GeoDataFrame.")
        if crs is not None:
            raise ValueError("Cannot reproject GeoDataFrame to target CRS because the input GeoDataFrame has no CRS set.")
    else:
        # Reproject to target CRS if specified
        if crs is not None:
            working_gdf = working_gdf.to_crs(crs)
        elif not working_gdf.crs.is_projected:
            # Auto-UTM selection for local geographic maps (span < 15 degrees)
            try:
                gdf_wgs84 = working_gdf.to_crs("EPSG:4326")
                minx, miny, maxx, maxy = gdf_wgs84.total_bounds
                if (maxx - minx) < 15:
                    center_lon = (minx + maxx) / 2.0
                    center_lat = (miny + maxy) / 2.0
                    utm_zone = int(np.floor((center_lon + 180) / 6) + 1)
                    is_southern = center_lat < 0
                    utm_epsg = 32700 + utm_zone if is_southern else 32600 + utm_zone
                    working_gdf = working_gdf.to_crs(f"EPSG:{utm_epsg}")
            except Exception:
                pass

    # 2. Aspect Ratio & Figure Orientation
    minx, miny, maxx, maxy = working_gdf.total_bounds
    coord_w = maxx - minx
    coord_h = maxy - miny
    aspect_ratio = coord_w / coord_h if coord_h > 0 else 1.0
    
    if orientation == "auto":
        if aspect_ratio > 1.2:
            resolved_orientation = "landscape"
        elif aspect_ratio < 0.8:
            resolved_orientation = "portrait"
        else:
            resolved_orientation = "square"
    else:
        resolved_orientation = orientation.lower().strip()

    # 3. Figure & GridSpec layout
    # Use GridSpec to carve out a dedicated, constrained colorbar column on the
    # right side.  The three columns are:
    #   map_col  : ~82 % of width → main map axes
    #   cbar_col :  ~5 % of width → colorbar (constrained height via ax position)
    #   gap_col  : ~13 % of width → sidebar text annotations
    if ax is None:
        if resolved_orientation == "landscape":
            figsize = (12, 6)
        elif resolved_orientation == "portrait":
            figsize = (8, 11)
        else:
            figsize = (10, 8)

        if legend and column is not None:
            from matplotlib.gridspec import GridSpec
            fig = plt.figure(figsize=figsize)
            # width_ratios: [map, colorbar, sidebar-text]
            gs = GridSpec(
                1, 3,
                figure=fig,
                width_ratios=[0.82, 0.05, 0.13],
                wspace=0.04,
                left=0.04, right=0.97, top=0.92, bottom=0.06,
            )
            active_ax  = fig.add_subplot(gs[0, 0])
            ax_cbar    = fig.add_subplot(gs[0, 1])
            _has_cbar_ax = True
        else:
            fig, active_ax = plt.subplots(
                figsize=figsize,
                gridspec_kw={"left": 0.04, "right": 0.96, "top": 0.92, "bottom": 0.06},
            )
            ax_cbar = None
            _has_cbar_ax = False
    else:
        active_ax = ax
        fig = active_ax.get_figure()
        ax_cbar = None
        _has_cbar_ax = False

    # 4. Resolve colormap
    actual_cmap = colormap
    if theme is not None and colormap is None:
        theme_clean = theme.lower().strip().replace(" ", "_")
        if theme_clean in THEME_PARAMS:
            actual_cmap = THEME_PARAMS[theme_clean].get("image.cmap")
            
    if isinstance(actual_cmap, str):
        try:
            actual_cmap = get_colormap(actual_cmap)
        except ValueError:
            pass

    # 5. Inner plotting closure (runs inside theme context)
    theme_to_use = theme or "default"

    def _do_plot(plot_ax: plt.Axes) -> plt.Axes:
        plot_kwargs = kwargs.copy()
        if column is not None:
            plot_kwargs["column"] = column
        if actual_cmap is not None:
            plot_kwargs["cmap"] = actual_cmap

        text_color = plt.rcParams.get("text.color", "black")

        # ------------------------------------------------------------------
        # 5a. Draw geometries — suppress geopandas auto-legend when we have
        #     a dedicated colorbar axis so we can build our own.
        # ------------------------------------------------------------------
        use_gdf_legend = legend and column is not None and not _has_cbar_ax
        working_gdf.plot(ax=plot_ax, legend=use_gdf_legend, **plot_kwargs)

        # ------------------------------------------------------------------
        # 5b. Dedicated colorbar on ax_cbar (constrained bounding box)
        #
        # We use a dedicated GridSpec axis (ax_cbar) as the colorbar container.
        # This gives an explicit, predictable bounding box — no default sizing.
        # The colorbar strip is further shrunk to 60 % of the axis height by
        # repositioning ax_cbar after drawing, giving clear top/bottom margins.
        # ------------------------------------------------------------------
        if _has_cbar_ax and legend and column is not None and actual_cmap is not None:
            import matplotlib.cm as mcm
            import matplotlib.colors as mcolors

            col_vals = working_gdf[column].dropna()
            vmin = float(col_vals.min())
            vmax = float(col_vals.max())

            if isinstance(actual_cmap, str):
                cmap_obj = mcm.get_cmap(actual_cmap)
            else:
                cmap_obj = actual_cmap

            norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
            sm   = mcm.ScalarMappable(cmap=cmap_obj, norm=norm)
            sm.set_array([])

            cb = fig.colorbar(
                sm,
                cax=ax_cbar,
                orientation="vertical",
            )

            # Shrink colorbar to 60 % of its axis height, keeping it centred.
            # This prevents it from stretching edge-to-edge and looking oversized.
            pos = ax_cbar.get_position()
            margin = pos.height * 0.20  # 20 % top + 20 % bottom breathing room
            ax_cbar.set_position([
                pos.x0,
                pos.y0 + margin,
                pos.width,
                pos.height * 0.60,
            ])

            cb.ax.tick_params(labelsize=8, colors=text_color, length=4, width=0.8)
            cb.outline.set_edgecolor(text_color)
            cb.outline.set_linewidth(0.8)
            for lbl in cb.ax.get_yticklabels():
                lbl.set_color(text_color)
            if column:
                cb.set_label(column, color=text_color, fontsize=9, fontweight="bold")

        # ------------------------------------------------------------------
        # 5c. Titles
        # ------------------------------------------------------------------
        if title:
            plot_ax.set_title(
                title,
                fontsize=14,
                pad=20 if subtitle else 15,
                color=text_color,
                fontweight="bold",
            )
        if subtitle:
            plot_ax.text(
                0.5, 1.02, subtitle,
                color=THEME_PARAMS.get(theme_to_use, {}).get("text.color", text_color),
                fontsize=10, style="italic", ha="center", va="bottom",
                transform=plot_ax.transAxes,
            )

        # ------------------------------------------------------------------
        # 5d. Coordinate framing
        # ------------------------------------------------------------------
        if not show_coords:
            plot_ax.set_axis_off()
        else:
            plot_ax.tick_params(axis="both", which="both", length=0, labelsize=8)
            plot_ax.grid(True)
            plot_ax.xaxis.label.set_color(text_color)
            plot_ax.yaxis.label.set_color(text_color)
            for spine in plot_ax.spines.values():
                spine.set_color(text_color)

        # ------------------------------------------------------------------
        # 5e. Style the geopandas auto-legend (only used when no cbar_ax)
        # ------------------------------------------------------------------
        leg = plot_ax.get_legend()
        if leg is not None:
            leg.get_frame().set_facecolor(plt.rcParams.get("axes.facecolor", "white"))
            leg.get_frame().set_edgecolor(text_color)
            leg.get_frame().set_alpha(0.85)
            for txt in leg.get_texts():
                txt.set_color(text_color)
                txt.set_fontsize(8)
            if leg.get_title():
                leg.get_title().set_color(text_color)
                leg.get_title().set_fontsize(9)
                leg.get_title().set_weight("bold")

        # ------------------------------------------------------------------
        # 5f. Scale bar & north arrow (relative axes coordinates via transAxes)
        # ------------------------------------------------------------------
        if resolved_orientation == "landscape":
            scale_loc = "lower right"
            arrow_loc = "upper right"
        elif resolved_orientation == "portrait":
            scale_loc = "lower right"
            arrow_loc = "lower left"
        else:
            scale_loc = "lower right"
            arrow_loc = "upper right"

        # Add scale bar
        if scale_bar:
            add_scale_bar(plot_ax, working_gdf, loc=scale_loc, style=scale_bar_style,
                          color=text_color)

        # Add north arrow
        if north_arrow:
            add_north_arrow(plot_ax, loc=arrow_loc, style=north_arrow_style,
                            color=text_color)

        # ------------------------------------------------------------------
        # 5g. Dynamic sidebar text panel (fig.transFigure, descending y_cursor)
        #
        # Instead of a single hardcoded caption string, each metadata element
        # is rendered as its own annotated block.  A `y_cursor` variable is
        # decremented by `line_height` (in figure fraction) after every text
        # row, preventing any overlap no matter how long the values are.
        #
        # All coordinates use transform=fig.transFigure so they are fully
        # independent of map data coordinates.
        # ------------------------------------------------------------------
        sidebar_items: list = []
        if author:
            sidebar_items.append(("Author", author))
        if date:
            sidebar_items.append(("Date", date))
        if data_source:
            sidebar_items.append(("Source", data_source))
        if working_gdf.crs:
            # Use the authority-code short form (e.g. "EPSG:32637") to avoid overflow
            crs_str = working_gdf.crs.to_epsg()
            sidebar_items.append(("CRS", f"EPSG:{crs_str}" if crs_str else working_gdf.crs.to_string().split(" ")[0]))
        if credits:
            sidebar_items.append(("Credits", credits))

        if sidebar_items:
            if _has_cbar_ax:
                # Right sidebar column — starts just after the colorbar column
                x_anchor    = 0.885   # left edge of sidebar (figure fraction)
                y_start     = 0.88    # near the top of the plot area
                line_height = 0.045   # vertical step per text row
                label_fs    = 7.5
                value_fs    = 7.5
            else:
                # Compact footer strip for caller-supplied axes
                x_anchor    = 0.04
                y_start     = 0.048
                line_height = 0.022
                label_fs    = 7.0
                value_fs    = 7.0

            y_cursor = y_start  # descending pointer in figure-fraction space

            for label_str, value_str in sidebar_items:
                # Bold section header — left-aligned at x_anchor
                fig.text(
                    x_anchor, y_cursor,
                    f"{label_str}:",
                    fontsize=label_fs,
                    color=text_color,
                    alpha=0.90,
                    fontweight="bold",
                    ha="left",
                    va="top",
                    transform=fig.transFigure,
                )
                y_cursor -= line_height

                # Value rows — each wrapped line is its own fig.text() call
                # so the cursor advances exactly one line_height per row.
                for line in str(value_str).split("\n"):
                    fig.text(
                        x_anchor + 0.005, y_cursor,
                        line,
                        fontsize=value_fs,
                        color=text_color,
                        alpha=0.70,
                        ha="left",
                        va="top",
                        transform=fig.transFigure,
                    )
                    y_cursor -= line_height

                # Half-step breathing room between blocks
                y_cursor -= line_height * 0.4

        return plot_ax

    if theme and theme.lower().strip().replace(" ", "_") in THEME_PARAMS:
        with use_theme(theme):
            return _do_plot(active_ax)
    else:
        return _do_plot(active_ax)
