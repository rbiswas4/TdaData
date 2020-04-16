

__all__ = ['read_simsurvey', 'simsurvey_select']
import numpy as np
import pandas as pd
import simsurvey
from astropy.table import Table

def simsurvey_select(lcs, meta, phot):
    """
    Do selection on the basis of metadata in simsurvey

    Paramaeters
    -----------
    lcs : Instance of `simsurvey.LightcurveCollection`

    Returns
    -------
    meta : `pd.DataFrame`
        metadata of selected simulated SN

    phot : 
    """
    mask = (lcs.stats['mag_max']['p48g'] < 18.5 ) |(lcs.stats['mag_max']['p48r'] < 18.5 )
    meta = pd.DataFrame(lcs.meta)

    # Keep the order before any selection to pick out lcs
    meta['order'] = np.arange(len(meta))
    # print('Checking meta idx_orig')
    # print(meta['idx_orig'].describe())

    # Obtain original order
    meta['idx_orig'] = meta['idx_orig']

    # Now select
    meta = meta[mask]
    # print(meta.reset_index().columns)
    meta.rename(columns=dict(idx_orig='tid'), inplace=True)
    # print('Checking meta idx after changing names')
    # print(meta['tid'].describe())
    meta.set_index('tid', inplace=True)


    idxs = meta.reset_index().tid.values
    order = meta.reset_index().order.values


    # Pick the selected light curve by using the order column of meta
    lc_list = []
    for i, idx in zip(order, idxs):
        lc = lcs.lcs[i]
        lcpdf = Table(lc).to_pandas()
        lcpdf['tid'] = idx
        lc_list.append(lcpdf)
    phot = pd.concat(lc_list)

    return meta, phot
def read_simsurvey(pkl_fname,
                   shift_idx=0,
                   sim_suffix=None,
                   meta_selection_func=None,
                   ind_lc_selection_func=None,
                   phot_selection=None,
                   params_fname=None, mapping_dict=None):
    """
    Parameters
    ----------
    pkl_fname : str
        absolute path of output of simsurvey

    params_fname : str, defaults to `None`
        if present, combine with simulation outputs.

    mapping_dict : dict, defaults to `None`
        dictionary with keys from params_fname to keys intended.

    meta_selection_func : method, defaults to `None`
        method for selection that is applied to the pickle output from
        `sim-survey`

    Notes
    -----
    """
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
        meta = meta_selection_func(lcs, meta)

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
            if ind_lc_selection_func(lcpdf):
                lc_list.append(lcpdf)
        else:
            lc_list.append(lcpdf)

    # photometry table
    phot = pd.concat(lc_list)
    
    if phot_selection is not None:
        meta, phot = phot_selection(meta, phot, lcs)

    return meta, phot
