"""Python-to-R bridge for generating professional maps using ggplot2 and sf."""

import os
import shutil
import glob
import subprocess
import tempfile
import pandas as pd
import geopandas as gpd
from typing import Optional, Union, Any, List, Dict

def find_rscript() -> str:
    """Locate the Rscript executable on Windows.
    
    Returns
    -------
    str
        Path to the Rscript executable.
        
    Raises
    ------
    FileNotFoundError
        If Rscript cannot be located on the system.
    """
    # 1. Check if Rscript is in the system PATH
    rscript_path = shutil.which("Rscript")
    if rscript_path:
        return rscript_path

    # 2. Check Windows Registry
    import winreg
    for hive in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
        try:
            with winreg.OpenKey(hive, r"SOFTWARE\R-core\R") as key:
                install_path, _ = winreg.QueryValueEx(key, "InstallPath")
                if install_path:
                    path = os.path.join(install_path, "bin", "Rscript.exe")
                    if os.path.exists(path):
                        return path
        except OSError:
            pass

    # 3. Check typical Program Files installation paths
    program_files_paths = [
        r"C:\Program Files\R\R-*\bin\Rscript.exe",
        r"C:\Program Files (x86)\R\R-*\bin\Rscript.exe",
    ]
    for pattern in program_files_paths:
        matches = glob.glob(pattern)
        if matches:
            matches.sort()
            return matches[-1]

    raise FileNotFoundError(
        "Rscript executable could not be found. Please ensure R is installed "
        "and added to your system PATH, or installed in the default location."
    )

# Centralized configuration for required R packages
REQUIRED_R_PACKAGES = [
    "ggplot2", "sf", "terra", "raster", "stars",
    "ggrepel", "ggspatial", "cowplot", "patchwork",
    "gridExtra", "maps", "ggnewscale"
]

# Session cache to minimize package validation overhead
_R_ENV_VERIFIED = False
_R_PACKAGES_CHECKED = False

def find_r_home() -> str:
    """Locate the R_HOME directory.
    
    Returns
    -------
    str
        Path to the R home directory.
        
    Raises
    ------
    FileNotFoundError
        If R cannot be found on the system.
    """
    if "R_HOME" in os.environ and os.path.exists(os.environ["R_HOME"]):
        return os.environ["R_HOME"]
        
    # Check if Rscript is in path and use it to find R_HOME
    rscript_path = shutil.which("Rscript")
    if rscript_path:
        try:
            res = subprocess.run([rscript_path, "-e", "cat(R.home())"], capture_output=True, text=True, check=True)
            home = res.stdout.strip()
            if home and os.path.exists(home):
                return home
        except Exception:
            pass

    # Windows registry lookup
    if os.name == 'nt':
        import winreg
        for hive in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
            try:
                with winreg.OpenKey(hive, r"SOFTWARE\R-core\R") as key:
                    install_path, _ = winreg.QueryValueEx(key, "InstallPath")
                    if install_path and os.path.exists(install_path):
                        return install_path
            except OSError:
                pass

        # Globbing standard paths
        program_files_paths = [
            r"C:\Program Files\R\R-*",
            r"C:\Program Files (x86)\R\R-*",
        ]
        for pattern in program_files_paths:
            matches = glob.glob(pattern)
            if matches:
                matches.sort()
                return matches[-1]
                
    # macOS standard paths
    elif os.name == 'posix':
        mac_paths = [
            "/Library/Frameworks/R.framework/Resources",
            "/usr/local/lib/R",
            "/usr/lib/R",
            "/opt/homebrew/opt/r/lib/R",
        ]
        for path in mac_paths:
            if os.path.exists(path):
                return path

    raise FileNotFoundError(
        "R installation could not be found. Please ensure R is installed on your system. "
        "You can download R from https://cran.r-project.org/"
    )

def verify_r_environment() -> None:
    """Verify that R is installed and configure the rpy2 environment cleanly.
    
    Raises
    ------
    RuntimeError
        If R is missing, misconfigured, or rpy2 cannot be imported/initialized.
    """
    global _R_ENV_VERIFIED
    if _R_ENV_VERIFIED:
        return

    try:
        r_home = find_r_home()
        # Convert to 8.3 short path or forward slashes on Windows to avoid spaces issues in rpy2
        if os.name == 'nt':
            import ctypes
            buf = ctypes.create_unicode_buffer(1024)
            if ctypes.windll.kernel32.GetShortPathNameW(r_home, buf, 1024) > 0:
                r_home = buf.value
            r_home = r_home.replace("\\", "/")
            
        os.environ["R_HOME"] = r_home

        # Setup Windows specific paths for DLL loading
        if os.name == 'nt':
            r_bin_dir = os.path.join(r_home, "bin", "x64")
            if os.path.exists(r_bin_dir):
                if r_bin_dir not in os.environ["PATH"]:
                    os.environ["PATH"] = r_bin_dir + os.path.pathsep + os.environ["PATH"]
                try:
                    import sys
                    if sys.version_info >= (3, 8):
                        os.add_dll_directory(r_bin_dir)
                except Exception:
                    pass

        # Try to initialize rpy2
        import rpy2
        import rpy2.robjects as robjects
        
        _R_ENV_VERIFIED = True
    except Exception as e:
        raise RuntimeError(
            f"R environment verification failed.\n"
            f"Reason: {str(e)}\n"
            f"Action: Please make sure R is installed (download from https://cran.r-project.org/) "
            f"and added to your environment variables."
        )

def check_r_installation() -> bool:
    """Check if R is installed and available.
    
    Returns
    -------
    bool
        True if R is installed and configured, False otherwise.
    """
    try:
        verify_r_environment()
        return True
    except RuntimeError:
        return False

def check_r_packages(lib_dir: Optional[str] = None) -> List[str]:
    """Check which required R packages are missing.
    
    Parameters
    ----------
    lib_dir : str, optional
        Custom local library folder to search.
        
    Returns
    -------
    list of str
        List of missing package names.
    """
    verify_r_environment()
    
    import rpy2.robjects as robjects
    
    if lib_dir is None:
        pkg_dir = os.path.dirname(os.path.abspath(__file__))
        lib_dir = os.path.join(os.path.dirname(os.path.dirname(pkg_dir)), ".r_libs")
        
    os.makedirs(lib_dir, exist_ok=True)
    lib_dir_clean = lib_dir.replace("\\", "/")
    
    robjects.r(f'.libPaths(c("{lib_dir_clean}", .libPaths()))')
    
    try:
        # Optimized check: verify package directories directly via system.file to avoid scanning everything
        pkg_list_str = ", ".join(f'"{p}"' for p in REQUIRED_R_PACKAGES)
        r_code = f'pkgs <- c({pkg_list_str}); pkgs[sapply(pkgs, function(pkg) system.file(package = pkg) == "")]'
        missing_vec = robjects.r(r_code)
        missing = [str(x) for x in missing_vec]
    except Exception:
        missing = list(REQUIRED_R_PACKAGES)
        
    return missing

def install_missing_r_packages(repos: str = "https://cran.rstudio.com", lib_dir: Optional[str] = None) -> None:
    """Automatically check and install missing R packages using rpy2.
    
    Parameters
    ----------
    repos : str, default 'https://cran.rstudio.com'
        CRAN repository mirror to use.
    lib_dir : str, optional
        Custom local library directory to install packages into.
        
    Raises
    ------
    RuntimeError
        If installation fails or packages remain missing after installation.
    """
    global _R_PACKAGES_CHECKED
    if _R_PACKAGES_CHECKED:
        return
        
    verify_r_environment()
    
    print("Checking R installation...")
    print("Checking required R packages...")
    missing = check_r_packages(lib_dir)
    
    if not missing:
        print("All R packages are already installed.")
        _R_PACKAGES_CHECKED = True
        return
        
    if lib_dir is None:
        pkg_dir = os.path.dirname(os.path.abspath(__file__))
        lib_dir = os.path.join(os.path.dirname(os.path.dirname(pkg_dir)), ".r_libs")
        
    lib_dir_clean = lib_dir.replace("\\", "/")
    
    for pkg in missing:
        print(f"Installing missing package: {pkg}")
        
    import rpy2.robjects as robjects
    from rpy2.robjects.packages import importr
    
    try:
        utils = importr('utils')
        pack_names = robjects.vectors.StrVector(missing)
        utils.install_packages(pack_names, repos=repos, lib=lib_dir_clean)
    except Exception as e:
        raise RuntimeError(
            f"Failed to install R packages: {', '.join(missing)}.\n"
            f"Error details: {str(e)}\n"
            f"Suggested Action: Check your internet connection, or try installing them manually "
            f"in R: install.packages({repr(missing)}, lib='{lib_dir_clean}', repos='{repos}')"
        )
        
    still_missing = check_r_packages(lib_dir)
    if still_missing:
        raise RuntimeError(
            f"Verification failed. The following required R packages could not be installed: "
            f"{', '.join(still_missing)}.\n"
            f"Suggested Action: Check R logs above for compilation or dependency issues."
        )
        
    print("Installation completed successfully.")
    _R_PACKAGES_CHECKED = True

def ensure_r_packages(rscript_path: Optional[str] = None, lib_dir: Optional[str] = None) -> None:
    """Compatibility wrapper that calls install_missing_r_packages."""
    install_missing_r_packages(lib_dir=lib_dir)

def plot_map_r(
    vector_data: Optional[Union[str, gpd.GeoDataFrame]] = None,
    vector_column: Optional[str] = None,
    raster_data: Optional[str] = None,
    extra_vectors: Optional[List[Dict[str, Any]]] = None,
    points_data: Optional[Union[str, pd.DataFrame, gpd.GeoDataFrame]] = None,
    points_color_column: Optional[str] = None,
    points_label_column: Optional[str] = None,
    theme: str = "dark_matter",
    colormap: str = "neon",
    title: Optional[str] = None,
    subtitle: Optional[str] = None,
    output_path: Optional[str] = None,
    show_coords: bool = False,
    scale_bar: bool = True,
    scale_bar_style: str = "alternating",
    north_arrow: bool = True,
    north_arrow_style: str = "classic",
    width: float = 8.0,
    height: float = 8.0,
    dpi: int = 150,
    orientation: str = "auto",
    crs: Optional[str] = None,
    author: Optional[str] = None,
    credits: Optional[str] = None,
    data_source: Optional[str] = None,
    date: Optional[str] = None,
    created_by: Optional[str] = None,
    inset: bool = False,
    inset_map: Optional[str] = None,
    inset_position: Optional[List[float]] = None,
    inset_scale: float = 0.25,
    rscript_path: Optional[str] = None,
    lib_dir: Optional[str] = None
) -> str:
    """Plot vector and raster data using the R backend and ggplot2.
    
    Parameters
    ----------
    vector_data : str or geopandas.GeoDataFrame, optional
        Path to shapefile/geojson/geopackage or a GeoDataFrame.
    vector_column : str, optional
        The column name of the vector data to color-code.
    raster_data : str, optional
        Path to a continuous raster file (e.g. GeoTIFF).
    points_data : str, pandas.DataFrame, or geopandas.GeoDataFrame, optional
        Path to a CSV file or a DataFrame containing points with 'longitude' and 'latitude' columns.
    points_color_column : str, optional
        The column name of the points data to color-code points.
    points_label_column : str, optional
        The column name of the points data to use for ggrepel labels.
    theme : str, default 'dark_matter'
        The theme to apply ('dark_matter', 'retro_blueprint', 'natgeo_minimalist').
    colormap : str, default 'neon'
        The custom geographic colormap name ('elevation', 'bathymetry', 'blueprint', 'neon', 'editorial').
    title : str, optional
        Title of the map.
    subtitle : str, optional
        Subtitle of the map.
    output_path : str, optional
        Output image file path (e.g. PNG). If None, saves to a temporary file.
    show_coords : bool, default False
        Whether to show coordinate axes (ticks/labels).
    scale_bar : bool, default True
        Whether to add a scale bar.
    scale_bar_style : str, default 'alternating'
        Style of the scale bar ('alternating', 'minimal', 'blueprint', 'dark').
    north_arrow : bool, default True
        Whether to add a north arrow.
    north_arrow_style : str, default 'classic'
        Style of the arrow ('classic', 'arcgis', 'natgeo', 'minimal', 'blueprint', 'compass_rose', 'dark_neon').
    width : float, default 8.0
        Width of the output map in inches.
    height : float, default 8.0
        Height of the output map in inches.
    dpi : int, default 150
        DPI of the output map image.
    orientation : str, default 'auto'
        Figure orientation ('auto', 'portrait', 'landscape', 'square').
    crs : str, optional
        Target Coordinate Reference System to reproject vector layers to.
    author : str, optional
        Author name for metadata.
    credits : str, optional
        Credits text for layout.
    data_source : str, optional
        Data citation metadata.
    date : str, optional
        Map generation date.
    created_by : str, optional
        Text displayed in the "MAP CREATED BY" sidebar section.
        Defaults to ``author`` if not provided.  Set this to any string
        (e.g. your organisation name) to fully control what appears there
        without touching ``author``.
    inset : bool, default False
        Whether to overlay an inset locator map.
    rscript_path : str, optional
        Path to Rscript executable. If None, auto-detected.
    lib_dir : str, optional
        Path to local R library folder.
        
    Returns
    -------
    str
        The path to the generated map image.
    """
    if rscript_path is None:
        rscript_path = find_rscript()

    # Automatically check and install missing R packages using rpy2
    install_missing_r_packages(lib_dir=lib_dir)

    if lib_dir is None:
        pkg_dir = os.path.dirname(os.path.abspath(__file__))
        lib_dir = os.path.join(os.path.dirname(os.path.dirname(pkg_dir)), ".r_libs")
        
    lib_dir_clean = lib_dir.replace("\\", "/")
    
    # Determine if scales should be discrete or continuous
    from pandas.api.types import is_string_dtype, is_bool_dtype
    vector_discrete = False
    if vector_data is not None and vector_column is not None:
        try:
            gdf_inspect = vector_data
            if isinstance(vector_data, str):
                gdf_inspect = gpd.read_file(vector_data)
            col_dtype = gdf_inspect[vector_column].dtype
            if is_string_dtype(col_dtype) or is_bool_dtype(col_dtype) or isinstance(col_dtype, pd.CategoricalDtype):
                vector_discrete = True
        except Exception:
            pass

    points_discrete = False
    if points_data is not None and points_color_column is not None:
        try:
            df_inspect = points_data
            if isinstance(points_data, str):
                df_inspect = pd.read_csv(points_data)
            col_dtype = df_inspect[points_color_column].dtype
            if is_string_dtype(col_dtype) or is_bool_dtype(col_dtype) or isinstance(col_dtype, pd.CategoricalDtype):
                points_discrete = True
        except Exception:
            pass

    # Path to themes.R
    pkg_dir = os.path.dirname(os.path.abspath(__file__))
    themes_r_path = os.path.join(pkg_dir, "themes.R").replace("\\", "/")

    temp_files = []
    
    # Process vector data
    vector_path_r = "NULL"
    if vector_data is not None:
        if isinstance(vector_data, gpd.GeoDataFrame):
            temp_vec = tempfile.NamedTemporaryFile(suffix=".geojson", delete=False)
            temp_vec.close()
            vector_data.to_file(temp_vec.name, driver="GeoJSON")
            vector_path_r = f'"{temp_vec.name.replace("\\", "/")}"'
            temp_files.append(temp_vec.name)
        else:
            vector_path_r = f'"{vector_data.replace("\\", "/")}"'

    # Process raster data
    raster_path_r = "NULL"
    if raster_data is not None:
        raster_path_r = f'"{raster_data.replace("\\", "/")}"'

    # Process points data
    points_path_r = "NULL"
    if points_data is not None:
        if isinstance(points_data, (pd.DataFrame, gpd.GeoDataFrame)):
            df_to_save = points_data.copy()
            if isinstance(points_data, gpd.GeoDataFrame):
                df_to_save['longitude'] = points_data.geometry.x
                df_to_save['latitude'] = points_data.geometry.y
            temp_pts = tempfile.NamedTemporaryFile(suffix=".csv", delete=False)
            temp_pts.close()
            df_to_save.to_csv(temp_pts.name, index=False)
            points_path_r = f'"{temp_pts.name.replace("\\", "/")}"'
            temp_files.append(temp_pts.name)
        else:
            points_path_r = f'"{points_data.replace("\\", "/")}"'

    # Output path
    if output_path is None:
        temp_out = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        temp_out.close()
        output_path = temp_out.name
    
    output_path_clean = output_path.replace("\\", "/")
    
    logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "logo.png"))
    logo_path_clean = logo_path.replace("\\", "/")

    # Build R script lines
    r_lines = [
        f'.libPaths(c("{lib_dir_clean}", .libPaths()))',
        'library(ggplot2)',
        'library(sf)',
        'library(terra)',
        'library(stars)',
        'library(ggrepel)',
        'library(ggspatial)',
        'library(cowplot)',
        'library(patchwork)',
        'library(gridExtra)',
        'library(maps)',
        'library(ggnewscale)',
        f'source("{themes_r_path}")',
        '',
        '# Variable Setup',
        f'logo_img_path <- "{logo_path_clean}"',
        f'theme_name <- "{theme}"',
        f'colormap_name <- "{colormap}"',
        f'scale_bar <- {str(scale_bar).upper()}',
        f'scale_bar_style <- "{scale_bar_style}"',
        f'north_arrow <- {str(north_arrow).upper()}',
        f'north_arrow_style <- "{north_arrow_style}"',
        f'show_coords <- {str(show_coords).upper()}',
        f'orientation <- "{orientation}"',
        f'user_crs <- "{crs or "NULL"}"',
        f'author <- "{author or "NULL"}"',
        f'credits_val <- "{credits or "NULL"}"',
        f'data_source <- "{data_source or "NULL"}"',
        f'date_val <- "{date or "NULL"}"',
        # created_by: falls back to author if not explicitly set
        f'created_by_val <- "{created_by or author or "NULL"}"',
        f'inset_enabled <- {str(inset or (inset_map is not None)).upper()}',
        f'custom_inset_path <- "{inset_map.replace("\\", "/") if inset_map else "NULL"}"',
        f'inset_left <- {(inset_position or [0.7, 0.7])[0]}',
        f'inset_bottom <- {(inset_position or [0.7, 0.7])[1]}',
        f'inset_right <- {min(1.0, (inset_position or [0.7, 0.7])[0] + inset_scale)}',
        f'inset_top <- {min(1.0, (inset_position or [0.7, 0.7])[1] + inset_scale)}',
        f'main_width <- {width}',
        f'main_height <- {height}',
        f'title <- "{title or ""}"',
        f'subtitle <- "{subtitle or ""}"',
        # Declare vector_column and vector_discrete so R branches using
        # !is.null(vector_column) / vector_discrete work regardless of whether
        # vector_data was supplied.
        f'vector_column <- {repr(vector_column) if vector_column else "NULL"}',
        f'vector_discrete <- {str(vector_discrete).upper()}',
        '',
    ]

    # Vector Load
    if vector_data is not None:
        r_lines.extend([
            f'vec <- st_read({vector_path_r}, quiet = TRUE)',
            'vec <- st_make_valid(vec)',
            'bbox <- st_bbox(vec)',
            'span <- max(bbox["xmax"] - bbox["xmin"], bbox["ymax"] - bbox["ymin"])',
            'vec <- st_simplify(vec, preserveTopology = TRUE, dTolerance = span * 0.001)',
        ])

    # Raster Load
    if raster_data is not None:
        r_lines.extend([
            f'r <- terra::rast({raster_path_r})',
            'if (terra::ncell(r) > 2000000) {',
            '  fact <- ceiling(sqrt(terra::ncell(r) / 2000000))',
            '  r <- terra::aggregate(r, fact, fun = "mean")',
            '}',
        ])

    # Points Load
    if points_data is not None:
        r_lines.extend([
            f'pts <- read.csv({points_path_r})',
            'pts_sf <- st_as_sf(pts, coords = c("longitude", "latitude"), crs = 4326, remove = FALSE)',
        ])

    # Projection Management
    r_lines.extend([
        '# Resolve Target Projection',
        'target_crs <- NULL',
        'if (user_crs != "NULL" && user_crs != "") {',
        '  target_crs <- st_crs(user_crs)',
        '} else if (exists("r")) {',
        '  target_crs <- st_crs(r)',
        '} else if (exists("vec")) {',
        '  target_crs <- st_crs(vec)',
        '}',
        'if (is.na(target_crs) || is.null(target_crs)) {',
        '  target_crs <- st_crs(4326)',
        '}',
        '',
        '# UTM Auto-selection for local maps in degrees',
        'if (st_is_longlat(target_crs)) {',
        '  ref_bbox <- NULL',
        '  if (exists("vec")) {',
        '    ref_bbox <- st_bbox(st_transform(vec, 4326))',
        '  } else if (exists("pts_sf")) {',
        '    ref_bbox <- st_bbox(st_transform(pts_sf, 4326))',
        '  }',
        '  if (!is.null(ref_bbox)) {',
        '    center_lon <- (ref_bbox["xmin"] + ref_bbox["xmax"]) / 2',
        '    center_lat <- (ref_bbox["ymin"] + ref_bbox["ymax"]) / 2',
        '    lon_span <- ref_bbox["xmax"] - ref_bbox["xmin"]',
        '    if (lon_span < 15) {',
        '      utm_zone <- floor((center_lon + 180) / 6) + 1',
        '      is_southern <- center_lat < 0',
        '      utm_epsg <- ifelse(is_southern, 32700 + utm_zone, 32600 + utm_zone)',
        '      target_crs <- st_crs(utm_epsg)',
        '    }',
        '  }',
        '}',
        '',
        '# Reproject datasets',
        'if (exists("vec")) {',
        '  vec <- st_transform(vec, target_crs)',
        '}',
        'if (exists("pts_sf")) {',
        '  pts_sf <- st_transform(pts_sf, target_crs)',
        '}',
        'if (exists("r")) {',
        '  r <- terra::project(r, target_crs$wkt)',
        '  r_df <- as.data.frame(r, xy = TRUE, na.rm = TRUE)',
        '  val_col <- colnames(r_df)[3]',
        '  is_classified <- FALSE',
        '  if (is.factor(r_df[[val_col]]) || length(unique(r_df[[val_col]])) < 15) {',
        '    r_df[[val_col]] <- as.factor(r_df[[val_col]])',
        '    is_classified <- TRUE',
        '  }',
        '}',
    ])

    # Dynamic Bounding Box & Aspect Ratio
    r_lines.extend([
        '# Calculate Bounding Box and Aspect Ratio',
        'map_bbox <- NULL',
        'if (exists("vec")) {',
        '  map_bbox <- st_bbox(vec)',
        '} else if (exists("r") && nrow(r_df) > 0) {',
        '  map_bbox <- c(xmin = min(r_df$x), xmax = max(r_df$x), ymin = min(r_df$y), ymax = max(r_df$y))',
        '}',
        '',
        'fig_width <- main_width',
        'fig_height <- main_height',
        'if (!is.null(map_bbox)) {',
        '  coord_w <- map_bbox["xmax"] - map_bbox["xmin"]',
        '  coord_h <- map_bbox["ymax"] - map_bbox["ymin"]',
        '  aspect <- coord_w / coord_h',
        '  if (orientation == "auto" || orientation == "fit") {',
        '    # Perfectly fit the canvas to the data aspect ratio',
        '    if (aspect >= 1) {',
        '      fig_width <- main_width',
        '      fig_height <- main_width / aspect',
        '    } else {',
        '      fig_height <- main_height',
        '      fig_width <- main_height * aspect',
        '    }',
        '  } else if (orientation == "landscape") {',
        '    if (main_width == main_height) {',
        '      fig_width <- main_width * 1.414',
        '      fig_height <- main_height',
        '    } else {',
        '      fig_width <- max(main_width, main_height)',
        '      fig_height <- min(main_width, main_height)',
        '    }',
        '  } else if (orientation == "portrait") {',
        '    if (main_width == main_height) {',
        '      fig_width <- main_width',
        '      fig_height <- main_height * 1.414',
        '    } else {',
        '      fig_width <- min(main_width, main_height)',
        '      fig_height <- max(main_width, main_height)',
        '    }',
        '  } else if (orientation == "square") {',
        '    fig_width <- min(main_width, main_height)',
        '    fig_height <- min(main_width, main_height)',
        '  }',
        '}',
    ])

    # Construct Plot
    r_lines.extend([
        '# Plot construction',
        'p <- ggplot()',
    ])

    # Raster Layer
    if raster_data is not None:
        r_lines.append('p <- p + geom_raster(data = r_df, aes(x = x, y = y, fill = .data[[val_col]]))')

    # Vector Layer
    if vector_data is not None:
        if vector_column:
            r_lines.append(f'p <- p + geom_sf(data = vec, aes(fill = .data[["{vector_column}"]]), color = NA, inherit.aes = FALSE)')
        else:
            r_lines.append('p <- p + geom_sf(data = vec, color = "#cccccc", fill = NA, inherit.aes = FALSE)')


    # Extra Vectors
    if extra_vectors:
        for idx, ev in enumerate(extra_vectors):
            ev_path = ev.get("data")
            if not ev_path: continue
            name = ev.get("name", f"Layer_{idx}")
            color = ev.get("color", "NA")
            fill = ev.get("fill", "NA")
            alpha = ev.get("alpha", 1.0)
            linewidth = ev.get("linewidth", 0.5)
            
            safe_path = str(ev_path).replace("\\", "/")
            
            r_lines.extend([
                f'ev_{idx} <- st_read("{safe_path}", quiet = TRUE)',
                f'ev_{idx} <- st_make_valid(ev_{idx})',
                f'ev_{idx} <- st_transform(ev_{idx}, target_crs)',
                'p <- p + ggnewscale::new_scale_fill() + ggnewscale::new_scale_color()'
            ])
            
            aes_args = []
            if color != "NA":
                aes_args.append(f'color="{name}"')
            if fill != "NA":
                aes_args.append(f'fill="{name}"')
            
            aes_str = f', aes({", ".join(aes_args)})' if aes_args else ''
            
            r_lines.append(f'p <- p + geom_sf(data = ev_{idx}{aes_str}, alpha={alpha}, linewidth={linewidth}, inherit.aes = FALSE)')
            
            if color != "NA":
                r_lines.append(f'p <- p + scale_color_manual(name="", values=c("{name}"="{color}"))')
            if fill != "NA":
                r_lines.append(f'p <- p + scale_fill_manual(name="", values=c("{name}"="{fill}"))')

    # Points Layer
    if points_data is not None:
        if points_color_column:
            r_lines.append(f'p <- p + geom_sf(data = pts_sf, aes(color = .data[["{points_color_column}"]]), size = 2, inherit.aes = FALSE)')
        else:
            r_lines.append('p <- p + geom_sf(data = pts_sf, color = "red", size = 2, inherit.aes = FALSE)')
            
        if points_label_column:
            if points_color_column:
                r_lines.append(f'p <- p + geom_label_repel(data = pts_sf, aes(label = .data[["{points_label_column}"]], geometry = geometry, color = .data[["{points_color_column}"]]), stat = "sf_coordinates", box.padding = 0.5, segment.color = "grey50", inherit.aes = FALSE)')
            else:
                r_lines.append(f'p <- p + geom_label_repel(data = pts_sf, aes(label = .data[["{points_label_column}"]], geometry = geometry), stat = "sf_coordinates", box.padding = 0.5, segment.color = "grey50", inherit.aes = FALSE)')

    # Theme and Scales
    r_lines.extend([
        '# Lock aspect ratio with coord_sf to prevent stretching',
        'p <- p + coord_sf(expand = FALSE, crs = target_crs)',
        '# Apply theme function',
        'theme_fn <- get(paste("theme_", theme_name, sep=""))',
        'p <- p + theme_fn()',
    ])

    if raster_data is not None:
        r_lines.append(f'p <- p + scale_fill_geoplot("{colormap}", discrete = is_classified)')
    elif vector_data is not None and vector_column:
        r_lines.append(f'p <- p + scale_fill_geoplot("{colormap}", discrete = {str(vector_discrete).upper()})')
        
    if points_data is not None and points_color_column:
        r_lines.append(f'p <- p + scale_color_geoplot("{colormap}", discrete = {str(points_discrete).upper()})')

    # Map Overlays and Layout Setup
    r_lines.extend([
        '# Define style colors based on theme name',
        'scale_bar_color <- ifelse(theme_name == "dark_matter", "#d1d2d6", ifelse(theme_name == "retro_blueprint", "#ffffff", "#1c1c1c"))',
        'scale_bar_bg <- ifelse(theme_name == "dark_matter", "#0f111a", ifelse(theme_name == "retro_blueprint", "#0f2d54", "#fbf9f3"))',
        'scale_font_family <- ifelse(theme_name == "retro_blueprint", "mono", ifelse(theme_name == "natgeo_minimalist", "serif", "sans"))',
        '',
        '# Adjust legend parameters and layout',
        'p <- p + theme(',
        '  legend.position = "right",',
        '  legend.background = element_rect(fill = "transparent", color = NA),',
        '  legend.text = element_text(color = scale_bar_color, family = scale_font_family),',
        '  legend.title = element_text(color = scale_bar_color, family = scale_font_family, face = "bold")',
        ')',
        '',
        '# Map Python scale bar styles to R ggspatial parameters',
        'scale_bar_style_r <- ifelse(scale_bar_style %in% c("alternating", "blueprint", "dark"), "bar", "ticks")',
        'scale_loc_r <- "br"',
        '',
        '# Apply Scale Bar overlay using ggspatial',
        'if (scale_bar == TRUE) {',
        '  p <- p + annotation_scale(',
        '    location = scale_loc_r, width_hint = 0.25, style = scale_bar_style_r,',
        '    text_col = scale_bar_color, text_family = scale_font_family,',
        '    line_col = scale_bar_color',
        '  )',
        '}',
        '',
        '# Map Python north arrow styles to R ggspatial styles',
        'arrow_loc_r <- ifelse(orientation == "portrait", "bl", "tr")',
        'arrow_style_r <- north_arrow_minimal(text_col = scale_bar_color, line_col = scale_bar_color)',
        'if (north_arrow_style %in% c("classic", "arcgis")) {',
        '  arrow_style_r <- north_arrow_fancy_orienteering(text_col = scale_bar_color, line_col = scale_bar_color, fill = c(scale_bar_color, "white"))',
        '} else if (north_arrow_style == "compass_rose") {',
        '  arrow_style_r <- north_arrow_nautical(text_col = scale_bar_color, line_col = scale_bar_color, fill = c(scale_bar_color, "white"))',
        '} else if (north_arrow_style == "dark_neon") {',
        '  arrow_style_r <- north_arrow_fancy_orienteering(text_col = scale_bar_color, line_col = scale_bar_color, fill = c("#8a2be2", "#151620"))',
        '}',
        '',
        '# Apply North Arrow overlay using ggspatial',
        'if (north_arrow == TRUE) {',
        '  p <- p + annotation_north_arrow(',
        '    location = arrow_loc_r, which_north = "true",',
        '    style = arrow_style_r',
        '  )',
        '}',
        '',
        '# Prepare metadata for caption',
        'clean_source <- ifelse(data_source == "NULL" || data_source == "", "Kenya Open Data Portal, ESA WorldCover 2021", data_source)',
        'clean_author <- ifelse(author == "NULL" || author == "", "KNBS, 2019", author)',
        'created_by_display <- ifelse(created_by_val == "NULL" || created_by_val == "", clean_author, created_by_val)',
        'date_text <- ifelse(date_val == "NULL" || date_val == "", format(Sys.Date(), "%d %b %Y"), date_val)',
        '',
        'crs_str <- ifelse(!is.null(target_crs$epsg), paste("WGS 84 / UTM Zone ", target_crs$epsg %% 100, ifelse(target_crs$epsg < 32700, "N", "S"), sep=""), target_crs$proj4string)',
        'if (nchar(crs_str) > 40) crs_str <- paste(substr(crs_str, 1, 37), "...", sep="")',
        '',
        'caption_text <- paste(',
        '  "Map Created By: ", created_by_display, "\n",',
        '  "Date: ", date_text, "\n",',
        '  "Data Source: ", clean_source, "\n",',
        '  "Coordinate System: ", crs_str, sep=""',
        ')',
        '',
        '# Professional typography',
        'title_sz_pt    <- 22',
        'subtitle_sz_pt <- 14',
        'p_main <- p + labs(title = title, subtitle = subtitle, caption = caption_text, x = NULL, y = NULL) +',
        '  theme(',
        '    axis.title      = element_blank(),',
        '    plot.title      = element_text(size = title_sz_pt, face = "bold", color = scale_bar_color, family = scale_font_family, margin = margin(t = 10, b = 5)),',
        '    plot.subtitle   = element_text(size = subtitle_sz_pt, face = "italic", color = scale_bar_color, family = scale_font_family, margin = margin(b = 10)),',
        '    plot.caption    = element_text(size = 9, color = scale_bar_color, family = scale_font_family, hjust = 0, margin = margin(t = 10)),',
        '    plot.margin     = margin(15, 15, 15, 15, "pt"),',
        '    plot.background = element_rect(fill = scale_bar_bg, color = NA)',
        '  )',
        '',
        '# Inset Map if enabled',
        'if (inset_enabled == TRUE && exists("map_bbox") && !is.null(map_bbox)) {',
        '  try({',
        '    if (custom_inset_path != "NULL") {',
        '      base_inset <- st_read(custom_inset_path, quiet = TRUE)',
        '      base_inset <- st_make_valid(base_inset)',
        '      base_inset <- st_transform(base_inset, target_crs)',
        '    } else {',
        '      base_inset <- st_as_sf(maps::map("world", plot = FALSE, fill = TRUE))',
        '      base_inset <- st_transform(base_inset, target_crs)',
        '    }',
        '    bbox_poly <- st_as_sfc(st_bbox(c(xmin=map_bbox["xmin"], xmax=map_bbox["xmax"], ymin=map_bbox["ymin"], ymax=map_bbox["ymax"]), crs=target_crs))',
        '    ',
        '    if (custom_inset_path != "NULL") {',
        '      # Use the full extent of the provided inset map',
        '      inset_lims <- st_bbox(base_inset)',
        '    } else {',
        '      # Zoom out automatically for the world map',
        '      center_x <- (map_bbox["xmin"] + map_bbox["xmax"]) / 2',
        '      center_y <- (map_bbox["ymin"] + map_bbox["ymax"]) / 2',
        '      range_x <- (map_bbox["xmax"] - map_bbox["xmin"]) * 4.5',
        '      range_y <- (map_bbox["ymax"] - map_bbox["ymin"]) * 4.5',
        '      inset_lims <- c(xmin = center_x - range_x, xmax = center_x + range_x, ymin = center_y - range_y, ymax = center_y + range_y)',
        '    }',
        '    ',
        '    p_inset_only <- ggplot() +',
        '      geom_sf(data = base_inset, fill = "#e0e0e0", color = "#b0b0b0", linewidth = 0.2) +',
        '      geom_sf(data = bbox_poly, fill = NA, color = "red", linewidth = 1.0) +',
        '      coord_sf(xlim = c(inset_lims["xmin"], inset_lims["xmax"]), ylim = c(inset_lims["ymin"], inset_lims["ymax"]), expand = FALSE) +',
        '      theme_void() +',
        '      theme(',
        '        panel.background = element_rect(fill = "#d4e6f1", color = scale_bar_color, linewidth = 0.5),',
        '        plot.background = element_rect(fill = "transparent", color = NA)',
        '      )',
        '    p_main <- p_main + inset_element(p_inset_only, left = as.numeric(inset_left), bottom = as.numeric(inset_bottom), right = as.numeric(inset_right), top = as.numeric(inset_top))',
        '  }, silent = TRUE)',
        '}',
        '',
        'p_final <- p_main',
    ])

    # Save
    r_lines.append(f'ggsave("{output_path_clean}", plot = p_final, width = fig_width, height = fig_height, dpi = {dpi}, bg = scale_bar_bg)')

    # Write script file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".R", delete=False, encoding="utf-8") as f:
        f.write("\n".join(r_lines))
        r_script_path = f.name

    try:
        result = subprocess.run(
            [rscript_path, r_script_path],
            capture_output=True,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        for tf in temp_files:
            if os.path.exists(tf):
                os.remove(tf)
        if os.path.exists(r_script_path):
            os.remove(r_script_path)
        raise RuntimeError(f"R script execution failed:\nSTDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}")

    # Clean up temp files
    for tf in temp_files:
        if os.path.exists(tf):
            os.remove(tf)
    if os.path.exists(r_script_path):
        os.remove(r_script_path)

    return output_path
