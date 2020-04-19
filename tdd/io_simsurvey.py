__all__ = ['read_simsurvey', 'select_using_simsurvey_meta', 'convert_meta_to_dataframe']

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


def convert_meta_to_dataframe(meta, shift_idx=0, orig_order=True):
    """
    Parameters
    ----------
    meta : `np.recarray`
        a metadata array from `simsurvey` output

    shift_idx : `int`
        number to be added to `idx_orig` parameter to get
        desired `tid`

    orig_order :  `Bool`, defaults to `True`
        if not `False`, add a column `order` specifying the row order
        in the input `meta`


    Returns
    -------
    meta : `pd.DataFrame`
        array in the form of a dataframe, with index given by 
        `tid` set to values of `shift_idx + idx_orig`, where `idx_orig` is a
        column in the input parameter `meta`. If `orig_order` is not `False`,
        this also contains a column with the order of the rows in the input
        `meta_data`
    """
    meta = pd.DataFrame(meta)

    if orig_order :
        # Keep the order before any selection to pick out lcs
        meta['order'] = np.arange(len(meta))

    meta.rename(columns=dict(idx_orig='tid'), inplace=True)

    # Used to fix splits
    meta['tid'] += shift_idx 

    meta.set_index('tid', inplace=True)

    return meta

def read_simsurvey(pkl_fname,
                   params=None,
                   meta_selection_func=None,
                   phot_selection_func=None,
                   ind_lc_selection_func=None,
                   sim_suffix=None,
                   shift_idx=0,
                   keep_all_simulated_meta=False,
                   threshold_for_lc=2,
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

    keep_all_simulated_meta : `bool`, defaults to `False`
        if `True`, keeps metadata for unselected objects. The  objects rejected
        by simsurvey have a selection of 0. Objects not observed have a selection of -1.
        Objects cchosen by metadata selection has a `selection` of 2 by default.
    threshold_for_lc : {1 | 2} , defaults to 2
        minimum value of `selected` column in output metadata. Must be greater or equal to 1,
        which imply all light curves passing criteria supplied to input `simsurvey` simulation.
        The default value of 2 corresponds to the selection applied on the metadata via `meta_selection_func`.
        
    Notes
    -----
    While there is no way to get higher values of `threshold_for_lc`, the `selection` column may be changed
    for soecific objects in the returned `meta` dataframe, and used for later selection

    """
    if mapping_dict is not None:
        raise NotImplementedError('Not implemented yet\n')

    if threshold_for_lc < 0.997:
        raise ValueError('A threshold value < 1 reults in problems due to photometry file being empty')

    lcs = simsurvey.LightcurveCollection(load=pkl_fname)

    # meta = pd.DataFrame(lcs.meta)

    # # Keep the order before any selection to pick out lcs
    # meta['order'] = np.arange(len(meta))
    # meta.rename(columns=dict(idx_orig='tid'), inplace=True)

    # # Used to fix splits
    # meta['tid'] += shift_idx 

    # meta.set_index('tid', inplace=True)
    meta_detected = convert_meta_to_dataframe(lcs.meta, shift_idx=shift_idx,
                                              orig_order=True)
    meta_detected['selected'] = 1

    # Now select
    if meta_selection_func is not None:
        meta = meta_selection_func(meta_detected, lcs)
        sel = meta.index.values
        meta_detected.loc[sel, 'selected'] = 2


    if keep_all_simulated_meta :
        ## rejected
        meta_rejected = convert_meta_to_dataframe(lcs.meta_rejected, shift_idx=shift_idx,
                                                  orig_order=True)
        meta_rejected['selected'] = 0
    
        ## not observed
        meta_not_observed = convert_meta_to_dataframe(lcs.meta_notobserved, shift_idx=shift_idx,
                                                      orig_order=True)
        meta_not_observed['selected'] = -1

        meta = pd.concat([meta_detected, meta_rejected, meta_not_observed])
    else:
        meta = meta_detected

    # Do join with params at this stage before appending `sim_suffix`
    if params is not None:
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
    idxs = meta.query('selected == @threshold_for_lc').reset_index().tid.values
    order = meta.query('selected == @threshold_for_lc').reset_index().order.values


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
    phot['selected'] = threshold_for_lc
    
    
    if phot_selection_func is not None:
        meta, phot = phot_selection_func(meta, phot, lcs)

    return meta, phot
