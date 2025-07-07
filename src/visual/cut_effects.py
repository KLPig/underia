import math
from visual import draw

def cut_eff(window, rr, sx, sy, ex, ey, color, dark=False):
    sx = int(sx)
    sy = int(sy)
    ex = int(ex)
    ey = int(ey)
    rr = int(rr)
    de = -1 if dark else 1
    k = 100
    dx = (ex - sx) / 1000 * k
    dy = (ey - sy) / 1000 * k
    for i in range(rr, 0, min(-1, -rr // 100)):
        cr = min(255, color[0] + 300 * de - 250 * i * de // rr)
        cg = min(255, color[1] + 300 * de - 250 * i * de // rr)
        cb = min(255, color[2] + 300 * de - 250 * i * de // rr)
        cr = max(0, cr)
        cg = max(0, cg)
        cb = max(0, cb)
        for r in range(1, 1000 // k):
            y = sy + (ey - sy) * r / 1000 * k
            x = sx + (ex - sx) * r / 1000 * k
            eex = x + dx
            eey = y + dy
            draw.line(window, (cr, cg, cb), (x, y), (eex, eey),
                      width=max(1, int(i * math.sin(r / 1000 * k * math.pi))))
