'''
Author: Shi Qiu
Initial Time: 2025-01-09 16:00:00
Last Edit Time: 2025-01-09 16:00:00

Description:
This function attempts to initialize the Google Earth Engine (GEE) API. If the
initialization fails due to authentication issues, it triggers the authentication
flow, which requires user interaction to complete. Once authenticated, it reinitializes
the GEE API.

Raises:
    ee.EEException: If the initialization fails and authentication is required.
'''

import ee

def authenticate():
    """
    Authenticate and initialize the Google Earth Engine API.

    If the user is already authenticated, the function initializes the API.
    If authentication is required, it prompts the user to authenticate
    and then reinitializes the API upon successful authentication.

    Raises:
        ee.EEException: If initialization fails and authentication is required.
    """
    try:
        # Attempt to initialize the Earth Engine API
        ee.Initialize()
        print("Google Earth Engine API initialized successfully.")
    except ee.EEException:
        # Handle cases where authentication is required
        print("Authentication required.")
        print("Redirecting to authentication flow... (Use Jupyter Notebook for easier interaction)")
        
        # Trigger the authentication process
        ee.Authenticate()
        print("Authentication completed.")
        
        # Reinitialize the Earth Engine API after authentication
        ee.Initialize()
        print("Google Earth Engine API initialized successfully.")
