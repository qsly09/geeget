import os
import json
import numpy as np
import geopandas as gpd
import ee
from shapely.geometry import Polygon
import rasterio
from rasterio import warp

def parse_gee_date(date):
    """
    Parses a date range string in the format 'YYYYMMDD-YYYYMMDD' and returns the start and end dates in 'YYYY-MM-DD' format.
    Args:
        date (str): A string representing a date range in the format 'YYYYMMDD-YYYYMMDD'.
    Returns:
        tuple: A tuple containing two strings, the start date and the end date, both in 'YYYY-MM-DD' format.
    """
    
    date_start, date_end = date.split("-")
    date_start = date_start[:4] + "-" + date_start[4:6] + "-" + date_start[6:]
    date_end = date_end[:4] + "-" + date_end[4:6] + "-" + date_end[6:]
    
    return date_start, date_end

def parse_gee_roi(roi):
    """
    Parses a region of interest (ROI) string and returns a GeoDataFrame with the geometry and a bounding box string.
    Parameters:
    roi (str): The region of interest string. It can be in one of the following formats:
        - Format 1: A coordinate string in the format of [[[-90.93400996,32.85891488],[-90.82700534,32.85891488],[-90.82700534,32.94915305],[-90.93400996,32.94915305],[-90.93400996,32.85891488]]]
        - Format 2: A bounding box string in the format of [-121.68453831871847,40.034385959224565,-121.65922118033382,40.05761920014249]
        - Format 3: A path to a GeoJSON file ending with .json
    Returns:
    tuple: A tuple containing:
        - aoi_geom (GeoDataFrame): A GeoDataFrame containing the geometry of the ROI.
    """

    # to get the geometry from the string, 
    # format 1 (copied from the PS explorer): [[[-90.93400996,32.85891488],[-90.82700534,32.85891488],[-90.82700534,32.94915305],[-90.93400996,32.94915305],[-90.93400996,32.85891488]]]
    if roi.startswith('[[['):
        # Assume it's a coordinate string and parse it
        coordinates = json.loads(roi)
        # Create GeoDataFrame with geometry
        polygon = Polygon(coordinates[0])
        aoi_geom = gpd.GeoDataFrame(geometry=[polygon], crs='EPSG:4326')
    # format 2 (GEE format, minx, miny, maxx, maxy): [-121.68453831871847,40.034385959224565,-121.65922118033382,40.05761920014249]
    elif roi.startswith('['):
        # Assume it's a bounding box and parse it
        minx, miny, maxx, maxy = json.loads(roi)
        # Create the polygon using the bounding box coordinates
        polygon = Polygon([
            (minx, miny),
            (minx, maxy),
            (maxx, maxy),
            (maxx, miny),
            (minx, miny)  # Close the polygon by repeating the first point
        ])

        # polygon = Polygon([[minx, miny], [maxx, miny], [maxx, maxy], [minx, maxy], [minx, miny]])
        aoi_geom = gpd.GeoDataFrame(geometry=[polygon], crs='EPSG:4326')
    # format 3 (geojson file)
    elif roi.endswith('.json'):
        aoi_geom = gpd.read_file(roi)
    
    roi_coords  = aoi_geom.geometry.total_bounds
    roi_gee     = ee.Geometry.BBox(roi_coords[0], roi_coords[1], roi_coords[2], roi_coords[3])
    
    return roi_gee

def parse_band_name(image_band, band):
    """
    Generate a filename for a specific band of an image.
    Args:
        image_band (str): The name of the image band.
        band (str): The specific band to be appended.
    Returns:
        str: The generated filename in the format 'image_band_band.tif'.
    """
    
    return image_band + '_' + band + '.tif'

def parse_reference_name(name = 'reference_layer', ci = 1, cn = 1):
    """
    Generate a reference name for an image, using different cores in parallel processing.
    Args:
        ci (int, optional): The first counter value. Defaults to 1.
        cn (int, optional): The second counter value. Defaults to 1.
    Returns:
        str: A formatted string representing the reference name in the format 'reference_{ci:09d}_{cn:09d}.tif'.
    """
    if ci == 1:
        return f'{name}.tif' # the first reference layer will be remained as the original name will not be deleted
    else:
        return f'{name}_{ci:09d}_{cn:09d}.tif'

def filter_missing_bands(image_folder, image_name, bands):
    """
    Identifies bands that are missing in the specified image folder.

    Args:
        image_folder (str): Path to the folder where images are stored.
        image_name (str): Name of the image being processed.
        bands (list): List of band names to check.

    Returns:
        list: List of bands that do not exist in the image folder.
    """
    # If the image folder does not exist, create it and return all bands
    if not os.path.exists(image_folder):
        return bands
    else:
        # Check for missing bands in the folder
        missing_bands = []
        for band in bands:
            band_filename = parse_band_name(image_name, band)
            if not os.path.exists(os.path.join(image_folder, band_filename)):
                missing_bands.append(band)

        return missing_bands

def read_image(filepath):
    """
    Reads an image from the specified file path using rasterio and returns the image data and its profile.
    Args:
        filepath (str): The path to the image file to be read.
    Returns:
        tuple: A tuple containing:
            - data (numpy.ndarray): The image data read from the file.
            - profile (dict): The profile metadata of the image.
    """
    
    # read the profile of the downloaded image
    with rasterio.open(filepath) as src:
        profile = src.profile
        data = src.read(1)
    return data, profile

def save_image(filepath, data, profile):
    """
    Saves an image to the specified file path using rasterio.
    Args:
        filepath (str): The path to the image file to be saved.
        data (numpy.ndarray): The image data to be saved.
        profile (dict): The profile metadata of the image.
    """
    
    # save the image
    with rasterio.open(filepath, 'w', **profile) as dst:
        dst.write(data, 1)       
    
def get_reference_profile(filepath_reference):
    """
    Reads a GeoTIFF file and extracts its Coordinate Reference System (CRS) and affine transformation matrix.
    Args:
        filepath_reference (str): The file path to the reference GeoTIFF file.
    Returns:
        tuple: A tuple containing:
            - crs (str): The CRS in Well-Known Text (WKT) format.
            - crs_transformer (list): The affine transformation matrix as a list of six elements.
    """
    
    # read the GeoTIFF to get the CRS and transform information
    with rasterio.open(filepath_reference) as src:
        # get the profile
        profile = src.profile
        # according to the wkt, get the crs
        crs = src.crs.to_wkt()
        crs_transformer = src.transform  # Get the affine transformation matrix
    # covnert the transform to the crs_transformer
    crs_transformer = [crs_transformer.a, crs_transformer.b, crs_transformer.c, crs_transformer.d, crs_transformer.e, crs_transformer.f]
    return profile, crs, crs_transformer


def warp_image(image, imageprofile, likeprofile, resampling=rasterio.warp.Resampling.nearest):
    """
    Warps an image array to match the CRS, transform, width, and height of a target profile.
    
    Args:
        image (numpy.ndarray): The input image array (shape: [bands, height, width]).
        imageprofile (dict): The profile of the input image, containing CRS, transform, etc.
        likeprofile (dict): The target profile, containing CRS, transform, width, and height.
    
    Returns:
        numpy.ndarray: The warped image array (shape: [bands, target_height, target_width]).
    """
    
    # update the updated profile
    desprofile = likeprofile.copy()
    desprofile['dtype'] = imageprofile['dtype']
    desprofile['nodata'] = imageprofile['nodata']
    
    # Create an empty array to store the warped image
    warped_image = np.zeros(
        (likeprofile['height'], likeprofile['width']),
        dtype=desprofile['dtype'] # do not change the orginal data type
    )
    
    # Warp each band of the input image
    warp.reproject(
        source=image,  # Source band
        destination=warped_image,  # Destination band
        src_transform=imageprofile['transform'],  # Source affine transform
        src_crs=imageprofile['crs'],  # Source CRS
        dst_transform=desprofile['transform'],  # Target affine transform
        dst_crs=desprofile['crs'],  # Target CRS
        resampling=resampling,  # Resampling method
        dst_nodata=desprofile['nodata']   # do not change it
        )

    return warped_image, desprofile