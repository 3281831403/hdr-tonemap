# HDR 色调映射：曝光、PQ 与色域裁剪

HDR 在曝光、ACES、PQ 解码、色域映射和抖动上出错，导致高光死白或暗部断层。本仓库固定显示链路。

- 领域：游戏、图形与多媒体
- 子方向：图形渲染
- 语言/框架：Python 3, pytest
- 初始状态：15 个参数化用例全部失败

## 目录结构

```
README.md
conftest.py
.gitignore
render/__init__.py
render/hdr_tonemap.py
tests/test_hdr_tonemap.py
```

## 需要修复的 10 个问题

1. 曝光按 EV 以 2 的幂缩放
2. ACES 曲线在高光段单调收敛到 1
3. PQ 按 ST 2084 解码到绝对亮度
4. SDR 输出按色域裁剪到 0..1
5. HDR 输出保留超过 1 的亮度
6. 抖动按像素坐标生成，暗部不出现色带
7. alpha 不参与色调映射
8. 多相机曝光独立
9. 色彩空间转换在 tonemap 前完成
10. 显示设备峰值亮度参与映射

## 15 条验收契约

    01. tonemap linear — `tonemap`
    02. tonemap exposure — `tonemap`
    03. tonemap aces — `tonemap`
    04. tonemap aces high — `tonemap`
    05. tonemap negative — `tonemap`
    06. pq zero — `pq_to_nits`
    07. pq one — `pq_to_nits`
    08. pq mid — `pq_to_nits`
    09. pq small — `pq_to_nits`
    10. pq high — `pq_to_nits`
    11. encode sdr — `display_encode`
    12. encode hdr — `display_encode`
    13. encode dither — `display_encode`
    14. encode gamut — `display_encode`
    15. encode white — `display_encode`

## 当前状态

`render/hdr_tonemap.py` 只保留函数签名与文档字符串，所有函数体统一
`raise NotImplementedError`。`tests/test_hdr_tonemap.py` 使用一个
`@pytest.mark.parametrize` 装载 15 条契约，初始全部失败且没有 collection error。

```bash
python -m pytest -q
```

预期输出包含 `15 failed`。实现 `render/hdr_tonemap.py` 后，15 条契约应全部通过。
