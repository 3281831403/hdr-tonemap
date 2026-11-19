"""HDR 色调映射：曝光、PQ 与色域裁剪。

本模块把 HDR 线性颜色送到显示设备前必须完成的几步固定下来：

1. 曝光按 EV 以 2 的幂缩放，而不是线性加减。
2. ACES 曲线用 Narkowicz 拟合，高光段单调收敛到 1，不会出现亮部反折。
3. PQ 码值按 ST 2084 常量解码成绝对亮度（nits）。
4. SDR 输出按色域裁剪到 0..1，负值与超白不会直接进显示器。
5. HDR 输出保留超过 1 的高光（上界放宽到 10000 nits 对应的 10.0）。
6. 抖动由像素坐标生成，邻域像素错开阈值，暗部不出现色带。
"""

from __future__ import annotations

# ST 2084 (PQ) 常量。
_C1 = 0.8359375
_C2 = 18.8515625
_C3 = 18.6875
_INV_M1 = 1.0 / 0.1593
_INV_M2 = 1.0 / 0.2393
_PEAK_NITS = 10000.0

# 抖动幅度：一个 8bit 量化步长。
_DITHER_STEP = 1.0 / 255.0

# HDR 输出的亮度上界（线性，对应峰值亮度）。
_HDR_MAX = 10.0


def _clamp(value, low, high):
    """把 value 钳制到 [low, high]。"""
    return max(low, min(high, value))


def _aces_fit(x):
    """Narkowicz 的 ACES 拟合曲线，高光段单调趋近 1。"""
    return (x * (2.51 * x + 0.03)) / (x * (2.43 * x + 0.59) + 0.14)


def tonemap(rgb, exposure_ev, use_aces):
    """按 EV 曝光后做 ACES 或线性钳制，返回 (r, g, b)。

    - 曝光倍数 ``2**exposure_ev`` 作用在线性颜色上，而不是线性加减 EV；
    - ``use_aces`` 为真时走 ACES 曲线，否则直接线性；
    - 两条路径最后都钳制到 [0, 1]：负值不外泄，高光收敛到 1，亮部不反折。
    """
    scale = 2.0 ** exposure_ev
    result = []
    for channel in rgb:
        value = channel * scale
        if use_aces:
            value = _aces_fit(value)
        result.append(_clamp(value, 0.0, 1.0))
    return tuple(result)


def pq_to_nits(pq):
    """ST 2084 PQ 码值转绝对亮度（nits，0..10000）。"""
    if pq <= 0.0:
        return 0.0
    p = pq ** _INV_M1
    numerator = max(p - _C1, 0.0)
    denominator = _C2 - _C3 * p
    return _PEAK_NITS * (numerator / denominator) ** _INV_M2


def _dither_offset(dither_xy):
    """由像素坐标生成 [-0.5, 0.5) 个量化步长的抖动偏移。"""
    x, y = dither_xy
    threshold = ((int(x) * 7 + int(y) * 13) % 16) / 16.0
    return (threshold - 0.5) * _DITHER_STEP


def display_encode(rgb, gamut, dither_xy):
    """按色域裁剪并加抖动，返回 (r, g, b)。

    先裁剪再加抖动：负值统一抬到 0；``gamut='sdr'`` 时上界压到 1，
    ``gamut='hdr'`` 时上界放宽到 ``_HDR_MAX``，保留超过 1 的高光。
    抖动阈值由像素坐标决定，相邻像素不同，暗部不会因为固定偏置出现色带。
    """
    offset = _dither_offset(dither_xy)
    high = 1.0 if str(gamut).lower() == "sdr" else _HDR_MAX
    return tuple(_clamp(channel, 0.0, high) + offset for channel in rgb)
