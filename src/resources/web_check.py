import requests
import xml.etree.ElementTree as et
import version
from tkinter import messagebox

target = 'https://klpig.github.io/underia/data.xml'

def compare(x: tuple[str, str, str], y: tuple[str, str, str]):
    if x[0] != y[0]:
        return 1 if y[0] > x[0] else -1
    elif x[1] != y[1]:
        return 1 if y[1] > x[1] else -1
    elif x[2] != y[2]:
        return 1 if y[2] > x[2] else -1
    else:
        return 0

def check(c_hash=None) -> tuple[bool, bool, str]:
    try:
        response = requests.get(target)
        if response.status_code == 200:
            root = et.fromstring(response.content)
            print('Datas get from web, ', root)
            name = root.find('name').text
            print('Name:', name)
            ff = root.find('content/hash[@version="%s.%s.%s"]' % version.VERSION)
            if ff is not None:
                print('Content Hash', int(ff.text))
                if int(ff.text) == c_hash:
                    b = False
                    print('Game not modified')
                else:
                    b = True
                    print('Game modified')
            else:
                b = True
                print('Typical version not found')
            version_new = root.find('version[@id="newest"]')
            v1 = version_new.find('first').text
            v2 = version_new.find('second').text
            v3 = version_new.find('third').text
            print('Newest version:', '%s.%s.%s' % (v1, v2, v3))
            version_sup = root.find('version[@id="supported"]')
            v1e = version_sup.find('first').text
            v2e = version_sup.find('second').text
            v3e = version_sup.find('third').text
            print('Supported version:', '%s.%s.%s' % (v1e, v2e, v3e))
            assert compare((v1, v2, v3), (v1e, v2e, v3e)) >= 0, 'Newest version is not supported'
            c1 = compare((v1, v2, v3), version.VERSION)
            c2 = compare((v1e, v2e, v3e), version.VERSION)
            if c1 < 0:
                print('Version no longer supported!')
                messagebox.showerror('Error', 'Your version is no longer supported!')
                return b, False, 'Your version is no longer supported!'
            elif c2 >= 0:
                print('Newest version!')
                return b, True, 'Newest version!'
            elif c1 > 0:
                print('New version available!')
                return b, True, 'New version available!'
            else:
                print('Version up-to-date')
                return b, True, 'Version up-to-date!'
        else:
            return False, False, 'Error %s while connecting to internet' % response.status_code
    except requests.exceptions.RequestException as e:
        return False, False, 'Error while connecting to internet: %s' % e
    except Exception as e:
        return False, False, 'Error while checking for updates: %s' % e

if __name__ == '__main__':
    print(check())