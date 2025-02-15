from src.underia import dialog, version
from src.resources import path
from src import constants
import pygame as pg
import os

pt = path.get_path('assets/graphics/legend')
image = {l: pg.image.load(os.path.join(pt, l)) for l in os.listdir(pt)}

def show_legend():
    window = pg.display.get_surface()
    music = pg.mixer.Sound(os.path.join(path.get_path('assets/musics'), 'the_legend.ogg'))
    dialogger = dialog.Dialogger(48, pg.Rect(0, window.get_height() - 180, window.get_width(), 180), target_surface=window, speed=12)
    texts = [[f'UNDERIA version {version.VERSION[0]}.{version.VERSION[1]}.{version.VERSION[2]}',
              'All left reserved.', 'by KLPIG\n', 'Released in 15/2/2025',
              'Press [C] to continue.', 'Press [ESC] to quit.', 'Assets:', 'Music from Undertale OST, Deltarune OST,\nand Terraria OST.',
              'Image drawn by KLPIG'],
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
             ['Dear traveller, can you save this world?']
             ]
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
