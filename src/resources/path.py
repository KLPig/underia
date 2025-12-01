import os
import sys

from constants import DEBUG, OS
import resources.log as log

if not DEBUG:
    if OS == 'Windows':
        pt = os.path.join(os.environ['APPDATA'], 'Underia')
    else:
        pt = '/Library/Underia'
else:
    pt = os.path.dirname(sys.modules['__main__'].__file__)

log.info("Discovering path...")
log.info(pt)
d = os.listdir(pt)
if 'assets' not in d:
    log.critical('Assets not found.')
    exit()


def get_path(filename=None):
    global pt
    if filename:
        return os.path.join(pt, filename)
    else:
        return pt


if OS == 'Windows':
    save_path = os.environ.get('HOMEPATH')
else:
    save_path = os.environ.get('HOME')
if save_path is None:
    save_path = '.'
save_path = os.path.join(save_path, '.underia')
if not os.path.exists(save_path):
    os.makedirs(save_path)

def get_save_path(filename):
    global save_path
    return os.path.join(save_path, filename)
