import random

import numpy

def seed_everything(seed: int):
    random.seed(seed)
    numpy.random.seed(seed)
