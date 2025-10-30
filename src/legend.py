from underia import dialog
import version
from resources import path
import constants
import pygame as pg
import os

pt = path.get_path('assets/graphics/legend')
image = {l: pg.image.load(os.path.join(pt, l)) for l in os.listdir(pt) if l.endswith('.png')}

def show_legend():
    window = pg.display.get_surface()
    music = pg.mixer.Sound(os.path.join(path.get_path('assets/musics'), 'the_legend.ogg'))
    dialogger = dialog.Dialogger(48, pg.Rect(0, window.get_height() - 180, window.get_width(), 180), target_surface=window, speed=.3)#12)
    texts = [[f'UNDERIA version {version.VERSION[0]}.{version.VERSION[1]}.{version.VERSION[2]}',
              'Copyright © 2025 KLPIG,\nlicensed under BSD 2-clause license.', 'by KLPIG\n',
              'Released in 14/06/2025.',
              'Press [C] to continue.', 'Press [ESC] to quit.', 'Assets:', 'Music from Undertale OST, Deltarune OST(Chapters 1-4),\nand Terraria OST.',
              'Sound effects from game Undertale, Deltarune\n, and Terraria.',
              'Image drawn by KLPIG', 'All for purposes in studying.'],
             ['Once upon a time, the world was full in chaos.',
              'Everything\'s both dark and light,\neither good or evil.',
              'Only the original chaos creature can live \nin this world.'],
             ['However, after a second, or a millennium, \nor even FOREVER, as there was no TIME here,',
              'There was a tree seedling, and a cross.',
              'They are the GOD.',
              'World starts to have a direction, a law.'],
             ['Soon, the seedling has grown into a tree,\nwe call it the WORLD\'S TREE, has formed the LAND.',
              'Also, the cross formed the sky,\nwe call it the FAITH.'],
             ['The WORLD\'S TREE SAID, "There should be a law."\nSo he created MATTERS and CLOCK,',
              'which controlled the substance and the current \nof time of the world.',
              'The FAITH SAID, "There should be LIGHT."\nSO he created the GODS EYE.\n',
              'They spin around the world, \nstaring for the day and night.',
              'But they didn\'t notice that, \nthere was something staring at him.'],
             ['The gods should stand up to find for \nthe ABYSS CREATURE,',
              'MATTERS and CLOCK together, \ncreated 3 mechanical and 3 biological being.'],
             ['With the 6 being and 2 gods, the WORLD\'S TREE\ntoiled for ages to fight for the ABYSS CREATURE.'],
             ['Knowing they might die, the WORLDS TREE created\nthe human\'s and monsters.',
              'Those clever creatures knew use tools and magics\nand these 2 races rule the world.'],
             ['The world tree has dead.', 'He left the world, his leaf became the rain,\nmaking millions of life.',
              'Also, one bulb-shaped flower became a\ndeformed plant in the rainforest.',
              'The ABYSS CREATURE has been destroyed,\nonly leaving its eye'],
             ['Dear traveller, can you save this world?']]
    if constants.LANG == 'zh':
        dialogger.speed *= 8
        texts = [[f'UNDERIA, v.{version.VERSION[0]}.{version.VERSION[1]}.{version.VERSION[2]}',
                  '版权所有 © 2025 KLPIG，\n采用 BSD-2 Simplified 许可证授权。', '由 KLPIG 制作\n',
                  '于2025年6月14日发布',
                  '按 [C] 继续。', '按 [ESC] 退出。',
                  '音乐、音效来自 Undertale(传说之下), Deltarune(三角符文), \nTerraria(泰拉瑞亚) 原声带。',
                  '图像由 KLPIG 绘制', 'ai翻译，勿喷（改了一点）。', '只用于学习用途。'],
                 ['很久很久以前，世界充满了混沌。',
                  '一切既黑暗而光明，\n非善亦非恶。',
                  '只有原初的混沌生物能在此中生存。'],
                 ['然而，或许是片刻之后，还是万万年之后，甚至是永恒，\n诞生了一株树苗和一块十字。',
                  '他们，是神。',
                  '世界开始有了方向和法则。'],
                 ['不久，树苗长成了大树，人称「世界之树」，创造了大地。',
                  '同时，十字架构成了天空，人称「信」。'],
                 ['世界之树说：“这里应该有法则。”\n于是他创造了「物」和「时」，',
                  '以控制世界中的实体和时间流。',
                  '信仰说：“这个世界应该有光明。”\n于是他创造了「神之眼」。\n',
                  '它们围绕世界旋转，\n日夜注视着世界。',],
                 ['「神」们发现了来自「深渊」的生物，',
                  '「物」和「时」一起，\n创造了 3 个机械和3 个血肉生物。'],
                 ['有了这 6 个生物和 2 个神，世界之树\n用了无数年与深渊生物战斗。'],
                 ['作为「遗产」，世界之树创造了人类和怪物。',
                  '这些聪明的生物懂得使用工具和魔法，\n这两个种族统治了世界。'],
                 ['「世界之树」死了。', '他离开了世界，他的叶子化作了雨水，\n滋润万物。',
                  '同时，一株球形花成为了雨林中\n一种畸形植物。',
                  '深渊生物已被摧毁，\n其眼却留在了人间。'],
                 ['亲爱的人儿啊，你能拯救这个世界吗？']]

    for t in texts:
        dialogger.push_dialog(*t)
    dialogger.update([])
    while True:
        dialogger.dialog_rect = pg.Rect(0, window.get_height() - 180, window.get_width(), 180)
        window.fill((0, 0, 0))
        no = [i for i in range(len(texts)) if dialogger.curr_text in texts[i]][0]
        if no > 0 and not music.get_num_channels():
            music.play()
            dialogger.speed = 3
        im = image[f'tale{no}.png']
        img = pg.transform.scale(im, ((window.get_height() - 180) / im.get_height() * im.get_width(), window.get_height() - 180))
        imr = img.get_rect(midtop=(window.get_width() / 2, 0))
        window.blit(img, imr)
        keys = []
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
            elif event.type == pg.KEYDOWN:
                keys.append(event.key)
                if event.key == pg.K_ESCAPE:
                    pg.quit()
                    quit()
                elif event.key == pg.K_F4:
                    constants.FULLSCREEN = not constants.FULLSCREEN
                    pg.display.set_mode(pg.display.get_window_size(), (pg.FULLSCREEN if constants.FULLSCREEN else 0) | constants.FLAGS)
        if pg.K_c in keys or pg.K_DELETE in keys:
            cv = pg.Surface(window.get_size(), pg.SRCALPHA)
            cv.blit(window, (0, 0))
            if constants.USE_ALPHA:
                for i in range(255):
                    pg.event.get()
                    window.fill((0, 0, 0))
                    cv.set_alpha(255 - i)
                    window.blit(cv, (0, 0))
                    pg.display.update()
                break
        dialogger.update(keys)
        pg.display.update()
        if dialogger.curr_text == '':
            break
    music.stop()