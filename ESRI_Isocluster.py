# IsoCluster_sample.py
# Description: Uses isodata clustering to get characteristics of natural cell groupings in multi-dimension  attribute space.
# Requirements: None
# Author: ESRI
# Date: 12/01/03

# Import system modules
import sys, string, os, win32com.client

# Create the Geoprocessor object
gp = win32com.client.Dispatch("esriGeoprocessing.GpDispatch.1")

try:
# Set the workspace
    gp.Workspace = "D:\My Docs\working\in_images\yuc"

# Set local variables
    InRasters = "yuc01.img;" #raster2; raster3"
    OutSignatureFile = "isocluster_yuc01.gsg"
    InNumberClasses = "65"
    InNumberIterations = "3"
    InMinClassSize = "36"
    InSampleInterval = "2"

# Check out Spatial Analyst extension license
    gp.CheckOutExtension("Spatial")

# Process: IsoCluster
    gp.IsoCluster_sa(InRasters, OutSignatureFile, InNumberClasses, InNumberIterations, InMinClassSize,  InSampleInterval)

except:
# Print error message if an error occurs
    gp.GetMessages()
