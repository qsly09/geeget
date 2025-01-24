'''
download data from gee
'''

import os
from pathlib import Path
import requests
import ee
from .utils import (
    parse_gee_roi,
    parse_gee_date,
    parse_band_name,
    parse_reference_name,
    filter_missing_bands,
    get_reference_profile,
    warp_image,
    read_image,
    save_image,
)
from .constants import (
    GEE_HLSL30_ADDRESS,
    GEE_HLSS30_ADDRESS,
    GEE_HLSL30_BANDS,
    GEE_HLSS30_BANDS,
)

def download_single_band(destination, image, band, region, resolution, band_name=""):
    """
    Downloads a single band from a gee image and saves it to the specified destination.
    Args:
        destination (str): The directory where the downloaded band image will be saved.
        image (ee.Image): The Earth Engine image object from which the band will be downloaded.
        band (str): The name of the band to download.
        region (dict): The region to download, specified as a GeoJSON dictionary.
        resolution (int): The resolution (in meters) for the downloaded image.
    Raises:
        HTTPError: If the request to download the image fails.
    Returns:
        None
    """

    # to get the image name from the folderpath
    image_name = os.path.basename(destination)
    if band_name == "":
        band_name = parse_band_name(image_name, band)
    filepath_band = os.path.join(destination, band_name)

    # download image with boundle
    image_url = image.getDownloadUrl(
        {
            "name": image_name,
            "bands": [band],
            "region": region,
            "scale": resolution,
            "format": "GEO_TIFF",
        }
    )

    response = requests.get(image_url, timeout=120, stream=True)  # 120 secs timeout
    if response.status_code != 200:
        raise response.raise_for_status()

    with open(filepath_band.replace(".tif", ".part.tif"), "wb") as fd:
        fd.write(response.content)
    os.rename(filepath_band.replace(".tif", ".part.tif"), filepath_band)
    return filepath_band


def hls(destination, date, extent, bands, sensor="L30", resolution=30, ci=1, cn=1):
    """
    Downloads Harmonized Landsat and Sentinel-2 (HLS) data from Google Earth Engine (GEE) for a specified date range and region of interest.

    Parameters:
    destination (str): The directory where the downloaded data will be saved.
    date (str): The date or date range for which to download the data. Format should be 'YYYY-MM-DD' or 'YYYY-MM-DD/YYYY-MM-DD'.
    extent (str): The region of interest in GEE format or as a path to a GeoTIFF file.
    bands (str): The bands to download. If empty, default bands for the sensor will be used.
    sensor (str, optional): The sensor type, either "L30" for Landsat or "S30" for Sentinel-2. Default is "L30".
    resolution (int, optional): The spatial resolution of the downloaded images. Default is 30 meters.
    ci (int, optional): The index of the current parallel process. Default is 1.
    cn (int, optional): The total number of parallel processes. Default is 1.

    Returns:
    None

    Notes:
    - The function will create a directory structure under the specified destination to store the downloaded data.
    - If the extent is not a GeoTIFF file, the function will download the first image from the GEE archive as a reference layer.
    - The function supports parallel downloading by splitting the image list based on the ci and cn parameters.
    - The downloaded images will be reprojected to match the reference layer and saved in GeoTIFF format.
    """

    # check if bands is empty
    if sensor == "L30":
        gee_hls_address = GEE_HLSL30_ADDRESS
        if bands == "":
            bands = GEE_HLSL30_BANDS
    elif sensor == "S30":
        gee_hls_address = GEE_HLSS30_ADDRESS
        if bands == "":
            bands = GEE_HLSS30_BANDS
    else:
        raise ValueError("Invalid sensor type. Please specify either 'L30' or 'S30'.")

    # convert date to date_start and date_end
    date_start, date_end = parse_gee_date(date)
    # convert extent to gee format
    roi_gee = parse_gee_roi(extent)
    # path
    destination = Path(destination)

    # see details at https://developers.google.com/earth-engine/datasets/catalog/NASA_HLS_HLSL30_v002
    # get the image collection
    collection = (
        ee.ImageCollection(gee_hls_address)
        .filterDate(date_start, date_end)
        .filterBounds(roi_gee)
    )
    # get the list of the selected images
    image_list_gee = ee.List(collection.toList(collection.size()))
    image_list_loc = image_list_gee.getInfo()

    folderpath_data = destination.joinpath("HLS")
    folderpath_data.mkdir(parents=True, exist_ok=True)

    if not extent.endswith(".tif"):
        # download the first image of gee archieve as reference layer
        image = ee.Image(image_list_gee.get(1))
        filepath_reference = destination.joinpath(parse_reference_name(ci=1))
        if not os.path.isfile(filepath_reference):
            reference_image_band = parse_reference_name(ci=ci, cn=cn)
            filepath_reference = download_single_band(
                str(destination),
                image,
                "B5",
                roi_gee,
                resolution,
                band_name=reference_image_band,
            )  # any band is ok, here we used B5
        likeprofile, likepcrs, liketransformer = get_reference_profile(filepath_reference)
        print(
            "The reference layer has been downloaded with the first image from the GEE archive."
        )
    else:
        # using a geotiff file as the reference layer
        likeprofile, likepcrs, liketransformer = get_reference_profile(extent)  

    print(f"Start downloading the HLS data from {date_start} to {date_end}:")
    

    # split the image list in parallel by ci and cn
    len_images = len(image_list_loc)
    # using ic and cn to access the image list
    for i in range(ci - 1, len_images, cn):
        image_loc = image_list_loc[i]
        # to get the image name, i.e., T18SUH_20200112T154027
        image_name = sensor + "_" + image_loc["properties"]["system:index"]
        folderpath_image = folderpath_data.joinpath(image_name)
        folderpath_image.mkdir(parents=True, exist_ok=True)

        # check existing bands
        bands_lack = filter_missing_bands(
            str(folderpath_image), image_name, bands
        )  # to get the bands that need to be downloaded
        if len(bands_lack) == 0:
            continue

        # download the missing bands
        image_gee = ee.Image(image_list_gee.get(i)).reproject(
            crs=likepcrs, crsTransform=liketransformer
        )
        for band in bands_lack:
            # define a part name for the band image for remaining for further processing
            band_name = parse_band_name(image_name, band).replace(".tif", ".part.tif")
            # download the band
            filepath_band = download_single_band(str(folderpath_image), image_gee, band, roi_gee, resolution, band_name = band_name)
            # read the profile of the downloaded image
            band_data, imageprofile = read_image(filepath_band)
            # warp the image to the reference layer
            band_data, desprofile = warp_image(band_data, imageprofile, likeprofile)
            # save the warped image
            save_image(filepath_band, band_data, desprofile)
            # change the part name to the original name
            os.rename(filepath_band, filepath_band.replace(".part.tif", ".tif"))
        print(f"{i + 1:09d}/{len_images:09d} {image_name}")
    if (
        ci > 1
    ):  # remove reference layer, but only reserve the first reference layer as normal layer
        os.remove(filepath_reference)
