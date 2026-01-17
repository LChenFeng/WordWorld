import pygame as pg
import numpy as np
import win32api
import ctypes

pg.init()

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
size_p = size * 1.4
pw = size_p / size
# 设置字体颜色
color = (255, 255, 255)
nocolor = (127, 127, 127)
# 设置背景颜色
backcolor = (0, 0, 0)
knapcolor = (200, 200, 200)
# 设置字体
font_path = 'Data/resource/Zpix-beta-3.0.2.ttf'
save_path = 'Save'
block_path = ['Data/json/blocks/chinese.json', 'Data/json/blocks/symbol.json']
real_path = 'Data/json/recipes'
font = pg.font.Font(font_path, round(size))
title = pg.transform.scale(pg.image.load('Data/resource/title.png'), (WIDTH, HEIGHT))
tw = title.get_width()
th = title.get_height()
# 设置区块大小
chunk_size = (48, 256)
world_size = (9600, 256)
# 表示世界中区块的编号范围
edgechunk = (-100, 99)
# 设置x轴边界
edgex = (-4800, 4799)
# 设置y轴边界
edgey = (-127, 128)
# 获取屏幕刷新率
fps = win32api.EnumDisplaySettings(None, 0).DisplayFrequency
# 计算刷新时间
dt = 1 / fps

g = 56

p = [0.9, 0.1]


def draw_word(screen, text, color, pos, font=font, alpha=255):
    t = font.render(text, True, color)
    t.set_alpha(alpha)
    screen.blit(t, pos)
