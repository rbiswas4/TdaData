import tdd
from tdd import (standard_aliases,
                 alias_dict,
                 standardize_sequence)

def test_std_aliases():
    mydict = standard_aliases()
    assert len(mydict) > 0 
    assert 'snid' in mydict['tid']
    assert 'expmjd' in mydict['mjd']


def test_alias_dict():
    """
    test for alias_dict function
    """
    aliases = dict(time=['mjd', 'expmjd'], flux=['counts'],\
                   fluxerr=['flux_err', 'fluxerror'], zpsys=['magsys'])
    test_seq = ['mJd', 'band', 'zp', 'Flux', 'fluxError', 'zpsys']
    val = alias_dict(test_seq, aliases) == {'Flux': 'flux', \
                                                 'fluxError': 'fluxerr',\
                                                 'mJd': 'time'}
    assert val

def test_standarizing_names():
    """
    test for standardizing names
    """
    aliases = dict(time=['mjd', 'expmjd'],
                   flux=['counts'], fluxerr=['flux_err', 'fluxerror'])
    test_seq = ['mJd', 'band', 'zp', 'Flux', 'fluxError']
    adict = alias_dict(test_seq, aliases)
    val = standardize_sequence(test_seq, adict) == ['time', 'band', 'zp',
                                                    'flux', 'fluxerr']
    assert val
