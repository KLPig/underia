import underia

img_str = ("<div class='item %s %s-%s'> <img src='assets/graphics/items/%s.png' "
           "onclick='location.href=\"./items.html#%s-main\"'> <span class='amount %s'>%s</span> </div>")
target = input('Target item: ')
target_item = underia.ITEMS[target]
included = []

def get_string(item, amount=1):
    tar_item = underia.ITEMS[item]
    recipes = [r for r in underia.RECIPES if r.result == item]
    if underia.TAGS['workstation'] in tar_item.tags:
        amount = 1
    if not len(recipes) or item in included:
        return f'<li>{img_str % ("main", tar_item.id, "main", tar_item.id, tar_item.id,
                                 "", f"{tar_item.name} *{amount}")}</li>'
    included.append(item)
    recipe = recipes[0]
    fmt = (f'<li>{img_str % ("main", tar_item.id, "main", tar_item.id, tar_item.id, 
               "caret", f"{tar_item.name} *{amount}")}'
           f'\n<ul class=\'nested\'>\n%s\n</ul></li>')
    n_str = ''
    for it, am in recipe.material.items():
        n_str += get_string(it, am * amount // recipe.crafted_amount) + '\n'
    return fmt % n_str

base = ('<!DOCTYPE html>\n<html>\n<head>\n<meta charset=\'utf-8\'>'
        f'\n<title>{target_item.name} - Recipe Tree</title>'
        '\n<link rel=\'stylesheet\' type=\'text/css\' href=\'tree.css\'>'
        '\n<link rel=\'stylesheet\' type=\'text/css\' href=\'styles.css\'>'
        '\n</head>\n<body><ul id=\'myUL\'>\n%s\n</ul>\n</body>\n'
        '<script src=\'tree.js\'></script>\n</html>')

with open(f'{target}_recipe.html', 'w') as f:
    f.write(base % get_string(target))