import os
import simsurvey
import pandas as pd
import tdd
from tdd import read_simsurvey, example_data,  select_using_simsurvey_meta
import pytest

def test_read_simsurvey():
    lcs_fname  = os.path.join(example_data,
                              'salt2_ex_lcs.pkl')
    params_fname = os.path.join(example_data,
                                'salt2_ex_params.csv')

    # read in params, and replace index name
    params = pd.read_csv(params_fname)
    params.rename(columns=dict(idx='tid'), inplace=True)
    params.set_index('tid', inplace=True)

    meta_all, phot_all = read_simsurvey(lcs_fname, shift_idx=0, sim_suffix=0,
                                        meta_selection_func=None, 
                                        threshold_for_lc=1,
                                        params=params, phot_selection_func=None)
    
    assert len(meta_all) == 8

    return meta_all, phot_all

def test_read_simsurvey_with_selection():

    lcs_fname  = os.path.join(example_data,
                              'salt2_ex_lcs.pkl')
    params_fname = os.path.join(example_data,
                                'salt2_ex_params.csv')

    # read in params, and replace index name
    params = pd.read_csv(params_fname)
    params.rename(columns=dict(idx='tid'), inplace=True)
    params.set_index('tid', inplace=True)

    meta_all, phot_all = read_simsurvey(lcs_fname, shift_idx=0, sim_suffix=0,
                                        meta_selection_func=select_using_simsurvey_meta, 
                                        threshold_for_lc=2,
                                        keep_all_simulated_meta=False,
                                        params=params, phot_selection_func=None)
    
    assert len(meta_all) == 8

    return meta_all, phot_all

@pytest.mark.xfail(simsurvey.__version__ == '0.6.0', reason="lcs.meta_notobserved not implemented in release")
def test_read_simsurvey_with_selection_keeping_all_params():

    lcs_fname  = os.path.join(example_data,
                              'salt2_ex_lcs.pkl')
    params_fname = os.path.join(example_data,
                                'salt2_ex_params.csv')

    # read in params, and replace index name
    params = pd.read_csv(params_fname)
    params.rename(columns=dict(idx='tid'), inplace=True)
    params.set_index('tid', inplace=True)

    meta_all, phot_all = read_simsurvey(lcs_fname, shift_idx=0, sim_suffix=0,
                                        meta_selection_func=select_using_simsurvey_meta, 
                                        threshold_for_lc=2,
                                        keep_all_simulated_meta=True,
                                        params=params, phot_selection_func=None)
    
    assert len(meta_all.query('selected == 2')) == 5
    assert len(meta_all.query('selected > 0')) == 8
    assert len(meta_all) == len(params)

    return meta_all, phot_all

def test_read_simsurvey_with_no_params():
    lcs_fname  = os.path.join(example_data,
                              'salt2_ex_lcs.pkl')
    meta_all, phot_all = read_simsurvey(lcs_fname, shift_idx=0, sim_suffix=0,
                                        meta_selection_func=None,
                                        threshold_for_lc=1,
                                        params=None, phot_selection_func=None)
    
    assert len(meta_all) == 8

    return meta_all, phot_all
