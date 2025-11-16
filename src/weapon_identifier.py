import underia.weapons as weapons
import underia.inventory as inventory
from xml.etree import ElementTree
import values.damages as damages
import version

datas = ElementTree.parse('weapons.xml').getroot()
n = int(datas.find('version').text)
log_content = f'<p>#Changelog: {n + 1}</p><list>'
add = 0
mod = 0

for k, w in weapons.WEAPONS.items():
    if datas.find(f"weapon[@id='{k}']") is None:
        log_content += f'<li><b>Added {inventory.ITEMS[k].name} (#{k})</b></li>'
        we = ElementTree.Element('weapon', id=k)
        sp = ElementTree.Element('speed')
        sp.text = str(w.cd)
        we.append(sp)
        at = ElementTree.Element('at_time')
        at.text = str(w.at_time)
        we.append(at)
        dmg_s = ElementTree.Element('damages')
        for dt, dv in w.damages.items():
            dmg = ElementTree.Element('damage', type=damages.DamageKeys[dt])
            dmg.text = str(dv)
            dmg_s.append(dmg)
        we.append(dmg_s)
        datas.append(we)
        add += 1
    else:
        de = datas.find(f"weapon[@id='{k}']")
        if de.find('speed').text != str(w.cd):
            log_content += f'<li>Changed {inventory.ITEMS[k].name} (#{k}) speed from {de.find('speed').text} to {w.cd}</li>'
            de.find('speed').text = str(w.cd)

            mod += 1
        if de.find('at_time').text != str(w.at_time):
            log_content += f'<li>Changed {inventory.ITEMS[k].name} (#{k}) at_time from {de.find('at_time').text} to {w.at_time}</li>'
            de.find('at_time').text = str(w.at_time)

            mod += 1
        dmg_s = de.find('damages')
        for dt, dv in w.damages.items():
            if dmg_s.find(f"damage[@type='{damages.DamageKeys[dt]}']") is None:
                log_content += f'<li>Added {inventory.ITEMS[k].name} (#{k}) damage type {damages.DamageKeys[dt]} with value {dv}</li>'
                dmg = ElementTree.Element('damage', type=damages.DamageKeys[dt])
                dmg.text = str(dv)
                dmg_s.append(dmg)

                mod += 1
            else:
                if dmg_s.find(f"damage[@type='{damages.DamageKeys[dt]}']").text != str(dv):
                    log_content += f'<li>Changed {inventory.ITEMS[k].name} (#{k}) damage type {damages.DamageKeys[dt]} value from {dmg_s.find(f"damage[@type='{damages.DamageKeys[dt]}']").text} to {dv}</li>'
                    dmg_s.find(f"damage[@type='{damages.DamageKeys[dt]}']").text = str(dv)
                    mod += 1

datas.find('version').text = str(n + 1)
log_content += f'</list><p>Total changes: {add} added, {mod} modified</p>'
log_content += f'<p>Log versioned <i>{version.VERSION}</i></p>'
with open('weapons.xml', 'w') as f:
    f.write(ElementTree.tostring(datas, encoding='unicode'))
with open(f'changelog/weapons{n + 1}.html', 'w') as f:
    f.write(log_content)