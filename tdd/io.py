"""
Class for io :
    - Should have methods to take data and transform to a photometry table and light curves
    - Should have methods to transform to light curves
"""
from __future__ import absolute_import, print_function, division
from future.utils import with_metaclass

__all__ = ['read_plasticc_data']

import abc
import numpy as np
import pandas as pd
from astropy.table import Table


def read_plasticc_data(metadata_fname, photometry_fname):
    """

    """
    metadata = pd.read_csv(metadata_fname)
    photometry = pd.read_csv(photometry_fname)
    return metadata, photometry



