'''
Author: Shi Qiu
Initial Time: 2025-01-09 16:00:00
Last Edit Time: 2025-01-09 16:00:00

Description:
A command-line interface (CLI) to make the package user-friendly.


Tested regions:
SERC (Smithsonian Env Research Center, MD):  [-76.6684662 ,  38.82467197, -76.42889892,  38.98579013]
Howland Forest, Maine:  [-68.82500705,  45.11237216, -68.60006578,  45.27336056]
Railroad Valley, NV:  [-115.79578886,   38.400624  , -115.57312436,   38.6060549 ]
White Sands, NM: [-106.50812095,   32.75797882, -106.14617191,   33.08320348]
'''

import os
import sys
import click
# Add the parent directory to this package to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import download as gd # GEE Data Download

gd.authenticate()

@click.command()
@click.option("--ci",          "-i", default=1, type=int, help="The core's id")
@click.option("--cn",          "-n", default=2, type=int, help="The number of cores")
@click.option("--product",     "-p", default="HLS", type=str, help="The product to download, such as HLS")
@click.option("--sensor",      "-s", default="S30", type=str, help="The sensor of the data, L30, S30; if not specified, the default sensor is L30")
@click.option("--bands",       "-b", default="B2,B3,B4,B8A,B11,B12,Fmask", type=str, help="The bands of the data; if not specified, all bands will be downloaded")
@click.option("--date",        "-d", default="20130411-20241231", type=str, help="The date range of the data, format: yyyymmdd(start)-yyyymmdd(end), like 20010101-20011231")
@click.option("--extent",      "-e", default="[-76.6684662 ,  38.82467197, -76.42889892,  38.98579013]", type=str, help="The extent of the data, format: minLon,minLat,maxLon,maxLat")
@click.option("--destination", "-l", default="/gpfs/sharedfs1/zhulab/Shi/ProjectSythetic/Test/SERC", type=str, help="The filepath of the data's location")
def main(ci, cn, product, sensor, bands, date, extent, destination):
    """
    Main function to download satellite data based on the specified parameters.
    Parameters:
    ci (int): Number of concurrent instances for parallel processing.
    cn (int): Number of concurrent nodes for parallel processing.
    product (str): Name of the satellite product to download. Currently supports "HLS".
    bands (str): Comma-separated list of bands to download. If empty, all bands will be downloaded.
    date (str): Date for the data to be downloaded.
    extent (list): Spatial extent for the data download in the format [min_lon, min_lat, max_lon, max_lat].
    destination (str): Path to the directory where the downloaded data will be saved.
    Raises:
    ValueError: If an invalid product name is provided.
    """
    
    if bands != '':
        bands = [band.strip() for band in bands.split(',')]
    # compare the product name to determine which download function to call
    if product.upper() == "HLS":
        gd.hls(destination,
               date,
               extent,
               sensor = sensor,
               bands = bands,
               ci = ci,
               cn = cn, # set up the parallelism
               )
    else:
        raise ValueError("Invalid product name. Please choose from: HLS")

if __name__ == "__main__":
    main()
