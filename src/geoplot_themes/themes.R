# ggplot2 themes and scale wrappers for geoplot-themes

library(ggplot2)

# Hex-code palettes matching geoplot-themes exactly
geoplot_palettes <- list(
  elevation = c("#1b4332", "#2d6a4f", "#40916c", "#d8f3dc", "#eed7a1", "#a98467", "#7f5539", "#f4f1de"),
  bathymetry = c("#03045e", "#0077b6", "#00b4d8", "#90e0ef", "#caf0f8"),
  blueprint = c("#0a2540", "#113f67", "#38598b", "#87a7b3", "#e7eaf6"),
  neon = c("#0f0c1b", "#31114b", "#8a2be2", "#ff007f", "#00ffff"),
  editorial = c("#2b2d42", "#8d99ae", "#edf2f4", "#c5a059", "#3a5a40")
)

#' Dark Matter ggplot2 Theme
#' 
#' High-contrast neon cyan/magenta styling on a near-black grid background.
theme_dark_matter <- function(base_size = 11, base_family = "sans") {
  theme_minimal(base_size = base_size, base_family = base_family) +
    theme(
      plot.background = element_rect(fill = "#090a0f", color = NA),
      panel.background = element_rect(fill = "#090a0f", color = NA),
      panel.border = element_rect(fill = NA, color = "#1f212d", linewidth = 1.2),
      plot.margin = margin(20, 20, 20, 20),
      text = element_text(color = "#d1d2d6"),
      plot.title = element_text(color = "#ffffff", face = "bold", size = 16, margin = margin(0, 0, 5, 0)),
      plot.subtitle = element_text(color = "#8a2be2", size = 11, margin = margin(0, 0, 15, 0)),
      plot.caption = element_text(color = "#4d4f5c", size = 8, hjust = 0, margin = margin(15, 0, 0, 0)),
      axis.text = element_text(color = "#4d4f5c", size = 9),
      axis.title = element_text(color = "#d1d2d6", size = 10, face = "bold"),
      panel.grid.major = element_line(color = "#1f212d", linetype = "solid", linewidth = 0.5),
      panel.grid.minor = element_line(color = "#151620", linetype = "solid", linewidth = 0.25),
      legend.background = element_rect(fill = "#0f111a", color = "#1f212d", linewidth = 0.8),
      legend.text = element_text(color = "#d1d2d6", size = 9),
      legend.title = element_text(color = "#ffffff", face = "bold", size = 10),
      legend.key = element_rect(fill = "transparent", color = NA),
      strip.background = element_rect(fill = "#1f212d", color = NA),
      strip.text = element_text(color = "#d1d2d6", face = "bold")
    )
}

#' Retro Blueprint ggplot2 Theme
#' 
#' Classic technical styling with blueprint navy background, white grids, and monospace typography.
theme_retro_blueprint <- function(base_size = 11, base_family = "mono") {
  theme_minimal(base_size = base_size, base_family = base_family) +
    theme(
      plot.background = element_rect(fill = "#0a2342", color = NA),
      panel.background = element_rect(fill = "#0a2342", color = NA),
      panel.border = element_rect(fill = NA, color = "#3182ce", linewidth = 1.5),
      plot.margin = margin(20, 20, 20, 20),
      text = element_text(color = "#ffffff"),
      plot.title = element_text(color = "#ffffff", face = "bold", size = 16, margin = margin(0, 0, 5, 0)),
      plot.subtitle = element_text(color = "#87a7b3", size = 11, face = "italic", margin = margin(0, 0, 15, 0)),
      plot.caption = element_text(color = "#4a5568", size = 8, hjust = 0, margin = margin(15, 0, 0, 0)),
      axis.text = element_text(color = "#3182ce", size = 9),
      axis.title = element_text(color = "#ffffff", size = 10, face = "bold"),
      panel.grid.major = element_line(color = "#1a365d", linetype = "solid", linewidth = 0.8),
      panel.grid.minor = element_line(color = "#1a365d", linetype = "dashed", linewidth = 0.4),
      legend.background = element_rect(fill = "#0f2d54", color = "#3182ce", linewidth = 1.0),
      legend.text = element_text(color = "#ffffff", size = 9),
      legend.title = element_text(color = "#ffffff", face = "bold", size = 10),
      legend.key = element_rect(fill = "transparent", color = NA),
      strip.background = element_rect(fill = "#1a365d", color = NA),
      strip.text = element_text(color = "#ffffff", face = "bold")
    )
}

#' National Geographic Minimalist ggplot2 Theme
#' 
#' Elegant editorial style with neutral cream background, muted gray grid borders, and serif typography.
theme_natgeo_minimalist <- function(base_size = 11, base_family = "serif") {
  theme_minimal(base_size = base_size, base_family = base_family) +
    theme(
      plot.background = element_rect(fill = "#fbf9f3", color = NA),
      panel.background = element_rect(fill = "#fbf9f3", color = NA),
      panel.border = element_rect(fill = NA, color = "#1c1c1c", linewidth = 1.5),
      plot.margin = margin(20, 20, 20, 20),
      text = element_text(color = "#1c1c1c"),
      plot.title = element_text(color = "#1c1c1c", face = "bold", size = 17, margin = margin(0, 0, 5, 0)),
      plot.subtitle = element_text(color = "#c5a059", size = 11, face = "italic", margin = margin(0, 0, 15, 0)),
      plot.caption = element_text(color = "#7f7d75", size = 8, hjust = 0, margin = margin(15, 0, 0, 0)),
      axis.text = element_text(color = "#a09e95", size = 9),
      axis.title = element_text(color = "#1c1c1c", size = 10, face = "bold"),
      panel.grid.major = element_line(color = "#eadecf", linetype = "solid", linewidth = 0.6),
      panel.grid.minor = element_line(color = "#eadecf", linetype = "dotted", linewidth = 0.3),
      legend.background = element_rect(fill = "#fbf9f3", color = "#1c1c1c", linewidth = 0.8),
      legend.text = element_text(color = "#1c1c1c", size = 9),
      legend.title = element_text(color = "#1c1c1c", face = "bold", size = 10),
      legend.key = element_rect(fill = "transparent", color = NA),
      strip.background = element_rect(fill = "#eadecf", color = NA),
      strip.text = element_text(color = "#1c1c1c", face = "bold")
    )
}

#' Geoplot Custom Fill Scale
#' 
#' @param palette One of 'elevation', 'bathymetry', 'blueprint', 'neon', 'editorial'.
#' @param discrete Logical, whether scale is discrete.
#' @param reverse Logical, whether colors should be reversed.
#' @param ... Additional arguments passed to scale_fill_manual or scale_fill_gradientn.
scale_fill_geoplot <- function(palette = "elevation", discrete = FALSE, reverse = FALSE, ...) {
  pal <- geoplot_palettes[[palette]]
  if (is.null(pal)) stop(paste("Palette not found:", palette))
  if (reverse) pal <- rev(pal)
  if (discrete) {
    scale_fill_manual(values = pal, ...)
  } else {
    scale_fill_gradientn(colours = pal, ...)
  }
}

#' Geoplot Custom Color/Colour Scale
#' 
#' @param palette One of 'elevation', 'bathymetry', 'blueprint', 'neon', 'editorial'.
#' @param discrete Logical, whether scale is discrete.
#' @param reverse Logical, whether colors should be reversed.
#' @param ... Additional arguments passed to scale_color_manual or scale_color_gradientn.
scale_color_geoplot <- function(palette = "elevation", discrete = FALSE, reverse = FALSE, ...) {
  pal <- geoplot_palettes[[palette]]
  if (is.null(pal)) stop(paste("Palette not found:", palette))
  if (reverse) pal <- rev(pal)
  if (discrete) {
    scale_color_manual(values = pal, ...)
  } else {
    scale_color_gradientn(colours = pal, ...)
  }
}
