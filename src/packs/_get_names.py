from xml.etree import ElementTree as etree
import os

ss = './ore_and_npc.py'
ssr = ss + '.data.xml'

xml = ''
if os.path.exists(ssr):
    with open(ssr, 'r') as f:
        xml = f.read()

if xml:
    root = etree.fromstring(xml)
else:
    root = etree.fromstring('<classes></classes>')

with open(ss, 'r') as f:
    lines = f.readlines()
classes = []
ais = []
for i in range(len(lines) - 1):
    l1 = lines[i].strip()
    l2 = lines[i + 1].strip()

    if l1.startswith('@entity.Entities.entity_type') and l2.startswith('class'):
        classes.append(l2.removeprefix('class ').split('(')[0])
    elif l1.startswith('@entity.AIs.entity_ai') and l2.startswith('class'):
        ais.append(l2.removeprefix('class ').split('(')[0])

print()

print('# From pack:', ss)
for a in ais:
    if root.find(f'ai[@name="{a}"]') is None:
        root.append(etree.Element('ai', name=a))
        print(f'class {a}(AIs.AIDefinition):\n\tpass')

print()

print('# From pack:', ss)
for c in classes:
    if root.find(f'class[@name="{c}"]') is None:
        root.append(etree.Element('class', name=c))
        print(f'class {c}(EntityDefinition):\n\tpass')

with open(ssr, 'w') as f:
    f.write(etree.tostring(root, encoding='unicode'))

