"""
生成第二只荷兰猪（白/黑/棕三色）的动画帧。

原始帧是单色（橙黄色）填充 + 黑色描边的卡通图，且只画了"头朝左"的一面。
这只三色猪左右两侧花色不同，所以不能简单地水平翻转，需要分别生成：

    frames/tricolor/left/<status>/*.png   头朝左 -> 看到的是猪的【左侧】
    frames/tricolor/right/<status>/*.png  头朝右 -> 看到的是猪的【右侧】

左侧：白底，从头顶到眼睛/耳朵一条黑色带，眼后脸颊一块棕色，背上一块黑色"鞍"，屁股和肚子白色
右侧：白色口鼻，黑色从眼睛一直覆盖到身体侧面，肚子白色

花纹的位置以每帧自动识别出的眼睛、耳朵为锚点，这样在不同姿势（走路/睡觉/被拎起）下都能对齐。

用法:  python tools/make_tricolor_skin.py
"""
import os
import sys
from collections import deque

import numpy as np
from PySide6.QtGui import QImage, QGuiApplication

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'frames')
DST = os.path.join(ROOT, 'frames', 'tricolor')
STATUSES = ['idle', 'sleep', 'walk', 'drag', 'fall', 'sleepwalk', 'walksleep', 'fallidle']

FILL = np.array([200, 154, 64.])      # 原图身体填充色
CLAW = np.array([136, 96, 16.])       # 原图爪子/脚掌颜色

WHITE = np.array([248, 246, 240.])
BLACK = np.array([38, 34, 34.])
BROWN = np.array([150, 80, 36.])
PINK = np.array([232, 178, 170.])
EYE_ON_BLACK = np.array([150, 150, 150.])   # 黑色毛上的五官线条改成灰色，不然看不见


# ---------- 读写 ----------
def load(path):
    im = QImage(path).convertToFormat(QImage.Format_RGBA8888)
    return np.frombuffer(im.constBits(), np.uint8).reshape(im.height(), im.width(), 4).copy()


def save(arr, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    arr = np.ascontiguousarray(arr)
    h, w, _ = arr.shape
    QImage(arr.data, w, h, 4 * w, QImage.Format_RGBA8888).save(path)


# ---------- 特征识别 ----------
def pool(m, k, fn):
    h, w = m.shape
    m = m[:h // k * k, :w // k * k].reshape(h // k, k, w // k, k)
    return fn(fn(m, axis=3), axis=1)


def detectFeatures(a, k=4):
    """返回身体填充区域的外框，以及身体内部的黑色小块（眼睛、耳朵等）"""
    rgb = a[..., :3].astype(float)
    sil = a[..., 3] > 128
    fill = (np.abs(rgb - FILL).sum(-1) < 40) & sil
    ys, xs = np.nonzero(fill)
    bbox = (xs.min(), ys.min(), xs.max(), ys.max())

    dark = (rgb.sum(-1) < 200) & sil
    t = (rgb @ FILL) / (FILL @ FILL)
    other = sil & ~dark & ~fill & (np.abs(rgb - FILL * t[..., None]).sum(-1) > 30)  # 鼻子/舌头/爪子/眼睛高光

    D, S, O = pool(dark, k, np.max), pool(sil, k, np.min), pool(other, k, np.max)
    h, w = D.shape
    seen = np.zeros((h, w), bool)
    comps = []
    for y0, x0 in zip(*np.nonzero(D)):
        if seen[y0, x0]:
            continue
        seen[y0, x0] = True
        q = deque([(y0, x0)])
        pts, touchesOutside, touchesOther = [], False, False
        while q:
            y, x = q.popleft()
            pts.append((y, x))
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    yy, xx = y + dy, x + dx
                    if not (0 <= yy < h and 0 <= xx < w) or not S[yy, xx]:
                        touchesOutside = True
                        continue
                    touchesOther |= O[yy, xx]
                    if D[yy, xx] and not seen[yy, xx]:
                        seen[yy, xx] = True
                        q.append((yy, xx))
        # 和外轮廓相连的是描边/腿，不是五官
        if touchesOutside or len(pts) < 150 // k:
            continue
        p = np.array(pts) * k + k / 2
        comps.append(dict(x=p[:, 1].mean(), y=p[:, 0].mean(), n=len(pts) * k, marked=touchesOther))
    return bbox, comps


def pickAnchors(bbox, comps, prevEar=None):
    """在内部小块中找出 耳朵 / 近侧眼睛 / 远侧眼睛（坐标为相对外框的 0~1）"""
    x0, y0, x1, y1 = bbox
    norm = [dict(c, u=(c['x'] - x0) / (x1 - x0), v=(c['y'] - y0) / (y1 - y0)) for c in comps]
    norm = [c for c in norm if c['v'] < 0.75 and c['n'] >= 150]  # 去掉脚

    # 耳朵：最靠后的、没有挨着高光/爪子的小块（睁开的眼睛有白色高光，肚子上的爪子挨着橙色）
    ears = [(c['u'], c['v']) for c in norm if not c['marked']]
    ear = max(ears) if ears else None
    ref = ear or prevEar
    near = far = None
    if ref:
        eyes = sorted([c for c in norm if c['u'] < ref[0] - 0.05 and abs(c['v'] - ref[1]) < 0.2],
                      key=lambda c: -c['u'])
        eyes = [(c['u'], c['v']) for c in eyes]
        # 近侧眼睛离耳朵很近；太远的只可能是远侧眼睛（近侧眼睛没识别出来时）
        if eyes and (ref[0] - eyes[0][0]) * (x1 - x0) < 330:
            near = eyes.pop(0)
        if eyes:
            far = eyes[0]
    return ear, near, far


def anchorsForStatus(frames):
    """逐帧识别，识别失败的用同一动作里最近一帧的结果补上"""
    raw = []
    prevEar = None
    for a in frames:
        bbox, comps = detectFeatures(a)
        ear, near, far = pickAnchors(bbox, comps, prevEar)
        prevEar = ear or prevEar
        raw.append([bbox, ear, near, far])
    for key in (1, 2):
        for i, r in enumerate(raw):
            if r[key] is None:
                order = sorted(range(len(raw)), key=lambda j: abs(j - i))
                r[key] = next(raw[j][key] for j in order if raw[j][key] is not None)
    return raw


# ---------- 花纹 ----------
def ellipse(X, Y, cx, cy, rx, ry, soft=3.0):
    """椭圆覆盖率，边缘做几个像素的抗锯齿"""
    s = np.sqrt(((X - cx) / rx) ** 2 + ((Y - cy) / ry) ** 2)
    return np.clip((1 - s) * min(rx, ry) / soft + 0.5, 0, 1)


def patterns(shape, bbox, ear, near, far, side):
    """返回 (棕色覆盖率, 黑色覆盖率)，坐标系为原图（头朝左）"""
    h, w = shape
    Y, X = np.mgrid[0:h, 0:w].astype(np.float32)
    x0, y0, x1, y1 = bbox
    bw, bh = x1 - x0, y1 - y0
    P = lambda uv: (x0 + uv[0] * bw, y0 + uv[1] * bh)
    Ex, Ey = P(near)
    Rx, Ry = P(ear)
    d = float(np.clip(np.hypot(Rx - Ex, Ry - Ey), 170, 240))  # 眼睛到耳朵的距离作为长度单位
    upright = bh > 0.6 * bw  # 被拎起来/下落时是正面朝外的直立姿势

    brown = np.zeros((h, w), np.float32)
    black = np.zeros((h, w), np.float32)

    if side == 'left':
        # 头顶到眼睛、耳朵的黑色带
        mx, my = (Ex + Rx) / 2, (Ey + Ry) / 2
        black = np.maximum(black, ellipse(X, Y, mx + 0.05 * d, my - 0.55 * d, 1.0 * d, 0.72 * d))
        # 眼睛后下方的棕色脸颊，一直延伸到下巴
        brown = np.maximum(brown, ellipse(X, Y, Ex + 0.45 * d, Ey + 0.55 * d, 0.6 * d, 0.5 * d))
        brown = np.maximum(brown, ellipse(X, Y, Ex + 0.2 * d, Ey + 0.85 * d, 0.45 * d, 0.4 * d))
        # 背上的黑色鞍，屁股留白
        sx0, sx1 = Rx + 0.7 * d, x1 + 0.05 * bw
        if sx1 - sx0 > 0.3 * d:
            saddle = ellipse(X, Y, (sx0 + sx1) / 2, y0 - 0.1 * bh, (sx1 - sx0) / 2, 0.72 * bh)
            rump = ellipse(X, Y, x1 + 0.02 * bw, y1, 0.17 * bw, 0.5 * bh)
            black = np.maximum(black, saddle * (1 - rump))
        # 远侧眼睛是右眼，在黑色里（只在正面/直立的姿势里看得到）
        if far and upright:
            Fx, Fy = P(far)
            black = np.maximum(black, ellipse(X, Y, Fx + 0.05 * d, Fy - 0.1 * d, 0.42 * d, 0.42 * d))
    else:
        # 眼睛、头顶、耳朵一大块黑
        black = np.maximum(black, ellipse(X, Y, Ex + 0.4 * d, Ey - 0.15 * d, 1.0 * d, 0.95 * d))
        # 身体侧面黑色，肚子和屁股留白
        bx0 = Ex + 0.4 * d
        if x1 > bx0:
            body = ellipse(X, Y, x1 + 0.1 * bw, y0 + 0.2 * bh, (x1 + 0.1 * bw - bx0), 0.62 * bh)
            rump = ellipse(X, Y, x1 + 0.02 * bw, y1, 0.14 * bw, 0.55 * bh)
            black = np.maximum(black, body * (1 - rump))
        # 远侧眼睛是左眼，旁边一点棕色
        if far and upright:
            Fx, Fy = P(far)
            brown = np.maximum(brown, ellipse(X, Y, Fx + 0.15 * d, Fy + 0.3 * d, 0.35 * d, 0.3 * d))
    return brown, np.clip(black, 0, 1)


def boxErode(mask, r):
    """用积分图做方形腐蚀"""
    inv = (~mask).astype(np.int32)
    ii = np.pad(inv.cumsum(0).cumsum(1), ((1, 0), (1, 0)))
    h, w = mask.shape
    y0 = np.clip(np.arange(h) - r, 0, h)[:, None]
    y1 = np.clip(np.arange(h) + r + 1, 0, h)[:, None]
    x0 = np.clip(np.arange(w) - r, 0, w)[None, :]
    x1 = np.clip(np.arange(w) + r + 1, 0, w)[None, :]
    return (ii[y1, x1] - ii[y0, x1] - ii[y1, x0] + ii[y0, x0]) == 0


def recolor(a, anchors, side):
    bbox, ear, near, far = anchors
    rgb = a[..., :3].astype(np.float32)
    sil = a[..., 3] > 128
    brown, black = patterns(sil.shape, bbox, ear, near, far, side)

    # 身体颜色：白 -> 棕 -> 黑 依次叠加
    body = WHITE * (1 - brown[..., None]) + BROWN * brown[..., None]
    body = body * (1 - black[..., None]) + BLACK * black[..., None]

    # 描边颜色：外轮廓保持黑色，身体内部的五官在黑毛上变灰
    interior = boxErode(sil, 40).astype(np.float32)
    lineMix = (interior * black)[..., None]
    line = EYE_ON_BLACK * lineMix

    out = a.copy()
    # 原图像素 ≈ t*填充色 + (1-t)*黑色（抗锯齿边缘），按同样比例换成新颜色
    # 鼻子(128,104,64)和填充色很接近，阈值要小一点才不会被误改；爪子只改本身，不碰描边
    for src, dst, minT, maxResidual in ((FILL, body, 0.0, 15), (CLAW, PINK, 0.6, 30)):
        t = np.clip((rgb @ src) / (src @ src), 0, 1)
        m = (np.abs(rgb - src * t[..., None]).sum(-1) < maxResidual) & (t > minT)
        new = dst * t[..., None] + line * (1 - t[..., None])
        out[..., :3][m] = np.clip(new[m], 0, 255).astype(np.uint8)
    return out


def main():
    app = QGuiApplication.instance() or QGuiApplication(sys.argv)
    for status in STATUSES:
        folder = os.path.join(SRC, status)
        names = sorted(f for f in os.listdir(folder) if f.endswith('.png'))
        frames = [load(os.path.join(folder, n)) for n in names]
        allAnchors = anchorsForStatus(frames)
        for name, a, anchors in zip(names, frames, allAnchors):
            save(recolor(a, anchors, 'left'), os.path.join(DST, 'left', status, name))
            # 右侧：在原图坐标里画右侧花纹，然后整体翻转成头朝右
            save(recolor(a, anchors, 'right')[:, ::-1], os.path.join(DST, 'right', status, name))
        print(f'{status}: {len(names)} frames')


if __name__ == '__main__':
    main()
