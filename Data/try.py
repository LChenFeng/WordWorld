import numpy as np
class Map:
    DYN_DTYPE = np.dtype([('id', 'u2'), ('color', '3u1'), ('flags', 'u1')])  # flags[0]：is_entity

    def __init__(self, size):
        self.blocks = np.zeros(size, dtype=self.DYN_DTYPE)
        self.entity = {}

map=Map((3,4))
print(True<<7)
