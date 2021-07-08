#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: s1_ard.py
Version: v1.2
Date: 2021-03-10
Authors: Mullissa A., Vollrath A., Braun, C., Slagter B., Balling J., Gou Y., Gorelick N.,  Reiche J.
Description: This script creates an analysis ready S1 image collection.
License: This code is distributed under the MIT License.

    Parameter:
        START_DATE: The earliest date to include images for (inclusive).
        END_DATE: The latest date to include images for (exclusive).
        POLARIZATION: The Sentinel-1 image polarization to select for processing.
            'VV' - selects the VV polarization.
            'VH' - selects the VH polarization.
            "VVVH' - selects both the VV and VH polarization for processing.
        ORBIT:  The orbits to include. (string: BOTH, ASCENDING or DESCENDING)
        GEOMETRY: The region to include imagery within.
                  The user can interactively draw a bounding box within the map window or define the edge coordinates.
        APPLY_BORDER_NOISE_CORRECTION: (Optional) true or false options to apply additional Border noise correction:
        APPLY_SPECKLE_FILTERING: (Optional) true or false options to apply speckle filter
        SPECKLE_FILTER: Type of speckle filtering to apply (String). If the APPLY_SPECKLE_FILTERING parameter is true then the selected speckle filter type will be used.
            'BOXCAR' - Applies a boxcar filter on each individual image in the collection
            'LEE' - Applies a Lee filter on each individual image in the collection based on [1]
            'GAMMA MAP' - Applies a Gamma maximum a-posterior speckle filter on each individual image in the collection based on [2] & [3]
            'REFINED LEE' - Applies the Refined Lee speckle filter on each individual image in the collection
                                  based on [4]
            'LEE SIGMA' - Applies the improved Lee sigma speckle filter on each individual image in the collection
                                  based on [5]
        SPECKLE_FILTER_FRAMEWORK: is the framework where filtering is applied (String). It can be 'MONO' or 'MULTI'. In the MONO case
                                  the filtering is applied to each image in the collection individually. Whereas, in the MULTI case,
                                  the Multitemporal Speckle filter is applied based on  [6] with any of the above mentioned speckle filters.
        SPECKLE_FILTER_KERNEL_SIZE: is the size of the filter spatial window applied in speckle filtering. It must be a positive odd integer.
        SPECKLE_FILTER_NR_OF_IMAGES: is the number of images to use in the multi-temporal speckle filter framework. All images are selected before the date of image to be filtered.
                                    However, if there are not enough images before it then images after the date are selected.
        TERRAIN_FLATTENING : (Optional) true or false option to apply Terrain correction based on [7] & [8]. 
        TERRAIN_FLATTENING_MODEL : model to use for radiometric terrain normalization (DIRECT, or VOLUME)
        DEM : digital elevation model (DEM) to use (as EE asset)
        TERRAIN_FLATTENING_ADDITIONAL_LAYOVER_SHADOW_BUFFER : additional buffer parameter for passive layover/shadow mask in meters
        FORMAT : the output format for the processed collection. this can be 'LINEAR' or 'DB'.
        CLIP_TO_ROI: (Optional) Clip the processed image to the region of interest.
        SAVE_ASSETS : (Optional) Exports the processed collection to an asset.
        ASSET_ID : (Optional) The user id path to save the assets
        
    Returns:
        An ee.ImageCollection with an analysis ready Sentinel 1 imagery with the specified polarization images and angle band.
        
References
  [1]  J. S. Lee, “Digital image enhancement and noise filtering by use of local statistics,” 
    IEEE Pattern Anal. Machine Intell., vol. PAMI-2, pp. 165–168, Mar. 1980. 
  [2]  A. Lopes, R. Touzi, and E. Nezry, “Adaptative speckle filters and scene heterogeneity,
    IEEE Trans. Geosci. Remote Sensing, vol. 28, pp. 992–1000, Nov. 1990 
  [3]  Lopes, A.; Nezry, E.; Touzi, R.; Laur, H.  Maximum a posteriori speckle filtering and first204order texture models in SAR images.  
    10th annual international symposium on geoscience205and remote sensing. Ieee, 1990, pp. 2409–2412.
  [4] J.-S. Lee, M.R. Grunes, G. De Grandi. Polarimetric SAR speckle filtering and its implication for classification
    IEEE Trans. Geosci. Remote Sens., 37 (5) (1999), pp. 2363-2373.
  [5] Lee, J.-S.; Wen, J.-H.; Ainsworth, T.L.; Chen, K.-S.; Chen, A.J. Improved sigma filter for speckle filtering of SAR imagery. 
    IEEE Trans. Geosci. Remote Sens. 2009, 47, 202–213.
  [6] S. Quegan and J. J. Yu, “Filtering of multichannel SAR images, IEEE Trans Geosci. Remote Sensing, vol. 39, Nov. 2001.
  [7] Vollrath, A., Mullissa, A., & Reiche, J. (2020). Angular-Based Radiometric Slope Correction for Sentinel-1 on Google Earth Engine. 
    Remote Sensing, 12(11), [1867]. https://doi.org/10.3390/rs12111867
  [8] Hoekman, D.H.;  Reiche, J.   Multi-model radiometric slope correction of SAR images of221complex terrain using a two-stage semi-empirical approach.
    Remote Sensing of Environment 2222015,156, 1–10.

    """
import os

import wrapper as wp
import ee
import speckle_filter as sf




parameter = {
    'START_DATE': '2021-01-01',
    'STOP_DATE': '2021-07-01',
    'POLARIZATION': 'VVVH',
    # 'POLARIZATION': 'VV',
    'ORBIT': 'DESCENDING',
    # 'ROI': ee.Geometry.Rectangle([-47.1634, -3.00071, -45.92746, -5.43836]),
    'ROI': ee.Geometry.Rectangle([5.71773, 52.65939, 5.7766, 52.7029]),
    'APPLY_BORDER_NOISE_CORRECTION': True,
    'APPLY_SPECKLE_FILTERING': True,
    'SPECKLE_FILTER_FRAMEWORK': 'MULTI',
    # 'SPECKLE_FILTER': 'GAMMA MAP',
    # 'SPECKLE_FILTER': 'REFINED LEE',
    'SPECKLE_FILTER': 'LEE',
    'SPECKLE_FILTER_KERNEL_SIZE': 9,
    'SPECKLE_FILTER_NR_OF_IMAGES': 10,
    'APPLY_TERRAIN_FLATTENING': True,
    'DEM': ee.Image('USGS/SRTMGL1_003'),
    'TERRAIN_FLATTENING_MODEL': 'VOLUME',
    'TERRAIN_FLATTENING_ADDITIONAL_LAYOVER_SHADOW_BUFFER': 0,
    'FORMAT': 'DB',
    'CLIP_TO_ROI': True,
    'SAVE_ASSET': False,
    'ASSET_ID': "users/adugnagirma"
}


import requests
import io
import zipfile
from zipfile import ZipFile
from typing import Union as U, Optional as O
import datetime as dt
from tqdm import tqdm


# MAP_S1_FNS = {
#     'VV': 'download.VV.tif',
#     'VH': 'download.VH.tif',
#     'angle': 'download.angle.tif',
# }

MAP_S1_FNS = {
    'VV': 'VV.tif',
    'VH': 'VH.tif',
    'angle': 'angle.tif',
}


def map_gee_zip(path_zip: U[str, ZipFile], map_fn: dict, to_bytes=False) -> dict:
    if isinstance(path_zip, str):
        z = ZipFile(path_zip)
    else:
        z = path_zip
    lst_ = z.filelist
    ret = {}
    for x in lst_:
        fn = x.filename
        s = fn.split('.')[-2]
        if s in map_fn:
            if to_bytes:
                with z.open(x, 'r') as fz:
                    # ret[map_fn[s]] = fz.read()
                    ret[s] = fz.read()
            else:
                # ret[map_fn[s]] = f'/vsizip/{path_zip}/{fn}'
                ret[s] = f'/vsizip/{path_zip}/{fn}'
    return ret


def get_data(url: str) -> dict:
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        buffer = io.BytesIO()
        buffer.write(r.content)
    with zipfile.ZipFile(buffer, 'r') as fz:
        data = map_gee_zip(fz, MAP_S1_FNS, to_bytes=True)
    return data


def save_data(data: dict, dir_out: str, map_fns: O[dict] = None) -> bool:
    if map_fns is None:
        map_fns = MAP_S1_FNS
    ret = True
    for x, y in data.items():
        path_out = os.path.join(dir_out, map_fns[x])
        os.makedirs(os.path.dirname(path_out), exist_ok=True)
        with open(path_out, 'wb') as f:
            f.write(y)
        if not os.path.isfile(path_out):
            ret = False
    return ret


if __name__ == '__main__':
    ee.Initialize()
    print('-')
    is_raw = False

    # processed s1 collection
    s1_processed = wp.s1_preproc(parameter, skip_processing=is_raw)
    s1_processed_list = s1_processed.toList(s1_processed.size())
    ee_infos = s1_processed_list.getInfo()

    # roi = parameter['ROI']
    # col = s1 = ee.ImageCollection('COPERNICUS/S1_GRD_FLOAT') \
    #     .filter(ee.Filter.eq('instrumentMode', 'IW')) \
    #     .filterDate('2021-03-01', '2021-04-01') \
    #     .filterBounds(roi)
    # ee_image = col.first().clip(roi)
    # # ee_image_flt = sf.gammamap(ee_image, 9)
    # ee_image_flt = sf.leefilter(ee_image, 9)

    dir_out: str = '/home/ar/tmp/222/processing_lee'
    for xi, x in enumerate(tqdm(ee_infos)):
        date_id = dt.datetime.isoformat(dt.datetime.strptime(x['properties']['system:index'].split('_')[4][:8], '%Y%m%d'))[:10]
        if is_raw:
            map_fns = {z1: f'{date_id}-{z1}-raw.tif' for z1, z2 in MAP_S1_FNS.items()}
        else:
            map_fns = {z1: f'{date_id}-{z1}.tif' for z1, z2 in MAP_S1_FNS.items()}
        ee_image = ee.Image(s1_processed_list.get(xi))
        url = ee_image.getDownloadURL()
        data = get_data(url)
        #
        tmp_ = save_data(data, dir_out, map_fns)

    print('-')