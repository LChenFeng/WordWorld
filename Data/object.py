from Data.const import *
import json
import os

with open(block_path[0], 'r', encoding='utf-8') as file:
    CHAR = json.load(file)
with open(block_path[1], 'r', encoding='utf-8') as file:
    SYMBOL = json.load(file)
ID1 = [int(i) for i in CHAR.keys()]
ID2 = [int(i) for i in SYMBOL.keys()]
CHAR.update(SYMBOL)

real_rec = os.listdir(real_path)
RECIPES = []
for i in real_rec:
    with open(os.path.join(real_path, i), 'r') as file:
        RECIPES.append(json.load(file))


class Block:
    SPEACIAL = {}
    grid_size = 3
    cell_size = size // grid_size

    def __new__(cls, *args):
        if len(args) != 0:
            id = args[0]
            if id in Block.SPEACIAL:
                return super().__new__(Block.SPEACIAL[id])
        return super().__new__(cls)

    def __init__(self, id, n, i, j):
        self.pos = (n * chunk_size[0] + i, edgey[1] - j)
        self.id = int(id)
        data = CHAR[str(self.id)]
        self.name = data['name']
        self.color = data['color'] if 'color' in data else color
        self.hardness = data['hardness'] if 'hardness' in data else 0
        self.penetrable = data['penetrable'] if 'penetrable' in data else True
        self.replaceable = data['replaceable'] if 'replaceable' in data else False
        self.climbable = data['climbable'] if 'climbable' in data else False
        self.count = self.ini = round(self.hardness * (fps / 12))
        self.surface = font.render(self.name, True, self.color)
        self.mk = np.arange(self.grid_size ** 2)
        np.random.shuffle(self.mk)

    def __eq__(self, other):
        if isinstance(other, Block):
            if self.id == other.id:
                return True
        return False

    def broken(self):
        return self.count <= 0

    def item(self):
        return Items(self.id)

    def chain(self, round):
        return []

    def draw(self, screen, camera, alpha):
        sx, sy = camera.world_to_screen(self.pos)
        if -size <= sx <= WIDTH and -size <= sy <= HEIGHT and alpha != 0:
            self.surface.set_alpha(alpha)
            screen.blit(self.surface, (sx, sy))
            if self.count < self.ini:
                eliminated = round(np.ceil(self.grid_size ** 2 * (1 - self.count / self.ini)))
                for idx in self.mk[:eliminated]:
                    x = sx + (idx % self.grid_size) * self.cell_size
                    y = sy + (idx // self.grid_size) * self.cell_size
                    pg.draw.rect(screen, backcolor, (x, y, self.cell_size, self.cell_size))


class Soil(Block):
    _eq = Block(248, 0, 0, 0)

    def chain(self, round):
        if round[1, 0] == Soil._eq:
            return [(0, 1)]
        else:
            return []


class Table(Block):
    def __init__(self, *args):
        super().__init__(*args)
        self.syner = Synthesizer((WIDTH / 2 - per, 330 / scale), 3)

    def use(self, player, world):
        self.syner.opening = True
        player.knap.opening = True
        return self

    def close(self, player):
        self.syner.opening = False
        self.syner.close(player.knap)

    def in_edge(self, pos):
        return self.syner.in_edge(pos)

    def click(self, pos, on, mode):
        return self.syner.click(pos, on, mode)

    def match(self):
        self.syner.match()

    def draw_ui(self, screen):
        self.syner.draw(screen)


class Desk(Block):
    def __init__(self, *args):
        super().__init__(*args)
        self.syner = Synthesizer((WIDTH / 2 - per * 2, 245 / scale), 4)

    def use(self, player, world):
        self.syner.opening = True
        player.knap.opening = True
        return self

    def close(self, player):
        self.syner.opening = False
        self.syner.close(player.knap)

    def in_edge(self, pos):
        return self.syner.in_edge(pos)

    def click(self, pos, on, mode):
        return self.syner.click(pos, on, mode)

    def match(self):
        self.syner.match()

    def draw_ui(self, screen):
        self.syner.draw(screen)


class Word(Block):
    def item(self):
        return Items(np.random.choice(ID1))


class Symbol(Block):
    def item(self):
        return Items(np.random.choice(ID2))


class Lamp(Block):
    def __init__(self, *args):
        super().__init__(*args)
        self.light = Light(500, self.pos)
        self.colors = [self.color, [252, 252, 141]]
        self.opening = False

    def use(self, player, world):
        if self.opening:
            self.opening = False
            world.remove_light(self.light)
            self.color = self.colors[0]
        else:
            self.opening = True
            world.add_light(self.light)
            self.color = self.colors[1]

    def delete(self, world):
        if self.opening:
            world.remove_light(self.light)


class Candle(Block):
    def __init__(self, *args):
        super().__init__(*args)
        self.light = Light(300, self.pos)
        self.colors = [self.color, [255, 255, 224]]
        self.opening = False

    def use(self, player, world):
        if self.opening:
            self.opening = False
            world.remove_light(self.light)
            self.color = self.colors[0]
        else:
            self.opening = True
            world.add_light(self.light)
            self.color = self.colors[1]

    def delete(self, world):
        if self.opening:
            world.remove_light(self.light)


Block.SPEACIAL = {
    2758: Soil,
    2639: Table,
    3697: Desk,
    3719: Word,
    748: Symbol,
    507: Lamp,
    3653: Candle
}


class Items:
    SPEACIAL = {}
    per2 = int(per * 0.3)
    sp = 8 * scale
    font_i = pg.font.Font(font_path, int(per / 1.5))
    font_n = pg.font.Font(font_path, per2)

    def __new__(cls, *args):
        if len(args) != 0:
            id = args[0]
            if id in Items.SPEACIAL:
                return super().__new__(Items.SPEACIAL[id])
        return super().__new__(cls)

    def __init__(self, id, count=1):
        self.id = int(id)
        data = CHAR[str(self.id)]
        self.name = data['name']
        self.color = data['color'] if 'color' in data else color
        self.placeable = data['placeable'] if 'placeable' in data else True
        self.attack = data['attack'] if 'attack' in data else 1
        self.max_count = 64 if (data['stackable'] if 'stackable' in data else True) else 1
        self.count = min(count, self.max_count) if count > 0 else 1

    def __eq__(self, other):
        if isinstance(other, Items):
            if self.id == other.id:
                return True
        elif self.count <= 0 and other == None:
            return True
        return False

    def block(self, n, i, j):
        if self.placeable:
            self.count -= 1
            return Block(self.id, n, i, j)

    def check(self, round):
        locking = (round[0, 1] or round[2, 1] or round[1, 0] or round[1, 2]) != None
        return locking and self.placeable

    def clear(self):
        if self.count > 0:
            return self

    def full(self):
        return self.count >= self.max_count

    def get_quantity(self, rest=False):
        return self.max_count - self.count if rest else self.count

    def add(self, other):
        if self.id == other.id and not self.full():
            amount = min(self.max_count - self.count, other.count)
            self.count += amount
            other.count -= amount
            return self.clear(), other.clear()
        return other.clear(), self.clear()

    def apart(self, mode):
        if mode == 'one':
            amount = 1
        elif mode == 'half':
            amount = int(self.count / 2 + 0.5)
        elif mode == 'all':
            amount = self.count
        self.count -= amount
        return Items(self.id, amount)

    def draw(self, screen, x, y):
        draw_word(screen, self.name, self.color, (x + self.sp, y + self.sp), self.font_i)
        if self.count > 1:
            t = self.font_n.render(str(self.count), True, color)
            screen.blit(t, (x + per - t.get_width(), y + per - t.get_height()))


class Grass(Items):
    _eqs = [Block(2758, 0, 0, 0)]

    def check(self, round):
        return round[1, 2] in Grass._eqs and self.placeable


Items.SPEACIAL = {
    248: Grass
}


class Synthesizer:
    line_w = round(2 * scale)
    rh = per / 3
    sp = 15

    def __init__(self, pos, shape):
        self.x, self.y = pos
        self.size = shape
        self.width = per * shape
        self.rx = self.x + self.width + self.sp + per * 0.8
        self.ry = self.y + self.width / 2 - self.rh * 1.6
        self.cases = np.full((shape, shape), None, dtype=object)
        self.result = None
        self.opening = False

    def open(self):
        self.opening = True

    def close(self, knap):
        self.opening = False
        self.result = None
        for i in self.cases:
            for items in i:
                knap.add(items)
        self.cases = np.full((self.size, self.size), None, dtype=object)

    def in_edge(self, pos):
        x, y = pos
        return ((0 <= x - self.x <= self.width and 0 <= y - self.y <= self.width) or (
                0 <= x - self.rx <= per and 0 <= y - self.ry <= per)) and self.opening

    def click(self, pos, on, mode='all'):
        x, y = pos
        if 0 <= x - self.x <= self.width and 0 <= y - self.y <= self.width:
            x, y = int((y - self.y) // per), int((x - self.x) // per)
            try:
                items = self.cases[x, y]
            except KeyError:
                return
            if on == None:
                if items != None:
                    on = items.apart(mode)
            else:
                if items == None:
                    self.cases[x, y] = on.apart(mode)
                else:
                    self.cases[x, y], on = items.add(on.apart('all'))
        elif 0 <= x - self.rx <= per and 0 <= y - self.ry <= per:
            if self.result != None:
                if on == None:
                    self.syn()
                    return self.result
                elif on == self.result:
                    self.syn()
                    on.add(self.result)
        return on

    def match(self):
        ids = np.array([[x.id if x is not None else np.nan for x in row] for row in self.cases], dtype=np.float64)
        if not np.all(np.isnan(ids)):
            for rec in RECIPES:
                if rec['type'] == 'shaped':
                    arr = np.array(rec['pattern'], dtype=np.float64)
                    arr = np.where(arr == None, np.nan, arr)
                    for i in range(ids.shape[0] - arr.shape[0] + 1):
                        for j in range(ids.shape[1] - arr.shape[1] + 1):
                            if np.array_equal(ids[i:i + arr.shape[0], j:j + arr.shape[1]], arr, equal_nan=True):
                                idc = ids.copy()
                                idc[i:i + arr.shape[0], j:j + arr.shape[1]] = np.nan
                                if np.all(np.isnan(idc)):
                                    result = rec['result']
                                    self.result = Items(result['id'], result['count'] if 'count' in result else 1)
                                    return
                elif rec['type'] == 'shapeless':
                    if np.array_equal(ids[~np.isnan(ids)], rec['ingredients']):
                        result = rec['result']
                        self.result = Items(result['id'], result['count'] if 'count' in result else 1)
                        return
        self.result = None

    def syn(self):
        for i in self.cases:
            for j in i:
                j.apart('one') if j != None else None
        self.cases = np.where(self.cases == None, None, self.cases)

    def draw(self, screen):
        if self.opening:
            pg.draw.rect(screen, backcolor, (self.x, self.y, self.width, self.width))
            for i in range(self.size):
                x0 = self.x + per * i
                for j in range(self.size):
                    pg.draw.rect(screen, knapcolor, (x0, self.y + per * j, per, per), self.line_w)
                    if (items := self.cases[j, i]) != None:
                        items.draw(screen, x0, self.y + per * j)
            draw_word(screen, "==", backcolor, (self.rx - per * 0.8, self.ry + self.rh * 0.6))
            pg.draw.rect(screen, backcolor, (self.rx, self.ry, per, per))
            pg.draw.rect(screen, knapcolor, (self.rx, self.ry, per, per), self.line_w)
            self.result.draw(screen, self.rx, self.ry) if self.result != None else None


class Writeboard(Block):
    def __init__(self, *args):
        super().__init__(*args)

    def draw_ui(self):
        pass


class Light:
    def __init__(self, bright, pos):
        self.x, self.y = pos
        self.bright = bright
        self._v_light = np.vectorize(self.light_pos)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def light_pos(self, x, y):
        d2 = (x - self.x) ** 2 + (y - self.y) ** 2
        if d2 == 0:
            return 255
        else:
            bright = self.bright / d2
            return bright if bright >= 2 else 0

    def lighting(self, pos):
        return self._v_light(*pos)

    def set_bright(self, bright):
        self.bright = bright
