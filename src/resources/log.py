import logging
import datetime
import os
import constants

if constants.DEBUG:
    pt = None
else:
    pt = os.path.join(os.path.expanduser('~'), './.underia', 'logs')

    if not os.path.exists(pt):
        os.makedirs(pt)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
log_html = ('<!DOCTYPE html><html><head><title>LOG</title><link rel="stylesheet" href="../styles.css" type="text/css">'
            '</head><body><table><tr><th class="tt-time">TIME</th><th class="tt-lvl">LEVEL</th><th class="tt-msg">MESSAGE</th>'
            '</tr>')

fle = f'{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log'

if not constants.DEBUG:
    file_handler = logging.FileHandler(os.path.join(pt, fle))
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s %(levelname)s [%(name)s] %(message)s')
    file_handler.setFormatter(formatter)


    logger.addHandler(file_handler)

else:
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s %(levelname)s [%(name)s] %(message)s')
    stream_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)

def msg_html(lvl, msg):
    global log_html, fle, pt
    log_html += (f'<tr class="tt-{lvl}"><td>{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S').upper()}</td>'
                 f'<td>{lvl}</td><td>{msg}</td></tr>')
    with open(os.path.join(pt if pt is not None else './src/logs', fle + '.html'), 'w') as f:
        f.write(log_html + '</table></body></html>')
        f.close()

def debug(*args):
    logger.debug(' '.join(map(str, args)))
    msg_html('DEBUG', ' '.join(map(str, args)))

def info(*args):
    logger.info(' '.join(map(str, args)))
    msg_html('INFO', ' '.join(map(str, args)))

def warning(*args):
    logger.warning(' '.join(map(str, args)))
    msg_html('WARN', ' '.join(map(str, args)))

def error(*args):
    logger.error(' '.join(map(str, args)))
    msg_html('ERROR', ' '.join(map(str, args)))

def critical(*args):
    logger.critical(' '.join(map(str, args)))
    msg_html('FATAL', ' '.join(map(str, args)))
