# 导入需要的库包
import pygame
import random
import math
import sys
import time
from pygame.locals import *
from pygame import mixer

# 初始化
mixer.init()
pygame.init()
snow = []
SIZE = (729, 511)
RGB = (255, 255, 255)
PI = math.pi
sin = math.sin(PI/8)
cos = math.cos(PI/8)
next = ([1.6, 0], [0, -1.6], [1.6 ** 0.5, -1.6 ** 0.5], [-1.6 **0.5, -1.6 ** 0.5], [sin, -cos],[cos, -sin],[-sin, -cos], [-cos, -sin])
screen = pygame.display.set_mode(SIZE)
pygame.display.set_caption("Snow Picture Video")

# 模拟随机雪花飘落场景
for i in range(400):
    x = random.randrange(0, SIZE[0])
    y = random.randrange(0, SIZE[1])
    speedx = random.randint(-100, 101)/100
    speedy = random.randint(50, 380)/100
    snow.append([x, y, speedx, speedy])

# 定义主体函数
def Play(image):
    # 导入背景图片
    background = pygame.surface.Surface(SIZE)
    for k in range(3*10**2):
        # 点击关闭按按钮结束程序运行
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
        # 在缓冲区中绘制图像
        screen.blit(background, (0, 0))
        for i in range(len(snow)):
            for j in range(8):
                r = snow[i][3]
                beg = (snow[i][0] + r*next[j][0], snow[i][1] + r*next[j][1])
                end = (snow[i][0] + r*next[j][0], snow[i][1] + r*next[j][1])
                pygame.draw.line(screen, RGB, beg, end, 1)
                snow[i][0] += snow[i][2]/1.5
                snow[i][1] += snow[i][3] / 1.5
                if snow[i][1] > SIZE[1]:
                    snow[i][0] = random.randrange(0, SIZE[0])
                    snow[i][1] = random.randrange(-50, -10)
                pygame.display.flip()
        return False

# 加载音乐
#mixer.music.load('F:/music.mp3')
#mixer.music.play()

# Pygame游戏开发最小框架
while True:
    # 遍历要播放的图片
    for i in range(3):
        Play('F:/' + str(i) + '.PNG')

#mixer.music.stop()
pygame.quit()