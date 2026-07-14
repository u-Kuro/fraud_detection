import random

import numpy as np

def seed_everything(seed: int):
    random.seed(seed)
    np.random.seed(seed)
