import pygame as pg

target_cursor = (
    'x' * 10 + ' ' * 12 + 'x' * 10,
    'x' + ' ' * 30 + 'x',
    'x' + ' ' * 30 + 'x',
    'x' + ' ' * 30 + 'x',
    'x' + ' ' * 30 + 'x',
    'x' + ' ' * 30 + 'x',
    'x' + ' ' * 30 + 'x',
    'x' + ' ' * 30 + 'x',
    'x' + ' ' * 30 + 'x',
    'x' + ' ' * 30 + 'x',
    ' ' * 15 + 'xx' + ' ' * 15,
    ' ' * 15 + 'xx' + ' ' * 15,
    ' ' * 15 + 'xx' + ' ' * 15,
    ' ' * 15 + 'xx' + ' ' * 15,
    ' ' * 15 + 'xx' + ' ' * 15,
    ' ' * 10 + 'x' * 12 + ' ' * 10,
    ' ' * 10 + 'x' * 12 + ' ' * 10,
    ' ' * 15 + 'xx' + ' ' * 15,
    ' ' * 15 + 'xx' + ' ' * 15,
    ' ' * 15 + 'xx' + ' ' * 15,
    ' ' * 15 + 'xx' + ' ' * 15,
    ' ' * 15 + 'xx' + ' ' * 15,
    'x' + ' ' * 30 + 'x',
    'x' + ' ' * 30 + 'x',
    'x' + ' ' * 30 + 'x',
    'x' + ' ' * 30 + 'x',
    'x' + ' ' * 30 + 'x',
    'x' + ' ' * 30 + 'x',
    'x' + ' ' * 30 + 'x',
    'x' + ' ' * 30 + 'x',
    'x' + ' ' * 30 + 'x',
    'x' * 10 + ' ' * 12 + 'x' * 10,
)

target_cursor = [t.replace('x', '.') for t in target_cursor]

sword_cursor = (
    '            xxxx',
    '            xxxx',
    '          xx..xx',
    '          xx..xx',
    '        xx..xx  ',
    '        xx..xx  ',
    '  xx  xx..xx    ',
    '  xx  xx..xx    ',
    '  xxxx..xx      ',
    '  xxxx..xx      ',
    '    xxxx        ',
    '    xxxx        ',
    '  xx  xxxx      ',
    '  xx  xxxx      ',
    'xx              ',
    'xx              '
)

sword_cursor = [t.replace('x', '#').replace('.', 'x').replace('#', '.') for t in sword_cursor]

arrow_cursor_cursor = pg.cursors.Cursor((24, 24), (0, 0), *pg.cursors.compile(pg.cursors.thickarrow_strings))
target_cursor_cursor = pg.cursors.Cursor((32, 32), (16, 16), *pg.cursors.compile(target_cursor))
sword_cursor_cursor = pg.cursors.Cursor((16, 16), (15, 0), *pg.cursors.compile(sword_cursor))
