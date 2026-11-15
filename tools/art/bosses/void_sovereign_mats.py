"""Materials for void_sovereign: black-violet faceted void crystal with ghost facets seen through
the glass, magenta void fractures with subsurface bleed, a starlit cavity, a swirling chest star,
crown shards with glowing cores and a tattered cloak that dissolves into the starry void.

Accent discipline: the body is dark violet crystal whose form is carried by cold lavender edge
light, facet ridges and glassy streaks. Magenta is reserved for the void cracks, the eyes, the crown
cores and the chest star (by far the brightest element); violet light for runes, halo and hem."""
import math

import numpy as np

from bosslib import fbm, hash3, palette, vnoise, worley
from bossfx import bevel, dither, dramp, edge_dist, runes, smoothstep, sramp, spec, plane_xy, mix

TAU = 2 * math.pi

# void crystal: deep violet (not black) in the depths, cold lavender on edges and highlights
VC = palette("#05030b", "#0a0516", "#100821", "#170b2c", "#1e0f38", "#271345", "#311854", "#3c1e64",
             "#492576", "#582e8a", "#6a3aa0", "#7f4cb6", "#9864cb", "#b285de", "#cdaaee", "#e6d6fa")
MG = palette("#1a0216", "#3a0632", "#640c56", "#93147e", "#c21fa2", "#e83dc2", "#ff6edb", "#ffa8ec", "#ffe0f8")
VIO = palette("#0f0526", "#230b4d", "#3d1784", "#5c28b8", "#8048e0", "#a679f4", "#cdb0ff", "#efe4ff")
CLOTH = palette("#020103", "#06040b", "#0b0714", "#120b1f", "#1a102b", "#231638", "#2e1d47", "#3b2658", "#4b316b")
NEBV = palette("#04020b", "#0b041c", "#14072e", "#200a42", "#300e58", "#43136f", "#5a1886", "#74209b", "#9030ae")
NEB = palette("#020106", "#070312", "#100620", "#1b0a31", "#2a0e46", "#3d135c", "#541872", "#6f1f86")
STAR = palette("#2a0640", "#5a0f78", "#9a1c9c", "#d434b4", "#f46ad2", "#ffa6e6", "#ffd8f4", "#ffffff")

# world rest position of the chest star (set by the generator after the model is built)
CAVITY = {"c": np.array([0.0, 59.0, -1.5])}


def tone(ctx):
    n = ctx.nw
    return 0.06 * max(0.0, n[1]) - 0.11 * max(0.0, -n[1]) - ctx.ao * 0.5


def spike_prog(ctx):
    """0 at the base of a spike/curve_spike, 1 at its tip (per texel)."""
    prm = ctx.params
    loc = ctx.p[:, 1] - ctx.lo[1]
    if "curve_prog0" in prm:
        f = np.clip(loc / max(prm["spike_len"], 1e-6), 0, 1)
        return prm["curve_prog0"] + (prm["curve_prog1"] - prm["curve_prog0"]) * f
    if "spike_len" in prm:
        return np.clip((prm["spike_y0"] + loc) / prm["spike_len"], 0, 1)
    return np.clip(1 - ctx.t, 0, 1) if ctx.face not in ("up", "down") else np.full(ctx.N, 0.5)

# ============================================================================ void crystal


LDIR = np.array([-0.35, 0.75, -0.55]) / np.linalg.norm([-0.35, 0.75, -0.55])


def face_uv(ctx):
    """Cube-local coordinates in the plane of the current face (model units)."""
    p = ctx.p
    if ctx.face in ("north", "south"):
        return p[:, 0], p[:, 1]
    if ctx.face in ("east", "west"):
        return p[:, 2], p[:, 1]
    return p[:, 0], p[:, 2]


FACE_ID = {"north": 0, "south": 1, "east": 2, "west": 3, "up": 4, "down": 5}


def glass_streaks(ctx):
    """A few diagonal glassy specular streaks (about half the faces get one)."""
    if ctx.plane or ctx.face == "down" or min(ctx.tw, ctx.th) < 6:
        return 0.0
    hh = float(hash3(np.array([ctx.index]), np.array([FACE_ID[ctx.face]]), np.array([0]), 77)[0])
    if hh > 0.5:
        return 0.0
    diag = ctx.i + ctx.j * 0.7
    period = (ctx.tw + ctx.th) * 0.9
    ph = np.mod(diag - hh * 200.0, period)
    return (ph < 1.4) * 0.26 + ((ph > 2.8) & (ph < 3.5)) * 0.1


def crystal_v(ctx, seed=0, freq=0.14, stretch=0.6, base=0.25, striate=0.0, rim=0.16):
    """Value field of faceted void glass: flat facets each tilted at random (lit by a fixed key
    light), a refraction gradient (lighter towards the top of each face, deep violet below), crisp
    cold ridge lines, ghost facets deeper inside, bright cube-edge rims and glassy streaks."""
    p = ctx.p
    q = p * np.array([1.0, stretch, 1.0])
    f1, f2, cid = worley(q, freq, seed + 3)
    e = f2 - f1
    ck = np.floor(cid * 1e6)
    rv = np.stack([hash3(ck, ck * 0 + k, ck * 0, seed + 5) - 0.5 for k in range(3)], 1) * 1.3
    nf = ctx.nw[None, :] + rv
    nf /= np.linalg.norm(nf, axis=1, keepdims=True)
    lam = np.clip(nf @ LDIR, -0.2, 1)
    v = base + (lam - 0.35) * 0.34 + (cid - 0.5) * 0.06
    if ctx.face in ("up",):
        v += 0.12
    elif ctx.face == "down":
        v -= 0.08
    else:
        v += 0.18 * (1 - ctx.t) ** 2.0 - 0.06
    de = tex_dist(ctx, e)
    v += (de < 0.7) * 0.17 - ((de >= 0.7) & (de < 1.9)) * 0.05
    g1, g2, _ = worley(q * 1.45 + ctx.nw * 2.3 + 17.0, freq, seed + 7)
    v += (tex_dist(ctx, g2 - g1) < 0.5) * 0.06
    v += (fbm(p, 0.12, 3, seed + 9) - 0.5) * 0.08
    if striate:
        v += (vnoise(p * np.array([1.4, 0.07, 1.4]), 1.0, seed + 11) - 0.5) * striate
    v += bevel(ctx, 2.0, 0.26, 0.12) + tone(ctx) + 0.18 * spec(ctx, 10)
    if not ctx.plane and rim:
        d = edge_dist(ctx)
        v += (d == 0) * rim * 0.75 + (d == 1) * rim * 0.2
        v += (ctx.j == 0) * rim * 0.7 + (ctx.i == 0) * rim * 0.3
    v += glass_streaks(ctx)
    return v


def crystal_rgb(ctx, v, seed=0):
    rgb = dramp(VC, v, ctx, 0.55)
    h = fbm(ctx.pw, 0.05, 2, seed + 13)
    hz = (np.clip((h - 0.45) * 2.5, 0, 1) * 0.35)[:, None]
    rgb = rgb * (1 - hz) + rgb * np.array([0.82, 0.9, 1.5]) * hz
    p = ctx.p
    gl = hash3(np.floor(p[:, 0] * 2 + .01), np.floor(p[:, 1] * 2 + .01), np.floor(p[:, 2] * 2 + .01), 47 + seed) > 0.994
    rgb[gl] = VC[14]
    return rgb


def tex_dist(ctx, f):
    """Distance in texels to the zero set of a non-negative field f on the current face, using
    the larger one-sided difference (so the V-shaped kink of a Worley edge is not flattened).
    Makes line widths exact regardless of grazing angles or domain warping."""
    if ctx.tw < 2 or ctx.th < 2:
        return np.full(ctx.N, 99.0)
    F = f.reshape(ctx.th, ctx.tw)
    gxf = np.abs(np.diff(F, axis=1, append=F[:, -1:]))
    gxb = np.abs(np.diff(F, axis=1, prepend=F[:, :1]))
    gyf = np.abs(np.diff(F, axis=0, append=F[-1:, :]))
    gyb = np.abs(np.diff(F, axis=0, prepend=F[:1, :]))
    g = np.sqrt(np.maximum(gxf, gxb) ** 2 + np.maximum(gyf, gyb) ** 2).ravel()
    return f / np.maximum(g, 1e-5)


def void_cracks(ctx, rgb, glow, density=0.5, seed=0, freq=0.075, width=1.0):
    """Glowing magenta fractures: domain-warped world-space Worley edges (continuous across faces
    and cubes), drawn at an exact texel width, gated into patches that taper out; darkened lip and a
    soft magenta bleed into the surrounding crystal."""
    pw = ctx.pw
    q = pw * np.array([1.0, 0.6, 1.0])
    q = q + (np.stack([fbm(q, 0.22, 2, 27 + seed), fbm(q + 5.2, 0.22, 2, 28 + seed), fbm(q + 9.7, 0.22, 2, 29 + seed)], 1) - 0.5) * 3.0
    f1, f2, _ = worley(q, freq, 21 + seed)
    d = tex_dist(ctx, f2 - f1)
    g = fbm(pw, 0.045, 2, 23 + seed)
    thr = 0.66 - 0.2 * density
    gate = smoothstep(thr, thr + 0.06, g)
    wv = (0.45 + 0.75 * vnoise(pw, 0.25, 25 + seed)) * width * gate
    wcr = 0.95 * wv
    crack = d < wcr
    core = d < 0.32 * wv
    lip = (d < wcr + 1.0) & ~crack & (wv > 0.1)
    bleed = np.clip(1 - d / (5.0 * np.maximum(wv, 1e-3)), 0, 1) ** 2 * (wv > 0.1)
    rgb = mix(rgb, np.broadcast_to(MG[2], rgb.shape), bleed * 0.4)
    rgb[lip] = rgb[lip] * 0.55
    if crack.any():
        k = 1 - d[crack] / np.maximum(wcr[crack], 1e-6)
        rgb[crack] = sramp(MG, 0.42 + 0.36 * k)
    rgb[core] = MG[7]
    return rgb, glow | crack


def cavity_light(ctx, rgb, glow, R=7.0, strength=1.0):
    """Faces turned toward the chest star pick up its magenta light (emissive where strong)."""
    d = ctx.pw - CAVITY["c"][None, :]
    dist = np.sqrt((d * d).sum(1)) + 1e-6
    facing = np.clip(-(d @ ctx.nw) / dist, 0, 1)
    L = np.clip(facing * np.exp(-(dist / R) ** 2) * strength * 1.4, 0, 1)
    rgb = mix(rgb, sramp(MG, 0.35 + 0.4 * L), L * 0.85)
    return rgb, glow | (L > 0.38)


def crystal(ctx, seed=0, cracks=0.0, crack_w=1.0, cav=False, rune_band=False, striate=0.0, base=0.25):
    v = crystal_v(ctx, seed, striate=striate, base=base)
    rgb = crystal_rgb(ctx, v, seed)
    glow = np.zeros(ctx.N, dtype=bool)
    if rune_band:
        rgb, glow = rune_inlay(ctx, rgb, glow)
    if cracks:
        rgb, glow = void_cracks(ctx, rgb, glow, cracks, seed, width=crack_w)
    if cav:
        rgb, glow = cavity_light(ctx, rgb, glow)
    return rgb, glow


def rune_inlay(ctx, rgb, glow, cell=6.0):
    """Engraved runes in a recessed channel on the side faces (bracers, belt): thin, dim violet."""
    if ctx.face in ("up", "down") or min(ctx.tw, ctx.th) < 8:
        return rgb, glow
    d = edge_dist(ctx)
    tall = ctx.th > ctx.tw * 1.4
    half = 3.0
    if tall:   # vertical channel down the middle of the face
        cx = ctx.tw / 2
        off = np.abs(ctx.i + 0.5 - cx)
        x, y = ctx.i - (cx - half), ctx.j + ctx.index * 5
    else:      # horizontal channel
        cy = ctx.th / 2
        off = np.abs(ctx.j + 0.5 - cy)
        x, y = ctx.i + ctx.index * 7, ctx.j - (cy - half)
    chan = (off < half) & (d >= 2)
    groove = chan & (off > half - 0.6)
    rgb[chan] = rgb[chan] * 0.4
    rgb[groove] = VC[1]
    m, cid = runes(x, y, cell=cell, seed=5 + ctx.index, density=0.36, stroke=0.42, gap=0.24)
    m &= chan & ~groove & (cid < 0.75)
    rgb[m] = sramp(VIO, 0.5 + 0.12 * hash3(ctx.i, ctx.j, ctx.i * 0, 3)[m])
    return rgb, glow | m

# ============================================================================ shaders


def _w(fn):
    def sh(ctx):
        rgb, glow = fn(ctx)
        return rgb, 255, glow
    return sh


def shade_shard(ctx, cracks=0.0, core=False, seed=0, tipcol=0.35, lift=0.26, base=0.25, core_pal=None):
    """Crystal prism along a spike: darker base, lighter violet tip, lit vertical edges,
    optional glowing violet core seen through dark glass (crown shards)."""
    prog = spike_prog(ctx)
    v = crystal_v(ctx, seed, freq=0.24, stretch=0.35, base=base, striate=0.14, rim=0.1)
    v += lift * prog ** 1.6
    side = ctx.face not in ("up", "down")
    if side:
        ei = np.minimum(ctx.i, ctx.tw - 1 - ctx.i)
        v += (ctx.i == 0) * 0.24 + (ctx.i == ctx.tw - 1) * 0.08 - ((ei == 1) * 0.04)
    rgb = crystal_rgb(ctx, v, seed)
    tint = (prog ** 2 * tipcol)[:, None]
    rgb = rgb * (1 - tint) + sramp(VIO, 0.2 + 0.45 * v) * tint
    glow = np.zeros(ctx.N, dtype=bool)
    if core:
        # a glowing core seen through the dark glass: a narrow violet column with a soft halo,
        # hottest mid-length, fading towards the base and the clear tip
        along = np.sin(np.pi * np.clip(prog * 1.05, 0, 1)) ** 0.6
        if side:
            w = np.abs(ctx.s - 0.5) * 2                     # 0 centre line .. 1 face edge
            k = np.clip(1 - w / 0.42, 0, 1) * along
            halo = np.clip(1 - w / 0.8, 0, 1) * along
        else:
            x, y = plane_xy(ctx)
            k = np.clip(1 - np.maximum(np.abs(x), np.abs(y)) / 0.45, 0, 1) * along
            halo = k
        cp = core_pal if core_pal is not None else VIO
        rgb = mix(rgb, sramp(cp, 0.1 + 0.25 * halo), halo * 0.55)
        line = k > 0.3
        rgb[line] = sramp(cp, 0.4 + 0.5 * k[line])
        hot = k > 0.85
        rgb[hot] = cp[-2]
        glow = line
    if cracks:
        rgb, glow = void_cracks(ctx, rgb, glow, cracks, seed + 3, width=0.9)
    return rgb, 255, glow


def shade_claw(ctx):
    prog = spike_prog(ctx)
    v = crystal_v(ctx, 5, freq=0.3, stretch=0.4, base=0.2, striate=0.08, rim=0.0) + 0.3 * prog ** 2.5
    if ctx.face not in ("up", "down"):
        v += (ctx.i == 0) * 0.2 - (ctx.i == ctx.tw - 1) * 0.06
    rgb = crystal_rgb(ctx, v, 5)
    tip = prog > 0.86
    rgb[tip] = mix(rgb[tip], sramp(VC, np.full(tip.sum(), 0.8)), 0.6)
    return rgb, 255, np.zeros(ctx.N, dtype=bool)


def shade_head(ctx):
    """Crown-helm skull: smooth black glass; the face carries deep sockets with slanted
    white-hot slit eyes, void tears and a forehead fracture."""
    v = crystal_v(ctx, 9, freq=0.16, base=0.25, rim=0.13)
    rgb = crystal_rgb(ctx, v, 9)
    glow = np.zeros(ctx.N, dtype=bool)
    if ctx.face == "north":
        x, y = plane_xy(ctx)
        sock = np.zeros(ctx.N)
        eye = np.zeros(ctx.N, dtype=bool)
        hot = np.zeros(ctx.N, dtype=bool)
        tears = np.zeros(ctx.N, dtype=bool)
        for sx in (-1, 1):
            ax, ay = 0.13 * sx, -0.14
            bx, by = 0.78 * sx, 0.06
            dx, dy = bx - ax, by - ay
            L2 = dx * dx + dy * dy
            u = np.clip(((x - ax) * dx + (y - ay) * dy) / L2, 0, 1)
            px, py = ax + u * dx, ay + u * dy
            d = np.sqrt((x - px) ** 2 + (y - py) ** 2)
            th = 0.02 + 0.075 * np.sin(np.pi * np.clip(u * 1.08, 0, 1)) ** 0.7
            eye |= d < th
            hot |= d < th * 0.5
            sock = np.maximum(sock, np.clip(1 - d / 0.26, 0, 1) ** 0.7)
            # void tears dripping from the inner corners
            tx = 0.22 * sx + 0.035 * np.sin(y * 9 + sx)
            tears |= (np.abs(x - tx) < 0.03) & (y < -0.12) & (y > -0.34 + 0.06 * sx)
        rgb = rgb * (1 - 0.9 * sock[:, None])
        fore = (np.abs(x - 0.03 * np.sin(y * 14)) < 0.04) & (y > 0.62)
        rgb[tears | fore] = MG[3]
        rgb[eye] = MG[6]
        rgb[hot] = MG[8]
        glow = eye | tears | fore
    return rgb, 255, glow


def shade_void_wall(ctx):
    """Back of the chest cavity: a deep nebula with pin stars (all emissive)."""
    p = ctx.pw
    n = fbm(p * np.array([1.0, 1.0, 1.0]), 0.3, 4, 61)
    sw = fbm(p + 3.1, 0.18, 3, 63)
    v = 0.2 + (n - 0.5) * 0.9 + (sw - 0.5) * 0.4
    if ctx.face != "north":
        v = v * 0.6
    rgb = sramp(NEB, v + dither(ctx, 0.04))
    h = hash3(ctx.i, ctx.j, np.full(ctx.N, ctx.index), 67)
    st = h > 0.965
    rgb[st] = sramp(STAR, 0.6 + 0.4 * (h[st] - 0.965) / 0.035)
    return rgb, 255, np.ones(ctx.N, dtype=bool)


def _swirl(ctx, wind=2.4, gain=1.0, core_r=0.22, thr=0.15, seed=71):
    x, y = plane_xy(ctx)
    r = np.sqrt(x * x + y * y) + 1e-6
    a = np.arctan2(y, x)
    arm = 0.5 + 0.5 * np.cos(2 * (a + wind * np.log(r)))
    v = np.exp(-(r / core_r) ** 2) * 1.25 + arm ** 2.2 * np.exp(-r / 0.62) * 1.15 * gain
    v += (vnoise(np.c_[x * 6, y * 6, np.zeros(ctx.N)], 1.0, seed) - 0.5) * 0.14
    h = hash3(ctx.i, ctx.j, np.zeros(ctx.N), seed + 2)
    dots = (h > 0.92) & (r < 0.95)
    on = ((v > thr) & (r < 0.97)) | dots
    rgb = sramp(STAR, 0.2 + 0.85 * np.clip(v, 0, 1))
    rgb[dots & (v <= thr)] = STAR[6]
    rgb[r < core_r * 0.55] = STAR[7]
    return rgb, np.where(on, 255, 0), on


def shade_swirl(ctx):
    """Two-armed spiral galaxy (2-fold symmetric so a 180 degree spin loops seamlessly)."""
    return _swirl(ctx)


def shade_swirl2(ctx):
    """Second, tighter and fainter spiral layer turned 90 degrees: four arms in total."""
    return _swirl(ctx, wind=3.2, gain=0.75, core_r=0.15, thr=0.2, seed=75)


def shade_flare(ctx):
    """Four-pointed star flare (an astroid), white core fading to pink."""
    x, y = plane_xy(ctx)
    d = np.abs(x) ** 0.55 + np.abs(y) ** 0.55
    on = d < 0.78
    v = 1 - d / 0.78
    rgb = sramp(STAR, 0.45 + 0.6 * v)
    return rgb, np.where(on, 255, 0), on


def shade_core(ctx):
    x, y = plane_xy(ctx)
    r = np.maximum(np.abs(x), np.abs(y))
    rgb = sramp(STAR, 1.0 - 0.3 * r)
    return rgb, 255, np.ones(ctx.N, dtype=bool)


def shade_cloak(ctx):
    """Tattered void cloak: dark violet cloth hanging in pleats (deeper towards the hem) that frays
    and dissolves into an emissive starfield in its lower part; ragged hem strips, moth holes and
    side frays (binary alpha) with a thin ember rim where the void eats the cloth."""
    prm = ctx.params
    v0, v1, pid = prm.get("v0", 0.0), prm.get("v1", 1.0), prm.get("pid", 0)
    total = prm.get("total", 58.0)
    v = v0 + (v1 - v0) * ctx.t                      # 0 top of the whole cloak, 1 hem
    X = (ctx.s - 0.5) * ctx.tw / 2.0                # units across the panel
    Y = v * total
    P = np.c_[X + pid * 37.0, Y, np.full(ctx.N, pid * 5.0)]
    warp = fbm(P * np.array([0.12, 0.035, 1]), 1.0, 3, 81)
    ph = X * 0.8 + warp * 6.0
    fold = np.sin(ph)
    lit = np.cos(ph)                                 # pleats lit from one side
    fold2 = np.sin(X * 2.1 + warp * 10.0 + 1.3)
    depth = 0.7 + 0.5 * smoothstep(0.0, 0.6, v)
    base = 0.45 + depth * (0.16 * fold + 0.17 * np.clip(lit, 0, 1) ** 4) + 0.05 * fold2
    base += (fbm(P, 0.3, 3, 83) - 0.5) * 0.08 - v * 0.05
    base += ((ctx.i + ctx.j) % 2) * 0.022 - (ctx.j % 3 == 0) * 0.012      # weave
    top = np.clip(1 - Y / 2.0, 0, 1)
    base += top * 0.12 - ctx.ao * 0.3
    rgb = dramp(CLOTH, base, ctx, 0.6)
    # a thin dim violet border woven along the top and sides of the upper cloak
    bord = ((np.abs(Y - 1.6) < 0.35) | ((np.abs(np.abs(ctx.s - 0.5) * ctx.tw / 2.0 - (ctx.tw / 4.0 - 1.2)) < 0.3) & (v < 0.45)))
    rgb[bord] = mix(rgb[bord], sramp(VIO, np.full(bord.sum(), 0.34)), 0.6)
    # the void: an emissive nebula with stars replaces the cloth towards the hem
    vn = smoothstep(0.5, 0.9, v + (fbm(P, 0.08, 3, 85) - 0.5) * 0.45)
    nebf = fbm(P * np.array([1.0, 0.7, 1.0]), 0.14, 4, 87)
    neb_v = 0.08 + 0.9 * nebf ** 1.6 + 0.12 * vn
    rgb = mix(rgb, sramp(NEBV, neb_v + dither(ctx, 0.03)), vn)
    seam = (vn > 0.04) & (vn < 0.2)
    rgb[seam] = mix(rgb[seam], sramp(VIO, np.full(seam.sum(), 0.3)), 0.35)
    h = hash3(ctx.i, ctx.j, np.full(ctx.N, pid + ctx.index * 3), 89)
    dens = 0.055 * vn
    star = h > 1 - dens
    big = h > 1 - dens * 0.18
    rgb[star] = sramp(STAR, np.full(star.sum(), 0.62))
    rgb[big] = STAR[7]
    glow = star | ((vn > 0.55) & (neb_v > 0.5))
    # alpha: ragged hem strips + holes + frayed sides
    strip = vnoise(np.c_[X * 0.55 + pid * 13, np.zeros(ctx.N), np.zeros(ctx.N)], 1.0, 91)
    strip2 = vnoise(np.c_[X * 1.7 + pid * 7, Y * 0.05, np.zeros(ctx.N)], 1.0, 92)
    hem = 1.0 - (0.02 + 0.12 * strip ** 1.5 + 0.035 * strip2)
    holes_f = fbm(P * np.array([0.9, 0.45, 1.0]), 0.22, 3, 93)
    hole_thr = 0.8 - 0.15 * smoothstep(0.3, 1.0, v)
    sx = np.abs(ctx.s - 0.5) * 2
    fray = 1.0 - (0.02 + 0.2 * smoothstep(0.2, 1.0, v) * vnoise(np.c_[np.zeros(ctx.N), Y * 0.45 + pid * 9 + 3 * (ctx.s > 0.5), np.zeros(ctx.N)], 1.0, 95))
    cut = (v > hem) | (holes_f > hole_thr) | (sx > fray)
    if prm.get("taper"):
        # side panels narrow towards the shoulder
        cut |= sx > 0.55 + 0.45 * smoothstep(0.0, 0.35, v)
    # ragged glowing hem: a violet ember line along the torn edge (exact texel width), dimmer around holes
    dh = tex_dist(ctx, np.maximum(hem - v, 0.0))
    hem_glow = (dh < 1.7) & ~cut & (v > 0.6)
    hem_hot = (dh < 0.7) & ~cut & (v > 0.6)
    rgb[hem_glow] = sramp(VIO, np.full(hem_glow.sum(), 0.55))
    rgb[hem_hot] = VIO[7]
    near = (holes_f > hole_thr - 0.008) & ~cut & (v > 0.35)
    rgb[near] = sramp(VIO, np.full(near.sum(), 0.35))
    ember = near & (holes_f > hole_thr - 0.004) & (v > 0.5)
    rgb[ember] = VIO[5]
    glow |= ember | hem_glow
    alpha = np.where(cut, 0, 255)
    return rgb, alpha, glow & ~cut


def shade_tabard(ctx):
    """Royal tabard: the void cloth with a recessed central panel bearing a dim violet eye sigil,
    cut to a ragged point and dissolving into stars at the hem."""
    rgb, _, glow = shade_cloak(ctx)
    x, y = plane_xy(ctx)
    ax = np.abs(x)
    panel = ax < 0.34
    rgb[panel] = rgb[panel] * 0.72
    trim = (np.abs(ax - 0.34) < 0.045) & (y > -0.55)
    rgb[trim] = mix(rgb[trim], sramp(VIO, np.full(trim.sum(), 0.3)), 0.7)
    cy = 0.62
    r = np.sqrt((x / 0.27) ** 2 + ((y - cy) / 0.085) ** 2)
    eye = (np.abs(r - 1) < 0.22) & (np.abs(y - cy) < 0.09)
    pupil = (ax < 0.04) & (np.abs(y - cy) < 0.1)
    rays = (np.abs(y - cy) > 0.1) & (np.abs(y - cy) < 0.2) & (np.abs(np.mod((x + 0.3) / 0.15, 1) - 0.5) < 0.18) & (ax < 0.3)
    sig = eye | rays
    rgb[sig] = sramp(VIO, np.full(sig.sum(), 0.42))
    rgb[pupil] = sramp(VIO, np.full(pupil.sum(), 0.62))
    glow = (glow | pupil | eye)
    rag = vnoise(np.c_[x * 9.0, np.zeros(ctx.N), np.zeros(ctx.N)], 1.0, 97)
    point = -1.0 + 0.55 * (1 - ax) ** 1.2
    cut = (y < point + 0.25 * rag) | (fbm(np.c_[x * 3, y * 2, np.ones(ctx.N)], 1.0, 3, 98) > 0.7 - 0.15 * np.clip(-y, 0, 1)) & (y < -0.2)
    return rgb, np.where(cut, 0, 255), glow & ~cut


def shade_halo(ctx):
    """Broken violet halo behind the head: a bold outer ring cut by six gaps, a thin inner ring and
    short rune ticks between them; 6-fold symmetric so a 60 degree turn loops seamlessly."""
    x, y = plane_xy(ctx)
    r = np.sqrt(x * x + y * y)
    a = np.mod(np.arctan2(y, x), TAU / 6)            # angle within one 60 degree sector
    sec = a / (TAU / 6)
    gap = np.abs(sec - 0.5) < 0.1
    ring1 = (np.abs(r - 0.92) < 0.055) & ~gap
    ring2 = (np.abs(r - 0.72) < 0.03) & ~(np.abs(sec - 0.0) < 0.04) & ~(np.abs(sec - 1.0) < 0.04)
    tick = (np.abs(np.mod(sec * 5, 1) - 0.5) < 0.12) & (r > 0.77) & (r < 0.84) & ~gap
    stud = (np.abs(sec - 0.5) < 0.04) & (np.abs(r - 0.92) < 0.07)
    on = ring1 | ring2 | tick | stud
    rgb = np.zeros((ctx.N, 3)) + VIO[4]
    rgb[ring1] = sramp(VIO, 0.62 + 0.25 * (1 - np.abs(r[ring1] - 0.92) / 0.055))
    rgb[stud] = VIO[7]
    return rgb, np.where(on, 255, 0), on


SHADERS = {
    "crystal": _w(lambda c: crystal(c)),
    "crystal_cracked": _w(lambda c: crystal(c, seed=1, cracks=0.55)),
    "crystal_cracked_hi": _w(lambda c: crystal(c, seed=2, cracks=0.85, crack_w=1.15)),
    "frame": _w(lambda c: crystal(c, seed=3, cracks=0.6, cav=True)),
    "belt": _w(lambda c: crystal(c, seed=4, rune_band=True, base=0.25)),
    "bracer": _w(lambda c: crystal(c, seed=6, rune_band=True, cracks=0.35)),
    "shard": lambda c: shade_shard(c),
    "shard_dark": lambda c: shade_shard(c, seed=9, tipcol=0.05, lift=0.06, base=0.25),
    "shard_cracked": lambda c: shade_shard(c, cracks=0.7, seed=2),
    "crown": lambda c: shade_shard(c, core=True, seed=4, tipcol=0.3, lift=0.16, base=0.27, core_pal=MG),
    "claw": shade_claw,
    "head": shade_head,
    "void_wall": shade_void_wall,
    "swirl": shade_swirl,
    "swirl2": shade_swirl2,
    "flare": shade_flare,
    "core": shade_core,
    "cloak": shade_cloak,
    "halo": shade_halo,
    "tabard": lambda c: shade_tabard(c),
}
