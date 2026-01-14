| Major-Element(LV.X) | React-Element(LV.Y) | Condition       | Effect                                           |
|---------------------|---------------------|-----------------|--------------------------------------------------|
| Fire                | Water               | `X > MAX(2, Y)` | **Evaporation** - Direct Damage                  |
| Fire                | Water               | `Y > MAX(3, X)` | **Solidify** - Control                           |
| Fire                | Air                 | `Y > MAX(2, X)` | **Flame** - Ranged Burning Effect                |
| Earth               | Water               | `Y > X > 2`     | **Mudslide** - Add mass                          | 
| Earth               | Air                 | `Y - 1 > X > 1` | **Erosion** - Decrease damage                    | 
| Water               | Fire                | `Y > X > 2`     | **Melt** - Direct Damage                         |
| Life                | Fire                | `6 > Y > X > 2` | **Ember** - Direct Burning Effect                |
| Life                | Fire                | `X > Y > 5`     | **Nirvara** - Percentage damage                  |
| Earth               | Life                | `X > Y > 2`     | **Seedling** - Decrease defense                  |
| Death               | Life                | `X = Y > 2`     | **Reborn** - Decrease resistance                 |
| Earth               | Death               | `MIN(X, Y) > 2` | **Tomb** - Decrease resistance                   |
| Fire                | Light               | `Y > X > 2`     | **Enlighten** - Ranged Damage                    |
| Dark                | Death               | `X = Y > 4`     | **Reap** - Direct Damage                         |
| Light               | Life                | `X = Y > 4`     | **Shine** - Criticize                            |
| Death               | Time                | `X > 5`         | **Hell** - Global Continuous Damage              |
| Life                | Time                | `X > 5`         | **Growth** - Heal                                |
| Fire                | Water               | `X = Y > 6`     | ***Infinity & Infinitesimal*** - Damage & Freeze |
| Air                 | Water               | `X = Y > 6`     | ***Extent*** - Global Knockback                  |
| Life                | Death               | `X = Y > 6`     | ***Karma & Samsara*** - Deduct HP                |
| Light               | Dark                | `X = Y > 6`     | **Existence** - Chance to kill                   |
| Time                | Space               | `X = Y > 6`     | **Eternal** - Timestop                           |