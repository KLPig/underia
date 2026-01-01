import requests
import xml.etree.ElementTree as et
import version
import resources.log as log
import constants

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

def check(c_hash=None) -> tuple[bool, bool, str, list[str]]:
    if not constants.WEB_CHECK:
        return False, True, 'Web-check skipped!', []
    try:
        response = requests.get(target)
        if response.status_code == 200:
            root = et.fromstring(response.content)
            log.info('Datas get from web, ' + str(root))
            name = root.find('name').text
            log.info('Name: '+ name)
            ff = root.find('content/hash[@version="%s.%s.%s"]' % version.VERSION)
            if ff is not None:
                log.info('Content Hash ' + str(int(ff.text)))
                if int(ff.text) == c_hash:
                    b = False
                    log.info('Game not modified')
                else:
                    b = True
                    log.warning('Game modified')
            else:
                b = True
                log.warning('Typical version not found')

            evs = root.find('events')
            ns = []
            if evs is not None:
                for e in evs.findall('event'):
                    ns.append(e.text)
                log.info('Events: ' + str(ns))


            version_new = root.find('version[@id="newest"]')
            v1 = version_new.find('first').text
            v2 = version_new.find('second').text
            v3 = version_new.find('third').text
            log.info('Newest version: %s.%s.%s' % (v1, v2, v3))
            version_sup = root.find('version[@id="supported"]')
            v1e = version_sup.find('first').text
            v2e = version_sup.find('second').text
            v3e = version_sup.find('third').text
            log.info('Supported version: %s.%s.%s' % (v1e, v2e, v3e))
            assert compare((v1, v2, v3), (v1e, v2e, v3e)) <= 0, 'Newest version is not supported'
            c1 = compare((v1e, v2e, v3e), version.VERSION)
            c2 = compare((v1, v2, v3), version.VERSION)
            print(c1, c2)
            if c1 < 0:
                log.critical('Version no longer supported!')
                return b, False, 'Your version is no longer supported!', ns
            elif c2 >= 0:
                log.info('Newest version!')
                return b, True, 'Newest version!', ns
            elif c1 > 0:
                log.info('New version available!')
                return b, True, 'New version available!', ns
            else:
                log.warning('Version up-to-date')
                return b, True, 'Version up-to-date!', ns
        else:
            return False, False, 'Error %s while connecting to internet' % response.status_code
    except requests.exceptions.RequestException as e:
        return False, False, 'Error while connecting to internet: %s' % e, ns
    except Exception as e:
        return False, False, 'Error while checking for updates: %s' % e, ns

if __name__ == '__main__':
    print(check())