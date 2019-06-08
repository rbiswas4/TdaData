"""
Some utilities for aliases. Used to change dataframe column names to a standard
 set of names.
"""
from __future__ import division, absolute_import, print_function
from future.builtins import dict
__all__ = ['alias_dict', 'standardize_sequence', 'standard_aliases']

def alias_dict(sequence, aliases):
    """
    Given a dictionary of
    aliases of the form {standard_string_names: list of possible aliases}
    this finds occurances of aliases (ignoring capitalization) in the sequence
    of strings called sequence and returns a dictionary
    Dict(alias: standard_string_name)

    Parameters
    ----------
    sequence : a sequence of strings
    aliases : Dictionary with list-valued values
        dictionary with keys = standard desired names, value = possible aliases
        It is assumed that a single alias only works for a single key

    Returns
    -------
    Dictionary with keys in the sequence of strings that have been identified
    as a possible alias of standard_string_names with
    value =standard_string_names

    Examples
    ---------
    >>> aliases = dict(time=['mjd','expmjd'], flux=['counts'],\
                       fluxerr=['flux_err', 'fluxerror'], zpsys=['magsys'])
    >>> testSeq = ['mJd', 'band', 'zp', 'Flux', 'fluxError', 'zpsys']
    >>> alias_dict(testSeq, aliases) == {'Flux': 'flux', \
                                              'fluxError': 'fluxerr',\
                                              'mJd': 'time'}
    True


    Notes:
    ------
    1. It is obviously imperative that the list of possible aliases combined
    for all keys should not have duplicates
    2. The dictionary can be used to change non-standard column names in a
    `pd.DataFrame` through the use of `dataFrame.rename(columns=alias_dictionary,
    inplace=True)`
    """

    # Check that there is no string which might be the alias of more than one
    # variable
    _valueList = list(x for l in aliases.values() for x in l)
    assert len(set(_valueList)) == len(_valueList)

    # insert the standard name in the list of values
    # (necesary for the case where variable names are std names with caps)
    _ = [aliases.update({key: [key] + aliases[key]}) for key in aliases.keys()]

    # invert aliases dictionary to get
    inverse_dict = dict()
    _ = [inverse_dict.update({alias:aliastuple[0]})
         for aliastuple in aliases.items() for alias in aliastuple[1]]

    # Account for capitalization issues
    testDict = dict((s.lower(), s) for s in sequence)
    aliasedSet = set(inverse_dict.keys()) & set(testDict.keys())


    # return the dictionary
    alias_dict = dict((testDict[key], inverse_dict[key]) for key in aliasedSet
                     if testDict[key] != inverse_dict[key])

    return alias_dict

def standardize_sequence(sequence, alias_dict):
    """
    given a sequence of strings return a list of the strings, replacing those
    strings in the input sequence which are keys in the dictionary by their
    dictionary values

    Parameters
    ---------
    sequence : sequence of strings

    alias_dict : Dictionary
        Dictionary of aliases where the keys are strings in the sequence and
        the values are the standard names associated with those strings

    Returns
    -------
    list of strings

    Examples
    --------
    >>> aliases = dict(time=['mjd','expmjd'], flux=['counts'], fluxerr=['flux_err', 'fluxerror']) 
    >>> testSeq = ['mJd', 'band', 'zp', 'Flux', 'fluxError']
    >>> alias_dict = alias_dictionary(testSeq, aliases)
    >>> standardize_sequence(testSeq, alias_dict) == ['time', 'band', 'zp', 'flux', 'fluxerr']
    True

    Notes
    -----

    """
    std = [alias_dict[x] if x in alias_dict else x for x in sequence]
    return std

def standard_aliases():
    """
    A dictionary with keys as standard names and values as permissible aliases
    Parameters
    ----------
    Returns
    -------
    aliases : dict
        Dictionary with keys as standard parameters and values as possible aliases
    """
    key_values = (
        ('tid', ['snid', 'object_id']),
        ('tra', ['ra']),
        ('tdec', ['dec', 'decl']),
        ('mjd', ['expmjd', 'time']),
        ('band', ['bandpass', 'passband', 'filter', 'flt']),
        ('flux', ['counts', 'fluxcal']),
        ('fluxerr', ['flux_err', 'flux_error' ,'fluxerror']),
        ('tclass', ['target']),
        ('mag', ['magpsf']),
        ('magerr', ['magpsferr']),
        ('zp', ['zp', 'zeropoints']),
    )
    return dict(key_values)
