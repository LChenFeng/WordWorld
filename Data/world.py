import numpy as np
import pickle
import os
from Data.const import *
from Data.object import *

real_rec = os.listdir(real_path)
RECIPES = []
for i in real_rec:
    with open(os.path.join(real_path, i), 'r') as file:
        RECIPES.append(json.load(file))

DYN_DTYPE = np.dtype([('id', 'u2'), ('color', '3u1'), ('flags', 'u1')])  # flags 0:is_block_entity, 1:penetrable

BORN = {
}
UPDATE = {
}
BROKEN = {
}


# class Map:
#     def __init__(self, name, n):
#         self.name = name
#         if isinstance(n, int):
#             self.n = n
#             self.load()
#         elif isinstance(n, np.ndarray):
#             self.n = 0
#             self.blocks = n
#             self.entitiy = {}
#         else:
#             raise
#         self.durability = 0
#
#     def load(self):
#         self.blocks = np.load(os.path.join(save_path, f'{self.name}/chunks/{self.n}.npy'))
#         with open(os.path.join(save_path, f'{self.name}/chunks/{self.n}.pkl'), 'rb') as file:
#             self.entitiy = pickle.load(file)
#
#     def unload(self):
#         np.save(os.path.join(save_path, f'{self.name}/chunks/{self.n}.npy'), self.blocks)
#         with open(os.path.join(save_path, f'{self.name}/chunks/{self.n}.pkl'), 'wb') as file:
#             pickle.dump(self.entity, file)
#
#     def get_char(self, i, j, attri):
#         return CHAR[self.blocks_id[i, j]][attri]
#
#     def get_spec_pos(self, j, cond_func, n=1, reverse=False):
#         mask = np.array([cond_func(block) for block in self.blocks_id[j]])
#         indices = np.where(mask)[0]
#         if len(indices) >= n:
#             return indices[-n] if reverse else indices[n - 1]
#
#     @property
#     def blocks_id(self):
#         return self.blocks['id']
#
#     @property
#     def blocks_index(self):
#         return np.array(self.index_to_coord(np.indices(self.blocks.shape))).transpose(1, 2, 0)
#
#     def get_scr_pos(self, pos):
#         distance = (self.blocks_index - np.array([pos]).reshape(1, 1, 2)) * size
#         distance[1] = -distance[1]
#         return distance
#
#     def index_to_coord(self, index):
#         x = self.n * chunk_size[0] + index[1]
#         y = edgey[1] - index[0]
#         return x, y
#
#     def place(self, i_range, j_range, id):
#         region = self.blocks[i_range[0]:i_range[1], j_range[0]:j_range[1]]
#         origin = region.copy()
#         mask = CHAR[region['id']]['replaceable']
#         region[mask] = (id, CHAR[id]['color'], (id in BLOCK_ENTITY << 7) | (CHAR[id]['penetrable'] << 6))
#         indice = np.argwhere(mask)
#         if id in PLACE:
#             for i, j in indice:
#                 BORN[id](self, i + i_range[0], j + j_range[0])
#         return origin['id']
#
#     def destory(self, i_range, j_range):
#         region = self.blocks[i_range[0]:i_range[1], j_range[0]:j_range[1]]
#         origin = region.copy()
#         for i, j in np.moveaxis(np.indices(region.shape), 0, -1):
#             if (id := region[i, j]['id']) in DESTROY:
#                 BROKEN[id](self, i + i_range[0], j + j_range[0])
#         region[:, :] = (0, (0, 0, 0), 0)
#         return origin['id']
#
#     def draw(self, screen, scr_point):
#         a = self.get_scr_pos(scr_point)
#         for i, j in np.argwhere(
#                 (self.blocks_id > 0) & (a[:, :, 0] >= -size) & (a[:, :, 1] >= -size) & (a[:, :, 0] <= WIDTH) & (a[:, :, 1] <= HEIGHT)):
#             draw_word(screen, self.get_char(i, j, 'name'), self.blocks[i, j]['color'], a[:, i, j])


# class Chunk:
#     _eq = Block(2759, 0, 0, 0)
#     _v_draw = np.vectorize(lambda x, screen, camera, lit: x.draw(screen, camera, lit))
#     tree = np.array([
#         [np.nan, np.nan, np.nan, 3218, np.nan, np.nan, np.nan],
#         [np.nan, 3218, 3218, 3218, 3218, 3218, np.nan],
#         [3218, 3218, 3218, 1910, 3218, 3218, 3218],
#         [3218, 3218, 3218, 1910, 3218, 3218, 3218],
#         [np.nan, np.nan, np.nan, 1910, np.nan, np.nan, np.nan],
#         [np.nan, np.nan, np.nan, 1910, np.nan, np.nan, np.nan],
#         [np.nan, np.nan, np.nan, 1910, np.nan, np.nan, np.nan]
#     ])
#     tree = np.rot90(np.flip(tree), k=3)
#     k = 240
#
#     def __init__(self, n, type, seed):
#         self.n = n
#         self.type = type
#         self.seed = seed
#         self.rng = np.random.default_rng(abs(seed))
#         self.map = Map(chunk_size)
#
#     def load(self, name):
#         try:
#             ids = np.load(f'save/{name}/chunks/{self.n}.npy', allow_pickle=True)
#             self.blocks = np.full(chunk_size, None)
#             for i, _ in enumerate(ids):
#                 for j, r in enumerate(_):
#                     if not np.isnan(r):
#                         self.blocks[i, j] = Block(ids[i, j], self.n, i, j)
#             self.indice = np.indices(self.blocks.shape)
#         except FileNotFoundError:
#             self.blocks = np.full(chunk_size, None, dtype=object)
#             self.indice = np.indices(self.blocks.shape)
#             if self.type == 0:
#                 self.random()
#             elif self.type == 1:
#                 self.flat()
#             self.save(name)
#
#     def unload(self, name):
#         self.save(name)
#         self.blocks = None
#         self.indice = None
#
#     def save(self, name):
#         try:
#             np.save(f'save/{name}/chunks/{self.n}.npy', map)
#         except FileNotFoundError:
#             os.makedirs(f'save/{name}/chunks', exist_ok=True)
#             self.save(name)
#
#     def destroy(self, i, j, time=True):
#         if (block := self.blocks[i, j]) != None:
#             if block.hardness >= 0:
#                 block.count -= 1
#                 if block.broken() or not time:
#                     self.blocks[i, j] = None
#                     return block
#
#     def create(self, item, i, j):
#         if (block := self.blocks[i, j]) == None:
#             self.blocks[i, j] = item.block(self.n, i, j)
#         else:
#             if block.replaceable:
#                 self.blocks[i, j] = item.block(self.n, i, j)
#                 return block.item()
#
#     def _form_block(self, id, i, j):
#         self.blocks[i, j] = Block(id, self.n, i, j)
#
#     def form_layer(self, id, i=None, j=None):
#         if i is None and j is None:
#             i, j = self.indice
#         else:
#             i = (i, i) if type(i) == int else i
#             j = (j, j) if type(j) == int else j
#             if i is None:
#                 i, j = self.indice[..., j[0]:j[1] + 1]
#             elif j is None:
#                 i, j = self.indice[:, i[0]:i[1] + 1]
#             else:
#                 i, j = self.indice[:, i[0]:i[1] + 1, j[0]:j[1] + 1]
#         np.vectorize(self._form_block)(id, i, j)
#
#     def form_structure(self, structure, pos):
#         x, y = pos
#         for i in range(structure.shape[0]):
#             for j in range(structure.shape[1]):
#                 id = structure[i, j]
#                 if not np.isnan(id):
#                     self.blocks[x + i, y + j] = Block(id, self.n, x + i, y + j)
#
#     def form_base(self):
#         self.form_layer(1123, None, (chunk_size[1] - 2, chunk_size[1] - 1))
#         self.form_layer(1123, None, (0, 1))
#         if self.n == edgechunk[0]:
#             self.form_layer(1123, (0, 1))
#         elif self.n == edgechunk[1]:
#             self.form_layer(1123, (chunk_size[0] - 2, chunk_size[0] - 1))
#
#     def form_trees(self):
#         hshape = (int(self.tree.shape[0] / 2), self.tree.shape[1])
#         for i in range(4, chunk_size[0] - 4, 8):
#             if self.rng.integers(0, 2):
#                 j = self.get_surface([i])[0]
#                 space = self.blocks[i - hshape[0]:i + hshape[0] + 1, j - hshape[1]:j][~np.isnan(self.tree)]
#                 if np.all(np.vectorize(lambda x: x.replaceable if x != None else True)(space)):
#                     self.form_structure(self.tree, (i - hshape[0], j - hshape[1]))
#
#     def form_mineral(self, id, shape, deep, max_count):
#         count = 1 if max_count == 1 else self.rng.integers(1, max_count)
#         mu = sum(shape) / 2
#         x = self.rng.integers(0, chunk_size[0] - shape[1], size=count).tolist()
#         for i in x:
#             w = round(self.rng.normal(mu, mu * 0.3))
#             while w < shape[0] or w > shape[1]:
#                 w = round(self.rng.normal(mu, mu * 0.3))
#             h = round(self.rng.normal(mu, mu * 0.3))
#             while h < shape[0] or h > shape[1]:
#                 h = round(self.rng.normal(mu, mu * 0.3))
#             if type(deep) == int:
#                 deep = (max(self.get_surface([i + _ for _ in range(w + 1)], 2459)), deep)
#             y = self.rng.integers(deep[0], deep[1] - h + 1)
#             self.form_structure(np.full((w, h), id), (i, y))
#
#     def form_diggings(self):
#         self.form_mineral(1812, (2, 6), 178, 4)  # 煤
#         self.form_mineral(1519, (3, 6), 178, 4)  # 蜡
#         self.form_mineral(6764, (1, 4), 178, 1)  # 铁矿
#         self.form_mineral(6765, (2, 5), (178, chunk_size[1] - 2), 2)  # 铁矿
#         self.form_mineral(6765, (1, 3), (178, chunk_size[1] - 2), 2)  # 金矿
#         self.form_mineral(6766, (1, 3), chunk_size[1] - 2, 3)  # 钨矿
#         self.form_mineral(6767, (1, 3), chunk_size[1] - 2, 3)  # 钛矿
#         self.form_mineral(6768, (2, 5), 178, 3)  # 铜矿
#         self.form_mineral(1493, (1, 3), (200, chunk_size[1] - 2), 1)  # 钻石
#         if self.rng.integers(0, 1):
#             self.form_mineral(6769, (1, 3), (228, chunk_size[1] - 2), 1)  # 钚矿
#             self.form_mineral(6770, (1, 3), (228, chunk_size[1] - 2), 1)  # 铀矿
#
#     def flat(self):
#         self.form_layer(249, None, 127)
#         self.form_layer(2759, None, (128, 135))
#         self.form_layer(2459, None, (136, 178))
#         self.form_layer(3152, None, (179, chunk_size[1] - 3))
#         self.form_base()
#
#     def random(self):
#         noise1 = PerlinNoise(60, self.seed)
#         noise2 = PerlinNoise(60, self.seed - 999901)
#         for i in range(chunk_size[0]):
#             x = self.n * chunk_size[0] + i
#             j = max(min(108 + round(noise1([x / world_size[0]]) * Chunk.k), 128), 60)
#             r = max(min(j + 7 + round(noise2([x / world_size[0]]) * Chunk.k), j + 12), j + 2)
#             self.form_layer(249, i, j - 1)
#             self.form_layer(2759, i, (j, r - 1))
#             self.form_layer(2459, i, (r, 178))
#         self.form_layer(3152, None, (179, chunk_size[1] - 3))
#         self.form_trees()
#         self.form_diggings()
#         self.form_base()
#
#     def get_blocks(self, start, end):
#         return self.blocks[start[0]:end[0] + 1, start[1]:end[1] + 1]
#
#     def get_surface(self, x, id=2759):
#         ground = []
#         eq = Block(id, 0, 0, 0)
#         for i in x:
#             indice = np.where(self.blocks[i] == eq)
#             ground.append(indice[0][0])
#         return ground


class World:
    def __init__(self, name, on):
        self.name = name
        self.on = on
        with open(os.path.join(save_path, f'{self.name}/entities.pkl'), 'rb') as file:
            self.entities = pickle.load(file)
        self.map = np.hstack((self.load_chunk(i) for i in
                              range(max(on - dp_chunks, edgechunk[0]), min(on + dp_chunks, edgechunk[1]) + 1)))

    def load_chunk(self, n):
        return np.load(os.path.join(save_path, f'{self.name}/chunks/{self.n}.npy'))

    def unload_chunk(self, map):
        np.save(os.path.join(save_path, f'{self.name}/chunks/{self.n}.npy'), map)

    def update(self, new_on):
        pass

    @staticmethod
    def coord_to_index(pos):
        x = pos[0]
        n = int(x // chunk_size[0])
        if x >= 0:
            j = x % chunk_size[0]
        else:
            j = (x - edgex[0]) % chunk_size[0]
        return n, int(edgey[1] - pos[1]), int(j)

    @staticmethod
    def index_to_coord(n, i, j):
        x = n * chunk_size[0] + j
        y = edgey[1] - i
        return x, y

    def get_ids(self, pos1, pos2):
        if edgex[0] <= pos1[0] <= pos2[0] <= edgex[1] and edgey[0] <= pos1[1] <= pos2[1] <= edgey[1]:
            n1, i1, j1 = World.coord_to_index(pos1)
            n2, i2, j2 = World.coord_to_index(pos2)
            if n1 in self.maps and n2 in self.maps:
                if n1 == n2:
                    return self.maps[n1].blocks_id[i1:i2, j1:j2]
                else:
                    r1 = self.maps[n1].blocks_id[i1:i2, j1:]
                    r2 = self.maps[n2].blocks_id[i1:i2, :j2]
                    return np.concatenate([r1, r2], axis=1)
        return np.zeros((pos2[0] - pos1[0], pos2[1] - pos1[1]))

    def destroy(self, pos, handing=None):
        if edgex[0] <= pos[0] <= edgex[1] and edgey[0] <= pos[1] <= edgey[1]:
            n, i, j = World.coord_to_index(pos)
            return self.maps[n].destroy((i, i + 1), (j, j + 1))

    def place(self, pos, id):
        if edgex[0] <= pos[0] <= edgex[1] and edgey[0] <= pos[1] <= edgey[1]:
            n, i, j = World.coord_to_index(pos)
            return self.maps[n].place((i, i + 1), (j, j + 1), id)
        else:
            return np.array([item])

    def draw(self, screen, start):
        for map in self.maps.values():
            map.draw(screen, start)
