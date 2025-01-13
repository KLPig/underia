from src import underia, values
from matplotlib import pyplot as plt

pts = []
lbls = []

for w in underia.WEAPONS.values():
    iw = underia.ITEMS[w.name.replace(' ', '_')]
    for dt, dmg in w.damages.items():
        pts.append((iw.rarity, dmg * (37 if dt is values.DamageTypes.ARCANE else 1) * 40 / (w.at_time + w.cd)))
        lbls.append(f'{w.name} { {values.DamageTypes.PHYSICAL: 'Physical', values.DamageTypes.PIERCING: 'Piercing',
                                  values.DamageTypes.MAGICAL: 'Magical', values.DamageTypes.ARCANE: 'Arcane'}[dt] }')

plt.scatter([p[0] for p in pts], [p[1] for p in pts])
plt.xlabel('Rarity')
plt.ylabel('Damage')
for i, txt in enumerate(lbls):
    plt.annotate(txt, (pts[i][0], pts[i][1]))
plt.show()