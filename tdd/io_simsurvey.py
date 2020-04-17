

__all__ = ['read_simsurvey', 'select_using_simsurvey_meta']
import numpy as np
import pandas as pd
import simsurvey
from astropy.table import Table
from numpy.testing import assert_allclose

def select_using_simsurvey_meta(lcs, meta):
    """
    Do selection on the basis of metadata in `simsurvey`. The metadata can be the records of simulated transient
    properties or summaries stored in the simulation. This form of selection should not use the light curves.

    Parameters
    -----------
    lcs : Instance of `simsurvey.LightcurveCollection`

    meta : `pd.DataFrame`
        metadata of detected `simsurvey`

    Returns
    -------
    meta : `pd.DataFrame`
        metadata of selected simulated SN

    phot : 
    """
    mask = (lcs.stats['mag_max']['p48g'] < 18.5 ) |(lcs.stats['mag_max']['p48r'] < 18.5 )
    # Now select
    meta = meta[mask]

    return meta
def read_simsurvey(pkl_fname,
                   shift_idx=0,
                   sim_suffix=None,
                   meta_selection_func=None,
                   ind_lc_selection_func=None,
                   phot_selection=None,
                   params=None, mapping_dict=None):
    """
    Parameters
    ----------
    pkl_fname : str
        absolute path of output of simsurvey

    params : `pd.DataFrame`, defaults to `None`
        if present, combine with simulation outputs. Must have
        index `tid`.

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
            if ind_lc_selection_func(lcpdf):
                lc_list.append(lcpdf)
        else:
            lc_list.append(lcpdf)

    # photometry table
    phot = pd.concat(lc_list)
    phot['SNR'] = phot['flux']/phot['fluxerr']
    
    if phot_selection is not None:
        meta, phot = phot_selection(meta, phot, lcs)

    return meta, phot
