class UnderiaModData:
    def __init__(self, name, version, author, description):
        self.name = name
        self.version = version
        self.author = author
        self.desc = description

class UnderiaMod:
    def __init__(self, items, recipes, weapons, projectiles, entities, setup_func, update_func):
        self.items = items
        self.recipes = recipes
        self.weapons = weapons
        self.projectiles = projectiles
        self.entities = entities
        self.setup_func = setup_func
        self.update_func = update_func