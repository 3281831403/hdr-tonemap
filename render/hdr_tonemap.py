"""HDR 色调映射：曝光、PQ 与色域裁剪：待实现的核心模块。"""

from __future__ import annotations


def tonemap(rgb, exposure_ev, use_aces):
    """曝光并做 ACES 或线性钳制，返回 (r,g,b)。"""
    raise NotImplementedError

def pq_to_nits(pq):
    """ST 2084 PQ 码值转绝对亮度。"""
    raise NotImplementedError

def display_encode(rgb, gamut, dither_xy):
    """按色域裁剪并加抖动，返回 (r,g,b)。"""
    raise NotImplementedError
