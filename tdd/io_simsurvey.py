__all__ = ['read_simsurvey', 'select_using_simsurvey_meta']

import numpy as np
import pandas as pd
import simsurvey
from astropy.table import Table
from numpy.testing import assert_allclose

def select_using_simsurvey_meta(meta, lcs):
    """
    Return the metadata of selected SN in a `pd.DataFrame` o the basis of
    data in the `meta` dataframe and summaries in
    `simsurvey.LightCurveCollection`.

    Parameters
    -----------
    meta : `pd.DataFrame`
        metadata of detected `simsurvey`

    lcs : Instance of `simsurvey.LightcurveCollection`
        Simulation output from `simsurvey`.

    Returns
    -------
    meta : `pd.DataFrame`
        metadata of selected simulated SN

    phot :  `pd.DataFrame`
        photometry table of selected simulated SN
    
    Notes
    -----
    This is mostly to be used as a fast filter to minimize the time spent in
    reading the pickle file and space required to store it.
    """
    mask = (lcs.stats['mag_max']['p48g'] < 18.5 ) \
            |(lcs.stats['mag_max']['p48r'] < 18.5 )

    # Now select
    meta = meta[mask]

    return meta

def read_simsurvey(pkl_fname,
                   params=None,
                   meta_selection_func=None,
                   phot_selection_func=None,
                   ind_lc_selection_func=None,
                   sim_suffix=None,
                   shift_idx=0,
                   mapping_dict=None):
    """
    Return a metadata and photometry table containing selected TDAs simulated
    in `simsurvey`. This can be filtered through the use of three selection
    functions for convenience. If a dataframe containing parameters used for
    the simulation is provided, these columns can be joined to the metadata. 
    Finally, `sim_suffix` allows one to track different realizations of a
    simulation while `shift_idx` is a number that can be added to the index.

    Parameters
    ----------
    pkl_fname : str
        absolute path of output of simsurvey

    params : `pd.DataFrame`, defaults to `None`
        if present, combine with simulation outputs. Must have
        index `tid`.

    meta_selection_func : method, defaults to `None`
        method for selection that is applied to the pickle output from
        `sim-survey`. If not `None` this selection is applied after output
        read in, but before individual light curves are read in. The idea
        is that this method should be applied to the metadata and summary
        statistics. The expected call signature is
        ```meta, phot = meta_selection_func(meta, lcs)```
    
    phot_selection_func : method, defaults to `None`
        if not `None`, applied to both the photometry and the metadata tables
        in an efficient manner avoiding loops. The method is expected to have
        a call signature
        ```meta, phot = phot_selection_func(meta, phot, lcs)``` 
                   
    ind_lc_selection_func : method, defaults to `None`
        if not `None` applied to individual light curves by looping over
        them. This is slower and less preferable to the other methods. The
        expected call signature is 
        ```meta, phot = phot_selection_func(meta, lcpdf, lcs)``` 

    shift_idx : int, defaults to `None`
        if not `None`, is added to the an integer `tid` of the
        `simsurvey.LightcurveColletion` output recorded as `idx_orig` in
        `lcs.meta`. Used when a single parameter table is split into several
        of equal size and simulated in parallel.
    sim_suffix : int/string, defaults to `None`
        if not `None` added to the transient id `tid` with an underscore
        resulting in `f'{tid}_{sim_suffix}'`
    mapping_dict : dict, defaults to `None`
        dictionary with keys from params_fname to keys intended.
        Not implemented yet. The user must make this change themselves.


    Notes
    -----

    """
    if mapping_dict is not None:
        raise NotImplementedError('Not implemented yet\n')

    lcs = simsurvey.LightcurveCollection(load=pkl_fname)

    meta = pd.DataFrame(lcs.meta)

    # Keep the order before any selection to pick out lcs
    meta['order'] = np.arange(len(meta))
    meta.rename(columns=dict(idx_orig='tid'), inplace=True)

    # Used to fix splits
    meta['tid'] += shift_idx 

    meta.set_index('tid', inplace=True)

    # Now select
    if meta_selection_func is not None:
        meta = meta_selection_func(meta, lcs)

    # Do join with params at this stage before appending `sim_suffix`
    meta = meta.join(params, rsuffix='_input')
    
    # Check join OK if possible, and drop extra columnsdroplist = []
    drop_list = []
    for name in meta.columns.values:
        if '_input' in name:
            drop_list.append(name)
            orig = name.split('_input')[0]
            assert_allclose(meta[orig].values, meta[name].values)
    
    meta = meta.drop(columns=drop_list)
            
    # Append simulation identity to signify different sims
    if sim_suffix is None:
        meta.index = meta.reset_index()\
            .tid.apply(lambda x: f'{x}')
    else:
        meta.index = meta.reset_index()\
            .tid.apply(lambda x: f'{x}_{sim_suffix}')

    # Put tid in phots
    idxs = meta.reset_index().tid.values
    order = meta.reset_index().order.values


    # Pick the selected light curve by using the order column of meta
    lc_list = []
    for i, idx in zip(order, idxs):
        lc = lcs.lcs[i]
        lcpdf = Table(lc).to_pandas()
        lcpdf['tid'] = idx
        if ind_lc_selection_func is not None:
            if ind_lc_selection_func(meta, lcpdf, lcs):
                lc_list.append(lcpdf)
        else:
            lc_list.append(lcpdf)

    # photometry table
    phot = pd.concat(lc_list)
    phot['SNR'] = phot['flux']/phot['fluxerr']
    
    if phot_selection_func is not None:
        meta, phot = phot_selection_func(meta, phot, lcs)

    return meta, phot
