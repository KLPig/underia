from mods import mod
import os
import sys
import pickle

def wrap():
    module = sys.modules['__main__']
    code = ''
    with open(module.__file__, 'r') as f:
        code = f.read()

    try:
        name = getattr(module, 'MOD_NAME')
        version = getattr(module, 'MOD_VERSION')
        author = getattr(module, 'MOD_AUTHOR')
        description = getattr(module, 'MOD_DESCRIPTION')
    except AttributeError:
        print('Error: MOD_NAME, MOD_VERSION, MOD_AUTHOR, and MOD_DESCRIPTION must be defined in the main module.')
        return

    data = mod.UnderiaModData(name, version, author, description)

    try:
        items = getattr(module, 'ITEMS')
        recipes = getattr(module, 'RECIPES')
        weapons = getattr(module, 'WEAPONS')
        projectiles = getattr(module, 'PROJECTILES')
        entities = getattr(module, 'ENTITIES')
        try:
            setup_func = code.split('# SETUP_FUNC')[1]
            update_func = code.split('# UPDATE_FUNC')[1]
        except IndexError:
            print('Error: ')
            return
        try:
            if setup_func is not None:
                exec(setup_func)
        except Exception as e:
            print('Error in setup(): %s' % e)
            input('Continue? (Press Enter to continue)')
        try:
            if update_func is not None:
                exec(update_func)
        except Exception as e:
            print('Error in update(): %s' % e)
            input('Continue? (Press Enter to continue)')
    except AttributeError:
        print('Error: ITEMS, RECIPES, WEAPONS, PROJECTILES, and ENTITIES must be defined in the main module.')
        return

    mod_main = mod.UnderiaMod(items, recipes, weapons, projectiles, entities, setup_func, update_func)

    path = os.path.dirname(module.__file__)
    if not os.path.exists(os.path.join(path, 'dist')):
        os.mkdir(os.path.join(path, 'dist'))
    path = os.path.join(path, 'dist')
    with open(os.path.join(path, 'data.pkl'), 'wb') as f:
        pickle.dump(data, f)
    with open(os.path.join(path,'mod.pkl'), 'wb') as f:
        pickle.dump(mod_main, f)

    if not os.path.exists(os.path.join(path, name)):
        os.mkdir(os.path.join(path, name))
    os.rename(os.path.join(path, 'data.pkl'), os.path.join(path, name, 'data.umod'))
    os.rename(os.path.join(path,'mod.pkl'), os.path.join(path, name, 'mod.umod'))
    if not os.path.exists(os.path.join(path, name, 'assets')):
        os.mkdir(os.path.join(path, name, 'assets'))
    os.system('cp -r "%s" "%s" ' % (os.path.join(path, '..', 'assets'), os.path.join(path, name, 'assets')))

    print('Module wrapped successfully.')
