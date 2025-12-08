from visual import story
from resources import path
from underia import game
import pygame as pg
import constants

STORIES = [
    ([['A strange notebook appeared on your hand.'],
      ['...']],
     [
          [['"Ores"', "Disrupted by 'Chords', \nOres summon by the world seems a bit different.", 'Four basic metal ore: copper, iron/cobalt, steel/silver\n and platinum/zirconium.']],
          [['"The Huge Eye at Night"', 'How to attract it: A blood moon or \na bloody small eyeball.(made by materials from his servant)']],
          [["True Eye - The Watcher of Terror", "55 AT -9/4/17/29 DF\nAn eye shaped monster.", "Sprint towards player and summon small eye servant.\nEye servant may gain its resistance. (MASTERY or higher)",
           "With phases, increasing AT and decreasing DF.\nLast phase immune.(Self deduction, ULTIMATE only)", "Summon: Suspicious Eye under Stone Altar."]],
         [['"Spherical Icy Stuff"', "Ancient stuff from a icy cave.", "IDK IDK IDK WHAT IS THIS\nacheuihianwiciainceiaicnea", "How to summon? Fluffy stuff."]],
         [["Fluffff - The fluffy worm", "90AT 0/4/54/77 DF\n10/12/18/24 BODY PARTS", "The further the distance between, the higher the speed.\nSummon: Wild Fluffball"]],
         [['"Everyday Apple"', "Doctor won\'t find me anymore!!", "How to summon? Just eat it."]],
         [["Worlds Fruit - The Gods Heritage", "64 AT 25/27/32/42 DF\nDrops from the worlds\' tree.", "Teleport to player.\nSummon several servants to protect and attack.", 'Summon: World\'s Apple, drops from some trees.']],
          [['"A red plant"', 'Seems to drop from a huge cubic flexible organism.', 'How to summon? Where everything\'s red.']],
         [["Magma King - The fire monster", "72AT 9/11/13/15 DF\nSeparative cubes.", "Decreasing defense to separate into 2/2/3/3 cubes.\nSummon: Fire Slime"]],
         [["Tornado and Car Park Destroy", "The desert is mystery!\nLet's go to play, shall we?"]],
         [["Sandstorm - The Ghost of Desert", "180 AT 10/12/14/16 DF\nSeveral sandstorms.", "Summon: Storm"]],
         [["'Post-chaotic Angel'", "'The world is in chaos, \nuntil a angel appears.'", "We call it: 'The Spirit Angel'"]],
         [["'Echo - Underia'", "He must be the most powerful one among those REALITYs.",
           "His 6 sub-laws built up the bedrock.\nUnfortunately, he can't ever stay in a EXTENT.",
           "For the 'plan', \nhe is an indispensable force."]],
         [["Ray - Spirit Angel", '??AT ??DF\nHuman-like angel.', 'Able to use weapons to attack.\nChallenge him or finish his task may increase his acceptance to you.', 'Summon: Legend Soul or Curse Ray(NPC).']],
         [["'Echo - Ray & KPui", "We should have already thought about it.\nChaos just attacked us.", 'Their only target is him, \nthe GOD of KARMA', 'Fortunately, he left his spirit.\nI put it in UNDERIA...',
           'Our FATE is flowing...\nHow can we do?']],
         [["...", "Above the timeline, \n2,046,184AF, year 12", "...", "ETERNAL, what time is it now in REALITY?",
           "25 DEC?\n that should be Christmas..."],
          ["[ring... ring...]\nCall from REALITY..?", "...\n'UNDERIA! Merry christmas!'", "'We have to have some activities, shall me?'", "...What did you do to my world?"]],
         [["'Christmas Tree'", '...No no no!\nNot this tree!', 'A pine tree,\nu\'know?', 'And should be decorated with bells...\nSomething like that...', 'How to summon: a present!']]
      ],

     ),
    ([['This is a new notebook.', 'It\'s strange, same as notebook A?',
       '...', '\'NOTES\', it says.\n...by Robert Johnson'],
      ['\'NOTES, -by Robert Johnson\'\nwritten in a elegant italic font.']],
     [
      [],
      [],
      [],
      [],]),
    ([['This is a new notebook.', '...', '\'NOTES\'', '...by Eric Lee'],
      ['\'NOTES, -by Eric Lee\'\nwritten in a unclear and crazy font']],
     [[],
      [],
      [],
      [],
      [],
      [],
      [],
      ])
]

CHAPTERS = [
    [('L1', 'Ore'), ('M1', 'Unknown Eye Organism'), ('D1', 'True Eye - The Watcher of Terror'), ('M1B', 'Spherical Icy Stuff'),
     ('D1B', 'Fluffff - The fluffy worm'), ('M1C', 'Everyday Apple'), ('D1C', 'Worlds Fruit - The Gods Heritage'), ('M2', 'Red Plant'),
     ('D2', 'Magma King - The fire monster'), ('M3', "Tornado and Car Park Destroy"), ("D3", "Sandstorm - The Ghost of Desert"),
     ("MS1", "Post-chaotic Angel"), ("T1", "Echo - UNDERIA"), ("MD1", "The spirit angel - Ray"), ("T2", "Echo - RAY & KPUI"),
     ('TS', 'Echo - ???Christmas???'), ("MSC1", "Christmas Tree!!")],
    [('Intro', 5), ('1.', 6), ('2.', 7), ('3.', 8), ('4.', 9)],
    [('Intro', 10), ('Kun Kun', 10), ('Chicken Soup', 10), ('Tung Tung', 10), ('Hadi', 10), ('Spiked Head', 10), ('Final', 11)],
]

def guidance(md: str):
    pass

def start_write():
    story.show_story('note0tale',
                     [["A mysterious pen starts to write through midair,\nwords flows into my notebook..."]])

def show_notebook(chapter=0):
    pre_words, words = STORIES[chapter]
    chapters = CHAPTERS[chapter]
    story.show_story(f'note{chapter}intro',
                     [pre_words[0]])
    sel_c = 0
    window = pg.display.get_surface()
    font = pg.font.Font(path.get_path('assets/dtm-mono.otf' if constants.LANG != 'zh' else 'assets/fz-pixel.ttf'),
                        54)
    if constants.LANG == 'zh':
        font.set_bold(True)
    while True:
        window.fill((0, 0, 0))
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    sel_c = (sel_c - 1 + len(chapters)) % len(chapters)
                elif event.key == pg.K_DOWN:
                    sel_c = (sel_c + 1) % len(chapters)
                elif event.key == pg.K_RETURN:
                    if chapters[sel_c][0] in game.get_game().player.nts:
                        story.show_story(f'note{chapter}{chapters[sel_c][0]}', words[sel_c])
                elif event.key == pg.K_ESCAPE:
                    return
        di = sel_c // 8
        for j, (cht, nm) in enumerate(chapters[di * 8:di * 8 + 8]):
            i = j + di * 8
            y = 120 + j * 80
            x = 100
            if i == sel_c:
                c = (255, 255, 0)
            else:
                c = (255, 255, 255)
            text = font.render(f'{cht}. ' + (nm if cht in game.get_game().player.nts  else '???'), True, c)
            window.blit(text, (x,  y))
        pg.display.flip()
