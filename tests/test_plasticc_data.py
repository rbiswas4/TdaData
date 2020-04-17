import os
import tdd
from tdd import read_plasticc_data

def test_plasticc_data():
    example_meta = os.path.join(tdd.example_data,
                                'plasticc_train_meta.csv')
    example_phot = os.path.join(tdd.example_data,
                                'plasticc_train_phot.csv')

    # read in plasticc datasets
    metadata, photometry = read_plasticc_data(example_meta, example_phot)

    assert len(metadata) == 20
    assert len(photometry) == 6697

    assert photometry.tid.unique().size == len(metadata)


