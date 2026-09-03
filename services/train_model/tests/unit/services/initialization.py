import random

import numpy as np

from services.train_model.src.services.initialization import seed_everything


def test_seed_everything_sets_random_seed():
    seed_everything(42)
    val1 = random.random()
    seed_everything(42)
    val2 = random.random()
    assert val1 == val2


def test_seed_everything_sets_numpy_seed():
    seed_everything(99)
    arr1 = np.random.rand(3)
    seed_everything(99)
    arr2 = np.random.rand(3)
    assert np.allclose(arr1, arr2)


def test_seed_everything_with_zero():
    seed_everything(0)
    val = random.random()
    assert isinstance(val, float)


def test_seed_everything_with_large_seed():
    seed_everything(999_999)
    val = random.random()
    assert isinstance(val, float)
