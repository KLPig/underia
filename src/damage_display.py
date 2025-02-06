from src import underia, values
from matplotlib import pyplot as plt

pts = []
lbls = []

for w in underia.WEAPONS.values():
    iw = underia.ITEMS[w.name.replace(' ', '_')]
    for dt, dmg in w.damages.items():
        pts.append((iw.rarity, dmg * (37 if dt is values.DamageTypes.ARCANE else 1) * 40 / (w.at_time + w.cd + 1)))
        lbls.append(f'{w.name} { {values.DamageTypes.PHYSICAL: 'PHY', values.DamageTypes.PIERCING: 'PIC',
                                  values.DamageTypes.MAGICAL: 'MAG', values.DamageTypes.ARCANE: 'ARC', 
                                  values.DamageTypes.THINKING: 'THK'}[dt] }')

plt.scatter([p[0] for p in pts], [p[1] for p in pts])
plt.xlabel('Rarity')
plt.ylabel('Damage')
#for i, txt in enumerate(lbls):
#    plt.text(pts[i][0], pts[i][1], txt)
plt.show()