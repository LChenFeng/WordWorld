from Data.UI import *
from Data.player import *
from Data.world import *

os.environ['SDL_IME_SHOW_UI'] = '1'
pg.display.set_caption('文字世界')
screen = pg.display.set_mode((WIDTH, HEIGHT), pg.FULLSCREEN | pg.HWSURFACE | pg.DOUBLEBUF | pg.SWSURFACE)
pg.key.stop_text_input()


def load_player(world, mode):
    try:
        with open(os.path.join(save_path, world.name, 'player.pkl'), 'rb') as file:
            player = pickle.load(file)
    except FileNotFoundError:
        rng = np.random.default_rng(abs(world.seed))
        x = rng.integers(-20, 21) * chunk_size[0] + rng.integers(0, chunk_size[0])
        player = Player((x, world.born_place(x)), mode)
        player.knap.add(Items(507, 64))
        player.knap.add(Items(3653, 64))
        player.knap.add(Items(1518, 64))
        player.knap.add(Items(3697, 64))
        world.save(player)
    return player


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
                            return True if ui.indice == 0 else False
                case pg.MOUSEBUTTONDOWN:
                    match event.button:
                        case 4:
                            ui.move_indice(-1)
                        case 5:
                            ui.move_indice(1)
        screen.fill(backcolor)
        ui.draw(screen)
        pg.display.flip()


def play(name, mode, type, seed):
    clock = pg.time.Clock()
    world = World(name, type, seed)
    player = load_player(world, mode)
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
        world.draw(screen, player)
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
                        case pg.K_RIGHT:
                            ui.move_indice(1)
                        case pg.K_LEFT:
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
                                    play(name, mode, type, seed)
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
                                        name, type, mode, seed, _ = ui.get_world()
                                        play(name, mode, type, seed)
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
