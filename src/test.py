from src import underia

game = underia.Game()
underia.write_game(game)

game.monsters.append(underia.Monsters.Test((0, 0)))

game.run()