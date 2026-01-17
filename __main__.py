from perlin_noise import PerlinNoise
from Data.UI import *
from Data.player import *
from Data.world import *

os.environ['SDL_IME_SHOW_UI'] = '1'
pg.display.set_caption('文字世界')
screen = pg.display.set_mode((WIDTH, HEIGHT), pg.FULLSCREEN | pg.HWSURFACE | pg.DOUBLEBUF | pg.SWSURFACE)
pg.key.stop_text_input()
pg.mixer.music.set_volume(0.5)
pg.mixer.music.play(loops=-1, fade_ms=2000)


class WorldGenerate:
    DYN_DTYPE = np.dtype([('id', 'u2'), ('color', '3u1'), ('flags', 'u1')])  # flags 0:is_block_entity, 1:penetrable

    def __init__(self, name, type, seed, mode):
        self.name = name
        self.type = type  # 随机 0, 平坦 1
        self.seed = seed
        self.mode = mode
        self.rng = np.random.default_rng(seed)
        self.generate()
        self.born()
        self.save()

    def generate(self):
        self.map = np.zeros(world_size, dtype=self.DYN_DTYPE)
        if self.type:
            self.flat()
        else:
            self.unflat()

    def flat(self):
        pass

    def unflat(self):
        pass

    def born(self):
        middle = int(world_size[0] / 2)
        px = chunk_size[0] * int((edgechunk[1] - edgechunk[0]) / 6)
        j = self.rng.integers(middle - px, middle + px)
        i = self.map.get_spec_pos(j, lambda b: not CHAR[b]['penetrable'])
        self.player = Player(self.map.index_to_coord((100, j)), self.mode)
        self.player.knap.add(Items(507, 64))
        self.player.knap.add(Items(3653, 64))
        self.player.knap.add(Items(1518, 64))
        self.player.knap.add(Items(3697, 64))

    def save(self):
        os.mkdir(os.path.join(save_path, self.name))
        os.mkdir(os.path.join(save_path, f'{self.name}/chunks'))
        with open(os.path.join(save_path, f'{self.name}/init.json'), 'w+') as file:
            json.dump({'type': self.type, 'seed': self.seed, 'mode': self.mode}, file)
        with open(os.path.join(save_path, f'{self.name}/player.pkl'), 'wb+') as file:
            pickle.dump(self.player, file)
        with open(os.path.join(save_path, f'{self.name}/entities.pkl'), 'wb+') as file:
            pickle.dump({}, file)
        for i in range(edgechunk[0], edgechunk[1] + 1):
            x = chunk_size[0] * (i - edgechunk[0])
            np.save(os.path.join(save_path, f'{self.name}/chunks/{i}.npy'), self.map.blocks[x:x + chunk_size[0]])



def dead(player):
    ui = Dead()
    running = True
    while running:
        for event in pg.event.get():
            match event.type:
                case pg.QUIT:
                    running = False
                case pg.KEYDOWN:
                    match event.key:
                        case pg.K_RIGHT | pg.K_d:
                            ui.move_indice(1)
                        case pg.K_LEFT | pg.K_a:
                            ui.move_indice(-1)
                        case pg.K_SPACE | pg.K_RETURN:
                            player.hp.reset()
                            player.knap.add(Items(2569), (9, 2))
                            return not ui.indice
                case pg.MOUSEBUTTONDOWN:
                    match event.button:
                        case 4:
                            ui.move_indice(-1)
                        case 5:
                            ui.move_indice(1)
        screen.fill(backcolor)
        ui.draw(screen)
        pg.display.flip()


def play(name):
    clock = pg.time.Clock()
    with open(os.path.join(save_path, f'{name}/player.pkl'), 'rb') as file:
        player = pickle.load(file)
    world = World(name, player.on)
    running = True
    while running:
        for event in pg.event.get():
            match event.type:
                case pg.QUIT:
                    running = False
                case pg.KEYDOWN:
                    match event.key:
                        case pg.K_ESCAPE:
                            running = False
                        case pg.K_a:
                            player.move(-1)
                        case pg.K_d:
                            player.move(1)
                        case pg.K_w:
                            player.fly(1)
                        case pg.K_s:
                            player.fly(-1)
                        case pg.K_SPACE:
                            player.jump()
                        case pg.K_e:
                            player.open()
                        case key if 48 <= key <= 57:  # 0~9
                            player.knap.set_indice(key - 48)
                case pg.KEYUP:
                    match event.key:
                        case pg.K_a:
                            player.stop(-1)
                        case pg.K_d:
                            player.stop(1)
                        case pg.K_w:
                            player.stop_fly(1)
                        case pg.K_s:
                            player.stop_fly(-1)
                case pg.MOUSEBUTTONDOWN:
                    match event.button:
                        case 1:  # 左键
                            if player.knap.opening:
                                player.click(event.pos, 1)
                            else:
                                player.state = 1
                                player.excavate(world, event.pos)
                        case 3:  # 右键
                            if player.knap.opening:
                                player.click(event.pos, 3)
                            else:
                                player.state = 2
                                player.interact(world, event.pos)
                        case 4:  # 滚轮向上
                            player.knap.move_indice(-1)
                        case 5:  # 滚轮向下
                            player.knap.move_indice(1)
                case pg.MOUSEBUTTONUP:
                    player.state = 0
                    player.count = 0
        if player.hp.dead():
            player.reset()
            running = dead(player)
        screen.fill(backcolor)
        world.update(player.on)
        world.draw(screen, player.get_scrpoint())
        player.update(world)
        player.draw(screen)
        pg.display.flip()
        clock.tick(fps)
    player.reset()
    world.save(player)


def create():
    ui = Create()
    running = True
    while running:
        for event in pg.event.get():
            match event.type:
                case pg.QUIT:
                    running = False
                case pg.KEYDOWN:
                    match event.key:
                        case pg.K_ESCAPE:
                            running = False
                        case pg.K_RIGHT | pg.K_d:
                            ui.move_indice(1)
                        case pg.K_LEFT | pg.K_a:
                            ui.move_indice(-1)
                        case pg.K_BACKSPACE:
                            ui.remove()
                        case pg.K_SPACE | pg.K_RETURN:
                            if ui.indice == 0:
                                name, seed, type, mode = ui.world_data()
                                if name == '':
                                    continue
                                else:
                                    pg.key.stop_text_input()
                                    WorldGenerate(name, type, seed, mode)
                                    play(name)
                            running = False
                case pg.MOUSEBUTTONDOWN:
                    match event.button:
                        case 1 | 3:
                            ui.click(event.pos)
                        case 4:
                            ui.move_indice(-1)
                        case 5:
                            ui.move_indice(1)
                case pg.TEXTINPUT:
                    ui.input(event.text)
        screen.fill(backcolor)
        ui.draw(screen)
        pg.display.flip()


def worlds():
    ui = Worlds()
    running = True
    while running:
        for event in pg.event.get():
            match event.type:
                case pg.QUIT:
                    running = False
                case pg.KEYDOWN:
                    match event.key:
                        case pg.K_ESCAPE:
                            running = False
                        case pg.K_RIGHT | pg.K_d:
                            ui.move_indice(1)
                        case pg.K_LEFT | pg.K_a:
                            ui.move_indice(-1)
                        case pg.K_SPACE | pg.K_RETURN:
                            match ui.indice:
                                case 0:
                                    if ui.world != None:
                                        play(ui.get_name())
                                        running = False
                                case 1:
                                    ui.delete()
                                case 2:
                                    create()
                                    running = False
                                case _:
                                    running = False
                case pg.MOUSEBUTTONDOWN:
                    match event.button:
                        case 1 | 3:
                            ui.click(event.pos)
                        case 4:
                            ui.move_indice(-1)
                        case 5:
                            ui.move_indice(1)
        screen.fill(backcolor)
        ui.draw(screen)
        pg.display.flip()


def main():
    ui = Home()
    running = True
    while running:
        for event in pg.event.get():
            match event.type:
                case pg.QUIT:
                    running = False
                case pg.KEYDOWN:
                    match event.key:
                        case pg.K_UP | pg.K_w:
                            ui.move_indice(-1)
                        case pg.K_DOWN | pg.K_s:
                            ui.move_indice(1)
                        case pg.K_SPACE | pg.K_RETURN:
                            if ui.indice == 0:
                                worlds()
                            elif ui.indice == 1:
                                pass
                            else:
                                running = False
                case pg.MOUSEBUTTONDOWN:
                    match event.button:
                        case 4:
                            ui.move_indice(-1)
                        case 5:
                            ui.move_indice(1)
        screen.fill(backcolor)
        ui.draw(screen)
        pg.display.flip()
    pg.quit()


if __name__ == '__main__':
    main()
