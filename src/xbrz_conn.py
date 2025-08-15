import math
import numpy as np
from enum import Enum
from typing import List, Tuple, Callable, Dict, Any


class RotationDegree(Enum):
    ROT_0 = 0
    ROT_90 = 1
    ROT_180 = 2
    ROT_270 = 3


class BlendType(Enum):
    BLEND_NONE = 0
    BLEND_NORMAL = 1
    BLEND_DOMINANT = 2


class ColorFormat(Enum):
    RGB = 1
    ARGB = 2
    ARGB_UNBUFFERED = 3


class ScalerCfg:
    __slots__ = ('luminanceWeight', 'equalColorTolerance', 'centerDirectionBias',
                 'dominantDirectionThreshold', 'steepDirectionThreshold')

    def __init__(self):
        self.luminanceWeight = 1.0
        self.equalColorTolerance = 30.0
        self.centerDirectionBias = 1.0
        self.dominantDirectionThreshold = 3.6
        self.steepDirectionThreshold = 2.2


def make_pixel(a: int, r: int, g: int, b: int) -> int:
    return (a << 24) | (r << 16) | (g << 8) | b


def get_alpha(pixel: int) -> int:
    return (pixel >> 24) & 0xFF


def get_red(pixel: int) -> int:
    return (pixel >> 16) & 0xFF


def get_green(pixel: int) -> int:
    return (pixel >> 8) & 0xFF


def get_blue(pixel: int) -> int:
    return pixel & 0xFF


def gradientRGB(pixFront: int, pixBack: int, M: int, N: int) -> int:
    def calc_color(cF, cB):
        return (cF * M + cB * (N - M)) // N

    return make_pixel(
        255,
        calc_color(get_red(pixFront), get_red(pixBack)),
        calc_color(get_green(pixFront), get_green(pixBack)),
        calc_color(get_blue(pixFront), get_blue(pixBack))
    )


def gradientARGB(pixFront: int, pixBack: int, M: int, N: int) -> int:
    weightFront = get_alpha(pixFront) * M
    weightBack = get_alpha(pixBack) * (N - M)
    weightSum = weightFront + weightBack
    if weightSum == 0:
        return 0

    def calc_color(cF, cB):
        return (cF * weightFront + cB * weightBack) // weightSum

    a = weightSum // N
    r = calc_color(get_red(pixFront), get_red(pixBack))
    g = calc_color(get_green(pixFront), get_green(pixBack))
    b = calc_color(get_blue(pixFront), get_blue(pixBack))
    return make_pixel(a, r, g, b)


def distYCbCr(pix1: int, pix2: int, lumaWeight: float) -> float:
    r_diff = get_red(pix1) - get_red(pix2)
    g_diff = get_green(pix1) - get_green(pix2)
    b_diff = get_blue(pix1) - get_blue(pix2)

    k_b = 0.0593
    k_r = 0.2627
    k_g = 1 - k_b - k_r

    scale_b = 0.5 / (1 - k_b)
    scale_r = 0.5 / (1 - k_r)

    y = k_r * r_diff + k_g * g_diff + k_b * b_diff
    c_b = scale_b * (b_diff - y)
    c_r = scale_r * (r_diff - y)

    return math.sqrt((lumaWeight * y) ** 2 + c_b ** 2 + c_r ** 2)


def fill_block(target: np.ndarray, x: int, y: int, width: int, color: int, block_width: int, block_height: int):
    for dy in range(block_height):
        for dx in range(block_width):
            target[y + dy, x + dx] = color


class BlendResult:
    __slots__ = ('blend_f', 'blend_g', 'blend_j', 'blend_k')

    def __init__(self):
        self.blend_f = BlendType.BLEND_NONE
        self.blend_g = BlendType.BLEND_NONE
        self.blend_j = BlendType.BLEND_NONE
        self.blend_k = BlendType.BLEND_NONE


class Kernel4x4:
    __slots__ = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p')

    def __init__(self):
        self.a = self.b = self.c = self.d = 0
        self.e = self.f = self.g = self.h = 0
        self.i = self.j = self.k = self.l = 0
        self.m = self.n = self.o = self.p = 0


class Kernel3x3:
    __slots__ = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i')

    def __init__(self):
        self.a = self.b = self.c = 0
        self.d = self.e = self.f = 0
        self.g = self.h = self.i = 0


def pre_process_corners(ker: Kernel4x4, cfg: ScalerCfg, dist_func) -> BlendResult:
    res = BlendResult()
    if (ker.f == ker.g and ker.j == ker.k) or (ker.f == ker.j and ker.g == ker.k):
        return res

    jg = (dist_func(ker.i, ker.f) + dist_func(ker.f, ker.c) +
          dist_func(ker.n, ker.k) + dist_func(ker.k, ker.h) +
          cfg.centerDirectionBias * dist_func(ker.j, ker.g))
    fk = (dist_func(ker.e, ker.j) + dist_func(ker.j, ker.o) +
          dist_func(ker.b, ker.g) + dist_func(ker.g, ker.l) +
          cfg.centerDirectionBias * dist_func(ker.f, ker.k))

    if jg < fk:
        dominant = cfg.dominantDirectionThreshold * jg < fk
        if ker.f != ker.g and ker.f != ker.j:
            res.blend_f = BlendType.BLEND_DOMINANT if dominant else BlendType.BLEND_NORMAL
        if ker.k != ker.j and ker.k != ker.g:
            res.blend_k = BlendType.BLEND_DOMINANT if dominant else BlendType.BLEND_NORMAL
    elif fk < jg:
        dominant = cfg.dominantDirectionThreshold * fk < jg
        if ker.j != ker.f and ker.j != ker.k:
            res.blend_j = BlendType.BLEND_DOMINANT if dominant else BlendType.BLEND_NORMAL
        if ker.g != ker.f and ker.g != ker.k:
            res.blend_g = BlendType.BLEND_DOMINANT if dominant else BlendType.BLEND_NORMAL
    return res


class OutputMatrix:
    def __init__(self, scale: int, rot: RotationDegree, target: np.ndarray, trg_width: int):
        self.scale = scale
        self.rot = rot
        self.target = target
        self.trg_width = trg_width
        self.y = 0
        self.x = 0

    def set_pos(self, x: int, y: int):
        self.x = x
        self.y = y

    def ref(self, i: int, j: int) -> int:
        if self.rot == RotationDegree.ROT_0:
            return self.target[self.y + i, self.x + j]
        elif self.rot == RotationDegree.ROT_90:
            return self.target[self.y + (self.scale - 1 - j), self.x + i]
        elif self.rot == RotationDegree.ROT_180:
            return self.target[self.y + (self.scale - 1 - i), self.x + (self.scale - 1 - j)]
        elif self.rot == RotationDegree.ROT_270:
            return self.target[self.y + j, self.x + (self.scale - 1 - i)]
        return 0

    def set_ref(self, i: int, j: int, value: int):
        if self.rot == RotationDegree.ROT_0:
            self.target[self.y + i, self.x + j] = value
        elif self.rot == RotationDegree.ROT_90:
            self.target[self.y + (self.scale - 1 - j), self.x + i] = value
        elif self.rot == RotationDegree.ROT_180:
            self.target[self.y + (self.scale - 1 - i), self.x + (self.scale - 1 - j)] = value
        elif self.rot == RotationDegree.ROT_270:
            self.target[self.y + j, self.x + (self.scale - 1 - i)] = value


class Scaler:
    def __init__(self, scale: int):
        self.scale = scale

    def blend_line_shallow(self, col: int, out: OutputMatrix):
        pass  # To be implemented per scaler

    def blend_line_steep(self, col: int, out: OutputMatrix):
        pass

    def blend_line_steep_and_shallow(self, col: int, out: OutputMatrix):
        pass

    def blend_line_diagonal(self, col: int, out: OutputMatrix):
        pass

    def blend_corner(self, col: int, out: OutputMatrix):
        pass

    def alpha_grad(self, pix_back: int, pix_front: int, M: int, N: int):
        pass


class Scaler2x(Scaler):
    def __init__(self, alpha_grad_func):
        super().__init__(2)
        self.alpha_grad_func = alpha_grad_func

    def blend_line_shallow(self, col: int, out: OutputMatrix):
        self.alpha_grad_func(out.ref(1, 0), col, 1, 4)
        self.alpha_grad_func(out.ref(1, 1), col, 3, 4)

    def blend_line_steep(self, col: int, out: OutputMatrix):
        self.alpha_grad_func(out.ref(0, 1), col, 1, 4)
        self.alpha_grad_func(out.ref(1, 1), col, 3, 4)

    def blend_line_steep_and_shallow(self, col: int, out: OutputMatrix):
        self.alpha_grad_func(out.ref(1, 0), col, 1, 4)
        self.alpha_grad_func(out.ref(0, 1), col, 1, 4)
        self.alpha_grad_func(out.ref(1, 1), col, 5, 6)

    def blend_line_diagonal(self, col: int, out: OutputMatrix):
        self.alpha_grad_func(out.ref(1, 1), col, 1, 2)

    def blend_corner(self, col: int, out: OutputMatrix):
        self.alpha_grad_func(out.ref(1, 1), col, 21, 100)


# Similar classes would be defined for Scaler3x, Scaler4x, etc.

def blend_pixel(ker: Kernel3x3, scaler: Scaler, out: OutputMatrix, blend_info: int, cfg: ScalerCfg, dist_func):
    if blend_info == 0:
        return

    rotations = [RotationDegree.ROT_0, RotationDegree.ROT_90, RotationDegree.ROT_180, RotationDegree.ROT_270]
    for rot in rotations:
        out.rot = rot
        # Apply blending based on rotation (implementation depends on full scaler logic)


def scale_image(factor: int, src: np.ndarray, trg: np.ndarray, cfg: ScalerCfg, y_first: int, y_last: int,
                dist_func, alpha_grad_func, oob_reader):
    src_height, src_width = src.shape
    trg_height, trg_width = trg.shape

    if y_first >= y_last or src_width <= 0:
        return

    # Preprocessing and main loop would be implemented here
    pass


def scale(factor: int, src: np.ndarray, trg: np.ndarray, col_fmt: ColorFormat, cfg: ScalerCfg, y_first: int,
          y_last: int):
    if factor == 1:
        trg[y_first:y_last] = src[y_first:y_last]
        return

    if col_fmt == ColorFormat.RGB:
        dist_func = lambda p1, p2: distYCbCr(p1, p2, cfg.luminanceWeight)
        alpha_grad_func = lambda back, front, M, N: gradientRGB(front, back, M, N)
        # oob_reader = OobReaderDuplicate (to be implemented)
    elif col_fmt in [ColorFormat.ARGB, ColorFormat.ARGB_UNBUFFERED]:
        # Similar setup for ARGB formats
        pass

    scaler = {
        2: Scaler2x(alpha_grad_func),
        # 3: Scaler3x(alpha_grad_func), etc.
    }.get(factor)

    if scaler:
        scale_image(factor, src, trg, cfg, y_first, y_last, dist_func, alpha_grad_func,
                    None)  # oob_reader omitted for brevity


# Example usage
if __name__ == "__main__":
    src_image = np.zeros((100, 100), dtype=np.uint32)  # Example input
    trg_image = np.zeros((200, 200), dtype=np.uint32)  # 2x output
    cfg = ScalerCfg()
    scale(2, src_image, trg_image, ColorFormat.RGB, cfg, 0, 100)