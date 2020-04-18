"""
Class for io :
    - Should have methods to take data and transform to a photometry table and light curves
    - Should have methods to transform to light curves
"""
from __future__ import absolute_import, print_function, division
from future.utils import with_metaclass

__all__ = ['read_plasticc_data', 'standardize', 'fix_bandpass']
import numpy as np
import pandas as pd
from .aliases import standard_aliases, alias_dict

def standardize(df, index_column=None):
    
    # standard aliases in tdd
    std_aliases =  standard_aliases()
    a_dict = alias_dict(df.columns, std_aliases)
    df.rename(columns=a_dict, inplace=True)

    if index_column is not None:
        df.set_index(index_column, inplace=True)
    return None

def fix_bandpass(photometry, band_orig=(0, 1, 2, 3, 4, 5,),
                 band_names=('lsstu', 'lsstg', 'lsstr', 'lssti', 'lsstz', 'lssty',)):

    photometry.band = photometry.band.replace(band_orig, band_names)
    return None

def read_plasticc_data(metadata_fname, photometry_fname, band_orig=(0, 1, 2, 3, 4, 5,),
                       band_names=('lsstu', 'lsstg', 'lsstr', 'lssti', 'lsstz', 'lssty',),
                       zp=27.5):
    """
    function to read the plasticc data from a single metadata and 
    photometry csv file
    """
    metadata = pd.read_csv(metadata_fname)
    photometry = pd.read_csv(photometry_fname)

    standardize(metadata, index_column='tid')
    standardize(photometry)

    fix_bandpass(photometry, band_orig=band_orig, band_names=band_names)
    photometry['zp'] = zp
    photometry['zpsys'] = 'ab'

    return metadata, photometry

