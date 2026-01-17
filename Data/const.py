import pygame as pg
import numpy as np
import json
import win32api
import ctypes

pg.init()
pg.mixer.init(frequency=44100, buffer=512)

# 获取屏幕信息
info = pg.display.Info()
# 获取屏幕宽度
WIDTH = info.current_w
# 获取屏幕高度
HEIGHT = info.current_h
# 计算缩放比例，取最小值
sc = ctypes.windll.user32.GetDpiForWindow(ctypes.windll.user32.GetForegroundWindow()) / 96
scale = sc * (WIDTH / 1920 + HEIGHT / 1080) / 2

# 计算字体大小
size = 42 * scale
per = size * scale * 2
pw = 1.4
size_p = size * pw

# 设置字体颜色
color = (255, 255, 255)
nocolor = (127, 127, 127)
# 设置背景颜色
backcolor = (0, 0, 0)
knapcolor = (200, 200, 200)
# 设置字体
font_path = 'Data/resource/Zpix-beta-3.0.2.ttf'
bgm_path = 'Data/resource/EndlessAdventures.ogg'
save_path = 'Save'
block_path = ['Data/json/blocks/chinese.json', 'Data/json/blocks/symbol.json']
real_path = 'Data/json/recipes'
font_m = pg.font.Font(font_path, round(size))
title = pg.transform.scale(pg.image.load('Data/resource/title.png'), (WIDTH, HEIGHT))
bgm = pg.mixer.music.load(bgm_path)
# 设置区块大小
chunk_size = (48, 256)
world_size = (9600, 256)
# 表示世界中区块的编号范围
edgechunk = (-100, 99)
# 设置x轴边界
edgex = (-4800, 4799)
# 设置y轴边界
edgey = (-127, 128)
dp_chunks = 2
# 获取屏幕刷新率
fps = win32api.EnumDisplaySettings(None, 0).DisplayFrequency
# 计算刷新时间
dt = 1 / fps

g = 56

p = [0.9, 0.1]

defaults = {
    "color": [255, 255, 255],  # RGB 颜色（3个uint8）
    "hardness": 0,  # 硬度（uint8）
    "penetrable": True,  # 是否可穿透（bool）
    "placeable": True,
    "replaceable": False,  # 是否可替换（bool）
    "stacking": 64,
    "exclevel": 1
}


def draw_word(surface, text, color, pos, font=font_m):
    t = font.render(text, True, color)
    surface.blit(t, pos)


def char_init():
    inits = []
    dt = np.dtype([('name', 'U1'), ('color', '3u1'), ('hardness', 'u1'), ('exclevel', 'u1'), ('stacking', 'u1'),
                   ('penetrable', 'bool'), ('placeable', 'bool'), ('replaceable', 'bool')])
    with open(block_path[0], 'r', encoding='utf-8') as file:
        c = json.load(file)
    with open(block_path[1], 'r', encoding='utf-8') as file:
        s = json.load(file)
    c.update(s)
    c = {int(i): c[i] for i in c.keys()}

    for key, sub_dict in c.items():
        # 从子字典中提取字段，缺失时使用默认值
        name = sub_dict.get('name')
        color = sub_dict.get("color", defaults["color"])
        hardness = sub_dict.get("hardness", defaults["hardness"])
        penetrable = sub_dict.get("penetrable", defaults["penetrable"])
        placeable = sub_dict.get("placeable", defaults["placeable"])
        replaceable = sub_dict.get("replaceable", defaults["replaceable"])
        exclevel = sub_dict.get("exclevel", defaults["exclevel"])
        stacking = sub_dict.get("stacking", defaults["stacking"])

        # 校验 color 格式（必须为3个 uint8 数值）
        if len(color) != 3:
            color = (color[:3] + [0, 0, 0])[:3]
        color = [int(c) % 256 for c in color]

        # 校验 hardness 格式（必须为整数）
        try:
            hardness = int(hardness) % 256  # uint8 范围 0-255
        except (TypeError, ValueError):
            hardness = defaults["hardness"]

        # 校验布尔字段（确保是 bool 类型）
        penetrable = bool(penetrable)
        replaceable = bool(replaceable)

        inits.append((name, color, hardness, exclevel, stacking, penetrable, placeable, replaceable))
    del c, s
    return np.array(inits, dtype=dt)


CHAR = char_init()
