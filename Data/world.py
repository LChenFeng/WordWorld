import numpy as np
from Data.const import *
from Data.object import *
from perlin_noise import PerlinNoise
import pickle


class Chunk:
    _eq = Block(2758, 0, 0, 0)
    _v_draw = np.vectorize(lambda x, screen, camera, lit: x.draw(screen, camera, lit))
    tree = np.array([
        [np.nan, np.nan, np.nan, 3217, np.nan, np.nan, np.nan],
        [np.nan, 3217, 3217, 3217, 3217, 3217, np.nan],
        [3217, 3217, 3217, 1909, 3217, 3217, 3217],
        [3217, 3217, 3217, 1909, 3217, 3217, 3217],
        [np.nan, np.nan, np.nan, 1909, np.nan, np.nan, np.nan],
        [np.nan, np.nan, np.nan, 1909, np.nan, np.nan, np.nan],
        [np.nan, np.nan, np.nan, 1909, np.nan, np.nan, np.nan]
    ])
    tree = np.rot90(np.flip(tree), k=3)
    k = 240

    def __init__(self, n, type, seed):
        self.n = n
        self.type = type
        self.seed = seed
        self.rng = np.random.default_rng(abs(seed))
        self.blocks = None
        self.indice = None
        self.shine = None

    def load(self, name):
        try:
            ids, self.shine = np.load(f'save/{name}/chunks/{self.n}.npy', allow_pickle=True)
            self.blocks = np.full(chunk_size, None)
            for i, _ in enumerate(ids):
                for j, r in enumerate(_):
                    if not np.isnan(r):
                        self.blocks[i, j] = Block(ids[i, j], self.n, i, j)
            self.indice = np.indices(self.blocks.shape)
        except FileNotFoundError:
            self.blocks = np.full(chunk_size, None, dtype=object)
            self.indice = np.indices(self.blocks.shape)
            self.shine = np.zeros(chunk_size)
            if self.type == 0:
                self.random()
            elif self.type == 1:
                self.flat()
            self.save(name)

    def unload(self, name):
        self.save(name)
        self.blocks = None
        self.indice = None
        self.shine = None

    def save(self, name):
        try:
            ids = np.array([[x.id if x is not None else np.nan for x in row] for row in self.blocks])
            map = np.array([ids, self.shine])
            np.save(f'save/{name}/chunks/{self.n}.npy', map)
        except FileNotFoundError:
            os.makedirs(f'save/{name}/chunks', exist_ok=True)
            self.save(name)

    def destroy(self, i, j, time=True):
        if (block := self.blocks[i, j]) != None:
            if block.hardness >= 0:
                block.count -= 1
                if block.broken() or not time:
                    self.blocks[i, j] = None
                    return block

    def create(self, item, i, j):
        if (block := self.blocks[i, j]) == None:
            self.blocks[i, j] = item.block(self.n, i, j)
        else:
            if block.replaceable:
                self.blocks[i, j] = item.block(self.n, i, j)
                return block.item()

    def _form_block(self, id, i, j):
        self.blocks[i, j] = Block(id, self.n, i, j)

    def form_layer(self, id, i=None, j=None):
        if i is None and j is None:
            i, j = self.indice
        else:
            i = (i, i) if type(i) == int else i
            j = (j, j) if type(j) == int else j
            if i is None:
                i, j = self.indice[..., j[0]:j[1] + 1]
            elif j is None:
                i, j = self.indice[:, i[0]:i[1] + 1]
            else:
                i, j = self.indice[:, i[0]:i[1] + 1, j[0]:j[1] + 1]
        np.vectorize(self._form_block)(id, i, j)

    def form_structure(self, structure, pos):
        x, y = pos
        for i in range(structure.shape[0]):
            for j in range(structure.shape[1]):
                id = structure[i, j]
                if not np.isnan(id):
                    self.blocks[x + i, y + j] = Block(id, self.n, x + i, y + j)

    def form_base(self):
        self.form_layer(1122, None, (chunk_size[1] - 2, chunk_size[1] - 1))
        self.form_layer(1122, None, (0, 1))
        if self.n == edgechunk[0]:
            self.form_layer(1122, (0, 1))
        elif self.n == edgechunk[1]:
            self.form_layer(1122, (chunk_size[0] - 2, chunk_size[0] - 1))

    def form_trees(self):
        hshape = (int(self.tree.shape[0] / 2), self.tree.shape[1])
        for i in range(4, chunk_size[0] - 4, 8):
            if self.rng.integers(0, 2):
                j = self.get_surface([i])[0]
                space = self.blocks[i - hshape[0]:i + hshape[0] + 1, j - hshape[1]:j][~np.isnan(self.tree)]
                if np.all(np.vectorize(lambda x: x.replaceable if x != None else True)(space)):
                    self.form_structure(self.tree, (i - hshape[0], j - hshape[1]))

    def form_mineral(self, id, shape, deep, max_count):
        count = 1 if max_count == 1 else self.rng.integers(1, max_count)
        mu = sum(shape) / 2
        x = self.rng.integers(0, chunk_size[0] - shape[1], size=count).tolist()
        for i in x:
            w = round(self.rng.normal(mu, mu * 0.3))
            while w < shape[0] or w > shape[1]:
                w = round(self.rng.normal(mu, mu * 0.3))
            h = round(self.rng.normal(mu, mu * 0.3))
            while h < shape[0] or h > shape[1]:
                h = round(self.rng.normal(mu, mu * 0.3))
            if type(deep) == int:
                deep = (max(self.get_surface([i + _ for _ in range(w + 1)], 2458)), deep)
            y = self.rng.integers(deep[0], deep[1] - h + 1)
            self.form_structure(np.full((w, h), id), (i, y))

    def form_diggings(self):
        self.form_mineral(1811, (2, 6), 178, 4)  # 煤
        self.form_mineral(1518, (3, 6), 178, 4)  # 蜡
        self.form_mineral(6763, (1, 4), 178, 1)  # 铁矿
        self.form_mineral(6763, (2, 5), (178, chunk_size[1] - 2), 2)  # 铁矿
        self.form_mineral(6764, (1, 3), (178, chunk_size[1] - 2), 2)  # 金矿
        self.form_mineral(6765, (1, 3), chunk_size[1] - 2, 3)  # 钨矿
        self.form_mineral(6766, (1, 3), chunk_size[1] - 2, 3)  # 钛矿
        self.form_mineral(6767, (2, 5), 178, 3)  # 铜矿
        self.form_mineral(1492, (1, 3), (200, chunk_size[1] - 2), 1)  # 钻石
        if self.rng.integers(0, 1):
            self.form_mineral(6768, (1, 3), (228, chunk_size[1] - 2), 1)  # 钚矿
            self.form_mineral(6769, (1, 3), (228, chunk_size[1] - 2), 1)  # 铀矿

    def flat(self):
        self.form_layer(248, None, 127)
        self.form_layer(2758, None, (128, 135))
        self.form_layer(2458, None, (136, 178))
        self.form_layer(3151, None, (179, chunk_size[1] - 3))
        self.form_base()
        self.shine[:, :128] = 255
        bright = 255
        d = 1
        while bright >= 3:
            bright = 255 / d ** 1.3
            self.shine[:, 127 + d] = bright
            d += 1

    def random(self):
        noise1 = PerlinNoise(60, self.seed)
        noise2 = PerlinNoise(60, self.seed - 999901)
        for i in range(chunk_size[0]):
            x = self.n * chunk_size[0] + i
            j = max(min(108 + round(noise1([x / world_size[0]]) * Chunk.k), 128), 60)
            r = max(min(j + 7 + round(noise2([x / world_size[0]]) * Chunk.k), j + 12), j + 2)
            self.form_layer(248, i, j - 1)
            self.form_layer(2758, i, (j, r - 1))
            self.form_layer(2458, i, (r, 178))
            self.shine[i, :j] = 255
            bright = 255
            d = 1
            while bright >= 3:
                bright = 255 / d ** 1.6
                self.shine[i, j + d - 1] = bright
                d += 1
        self.form_layer(3151, None, (179, chunk_size[1] - 3))
        self.form_trees()
        self.form_diggings()
        self.form_base()

    def get_blocks(self, start, end):
        return self.blocks[start[0]:end[0] + 1, start[1]:end[1] + 1]

    def get_surface(self, x, id=2758):
        ground = []
        eq = Block(id, 0, 0, 0)
        for i in x:
            indice = np.where(self.blocks[i] == eq)
            ground.append(indice[0][0])
        return ground

    def get_pos(self):
        return self.indice * [[[1]], [[-1]]] + [[[self.n * chunk_size[0]]], [[edgey[1]]]]

    def add_shine(self, light):
        self.shine += light.lighting(self.get_pos())

    def remove_shine(self, light):
        self.shine -= light.lighting(self.get_pos())

    def shining(self):
        pass

    def draw(self, screen, camera):
        mask = self.blocks != None
        Chunk._v_draw(self.blocks[mask], screen, camera, self.shine[mask])


class World:
    def __init__(self, name, type, seed):
        self.name = name
        self.type = type  # 随机 0, 平坦 1
        self.seed = seed
        self.rng = np.random.default_rng(abs(seed))
        self.chunks = {i: Chunk(i, type, seed) for i in range(edgechunk[0], edgechunk[1] + 1)}
        self.loading = set()

    def update(self, on):
        loading = {i for i in range(max(on - 1, edgechunk[0]), min(on + 2, edgechunk[1] + 1))}
        self.load(loading - self.loading)
        self.unload(self.loading - loading)
        self.loading = loading

    def load(self, n):
        for i in n:
            if edgechunk[0] <= i <= edgechunk[1]:
                self.chunks[i].load(self.name)

    def unload(self, n):
        for i in n:
            if edgechunk[0] <= i <= edgechunk[1]:
                self.chunks[i].unload(self.name)

    def save(self, player):
        for i in self.loading:
            self.chunks[i].save(self.name)
        with open(f'Save/{self.name}/init.json', 'w') as file:
            json.dump({'type': self.type, 'seed': self.seed, 'mode': player.mode}, file)
        with open(f'Save/{self.name}/player.pkl', 'wb') as file:
            pickle.dump(player, file)

    def destroy(self, pos, time=True):
        n, i, j = self.where(pos)
        x, y = pos
        block = self.chunks[n].destroy(i, j, time)
        try:
            block.delete(self)
        except AttributeError:
            pass
        if block != None:
            drop = np.random.choice([None, Items(3719)], p=p)
            ind = block.chain(self.get_blocks((x - 1, y - 1), (x + 1, y + 1)))
            locking = []
            for i in ind:
                n, i, j = self.where((x + i[0], y + i[1]))
                locking.append(self.chunks[n].destroy(i, j, time).item())
            return block.item(), locking, drop
        return None, [], None

    def create(self, item, pos):
        n, i, j = self.where(pos)
        if item.check(self.get_blocks((pos[0] - 1, pos[1] - 1), (pos[0] + 1, pos[1] + 1))):
            return self.chunks[n].create(item, i, j)

    def where(self, pos):
        x = pos[0]
        n = int(x // chunk_size[0])
        if x >= 0:
            i = x % chunk_size[0]
        else:
            i = (x - edgex[0]) % chunk_size[0]
        return n, int(i), int(edgey[1] - pos[1])

    def born_place(self, x):
        n, i, _ = self.where((x, 0))
        self.loading = {n - 1, n, n + 1}
        self.load(self.loading)
        return edgey[1] - self.chunks[n].get_surface([i])[0]

    def get_blocks(self, edge1, edge2):
        n1, i1, j1 = self.where(edge1)
        n2, i2, j2 = self.where(edge2)
        j1, j2 = min(j1, j2), max(j1, j2)
        if n1 == n2:
            i1, i2 = min(i1, i2), max(i1, i2)
            return self.chunks[n1].get_blocks((i1, j1), (i2, j2))
        elif n1 > n2:
            n1, n2 = n2, n1
            i1, i2 = i2, i1
        c1 = self.chunks[n1].get_blocks((i1, j1), (chunk_size[0] - 1, j2))
        c2 = self.chunks[n2].get_blocks((0, j1), (i2, j2))
        return np.vstack((c1, c2))

    def add_light(self, light):
        for n in self.loading:
            self.chunks[n].add_shine(light)

    def remove_light(self, light):
        for n in self.loading:
            self.chunks[n].remove_shine(light)

    def draw(self, screen, player):
        for n in self.loading:
            self.chunks[n].draw(screen, player.camera)
