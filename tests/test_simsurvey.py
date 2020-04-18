import os
import pandas as pd
import tdd
from tdd import read_simsurvey, example_data

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
                                        params=params, phot_selection_func=None)
    
    assert len(meta_all) == 8

    return meta_all, phot_all
