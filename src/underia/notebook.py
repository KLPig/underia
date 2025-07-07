from visual import story
from resources import path
from underia import game
import pygame as pg
import constants

STORIES = [
    ([['This notebook was found in your backpack.', 'It\'s strange, \ndid I put this here?',
     '...', 'Anyway, you looked toward the notebook.', '\'NOTES\', it says.\n...by Henry Victor',
      'Then, you opened the book.'],
      ['You looked at the cover of the book.', '\'NOTES, -by Henry Victor\'\nwritten in a neat and tidy font.']],
     [[['Hi, to somebody who ever see this notebook.', 'I\'m an adventurer just like you.',
       'I\'ve been tried for all the timelines to defeat IT, \nbut it fails.',
       'I\'m here fore a GUIDANCE, a POSSIBILITY, and a SOLUTION.', '...Anyway, just read the notes for more information.']],
      [['This world is extreme and perilous, \neven flowers and trees can be monsters.', 'So, beware! Don\'t be too close.'],
       ['For a award, the world give great ores!', 'Use pickaxe to mine them.'],
       ['Be ware of the darkness, \n and a species of dangerous monsters - the eyes.',
        'They won\'t be common found, when you are strong\nenough, use bloods and cells to attract them.',
        'That huge eye is watching you all the time.', 'You may see crystal stars scuttling on ground.',
        'They used to be a statue, but...\n..you know, they may enhance you magic.', 'I strongly use magic.'],
       ['Oh!\nAnd also', 'There are some plant in the hell.\nImproving your health.',
        'Get it, but make sure you are strong enough,\nalright?', '...a legend is that this will \nattract some mysterious beings...']],
      [['When you see this, the world will be changed.', 'The entities\' soul will be stronger.\nFull of power of spirit.'],
       ['New metals will flow on the world, \nwhich is unbelievably tough and valuable.'],
       ['The legend said the god made several mechanical bosses.', 'These metals may appeal them.']],
      [['To test if you are strong enough,\ntry a chaos creature.',
       'The true king of the poker, \nthe devil in the chaos hell.',
       'You will get a spiritual bulb.', 'The willpower of the ever soul of\na deformed flower.']],
      [['\'Faith\' and \'World\'s tree\' create the gods.', 'Their power is unimaginable.',
        'You need it.', 'You need to get its power.']],
      ]),
    ([['This is a new notebook.', 'It\'s strange, same as notebook A?',
       '...', '\'NOTES\', it says.\n...by Robert Johnson'],
      ['\'NOTES, -by Robert Johnson\'\nwritten in a elegant italic font.']],
     [[],
      [],
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
    [('Intro', 0), ('1.', 1), ('2.', 2), ('3.', 3), ('4.', 4)],
    [('Intro', 5), ('1.', 6), ('2.', 7), ('3.', 8), ('4.', 9)],
    [('Intro', 10), ('Kun Kun', 10), ('Chicken Soup', 10), ('Tung Tung', 10), ('Hadi', 10), ('Spiked Head', 10), ('Final', 11)],
]

def show_notebook(chapter=0):
    pre_words, words = STORIES[chapter]
    chapters = CHAPTERS[chapter]
    story.show_story(f'note{chapter}intro',
                     [pre_words[0] if chapters[0][1] >= game.get_game().player.profile.stage else pre_words[1]])
    sel_c = 0
    window = pg.display.get_surface()
    font = pg.font.Font(path.get_path('assets/dtm-mono.otf' if constants.LANG != 'zh' else 'assets/fz-pixel.ttf'),
                        54)
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
                    if chapters[sel_c][1] <= game.get_game().player.profile.stage:
                        story.show_story(f'note{chapter}{sel_c}', words[sel_c])
                elif event.key == pg.K_ESCAPE:
                    return
        for i, (cht, lv) in enumerate(chapters):
            y = 120 + i * 80
            x = 100
            if i == sel_c:
                c = (255, 255, 0)
            else:
                c = (255, 255, 255)
            l = game.get_game().player.profile.stage >= lv
            text = font.render(f'{cht} {"(locked)" if not l else ""}', True, c)
            window.blit(text, (x,  y))
        pg.display.flip()
