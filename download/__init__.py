'''
Author: Shi Qiu
Initial Time: 2025-01-09 16:15:00
Last Edit Time: 2025-01-09 16:15:00

Description:
This file initializes the Google Earth Engine authentication package.
It exposes the `authenticate` function for easy access when the package is imported.
'''

from .auth import authenticate
from .download import hls

# Explicitly define the public interface
__all__ = [
    'authenticate',
    'hls',
    ]  