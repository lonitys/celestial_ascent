"""Materials for nebula_leviathan: overlapping nebula fish-scales, armoured head plates, pale ventral
scutes, star-speckled fin membranes with a thin edge light, horn, teeth, the glowing maw and eyes.

Every shader returns (rgb (N,3), alpha, glow). Colour is built from a value term (scales, light, AO)
mapped through blue / violet / magenta ramps that are mixed by domain-warped 3D nebula noise evaluated
on the rest-pose world position, so the colour clouds flow continuously along the whole serpent.
"""
import numpy as np

from bosslib import fbm, hash3, palette, worley
from bossfx import bevel, dither, mix, smoothstep, sramp, stars

# ----------------------------------------------------------------------------- palettes (dark -> light)
P_BLUE = palette("#03040c", "#070c22", "#0c173d", "#12285e", "#1a3c80", "#2656a3", "#3a74c2", "#6198dc", "#9cc3f0")
P_VIOLET = palette("#05030c", "#100824", "#1d0f40", "#2f185e", "#45237f", "#5e31a0", "#7c48bf", "#a06ed8", "#c9a2ee")
P_MAGENTA = palette("#0b030b", "#200822", "#380e3e", "#54165a", "#74207a", "#962f9a", "#b649b4", "#d377cc", "#eeaee6")
P_BELLY = palette("#141228", "#211e40", "#302c5a", "#433e78", "#5a5495", "#746fb0", "#918cc9", "#b2aedf", "#d6d4f2")
P_HORN = palette("#07050f", "#120b24", "#1f1340", "#2f1d5c", "#432a78", "#5b3b94", "#7756ae", "#9879c6", "#bba3dc", "#ddcdf0")
P_TOOTH = palette("#2a2236", "#4e4560", "#7a718a", "#a8a0b2", "#cfc9d6", "#ebe7ee", "#fffcf8")
P_MAW = palette("#2a0630", "#4d0c58", "#761780", "#a026a6", "#c43fc4", "#e066da", "#f39cec", "#ffd2f8", "#ffffff")
P_EYE = palette("#03202b", "#074457", "#0d6f84", "#1a9fb0", "#3fcbd6", "#86ecef", "#cbfffb", "#ffffff")
P_EDGE = palette("#2c3c94", "#4a66c8", "#7393e6", "#a3c0fa", "#d9e7ff")
STAR = np.array([236.0, 228.0, 255.0])


def tone(ctx, up=0.07, down=0.14, ao=0.5):
    """Up faces brighter, down faces darker, baked AO."""
    n = ctx.nw
    return up * max(0.0, float(n[1])) - down * max(0.0, float(-n[1])) - ctx.ao * ao


def warp(q, amt=20.0):
    w = np.stack([fbm(q, 0.028, 2, 761), fbm(q, 0.028, 2, 767), fbm(q, 0.028, 2, 773)], axis=1) - 0.5
    return q + w * amt


def nebula_fields(ctx, q=None):
    """(violet weight, cloud density, magenta weight): a designed head -> tail gradient (indigo-blue
    head, violet body, magenta-violet tail) broken up by domain-warped noise on the rest pose."""
    q = ctx.pw if q is None else q
    qw = warp(q)
    g = np.clip((q[:, 2] + 30.0) / 145.0, 0, 1)
    hue = fbm(qw * np.array([1.0, 1.25, 0.42]), 0.034, 3, 701)
    cloud = fbm(qw * np.array([1.0, 1.0, 0.66]), 0.07, 4, 709)
    hb = smoothstep(0.2, 0.8, 0.36 + 0.55 * g + (hue - 0.5) * 1.2)
    mg = smoothstep(0.52, 0.7, cloud + 0.18 * g) * np.clip(1.2 - np.abs(hb - 0.7) * 1.6, 0, 1) * (0.45 + 0.5 * g)
    return hb, cloud, mg


def nebula_colour(v, hb, mg):
    rgb = mix(sramp(P_BLUE, v), sramp(P_VIOLET, v), hb)
    return mix(rgb, sramp(P_MAGENTA, v + 0.04), mg)


def dust(q, seed=719):
    """Ridged dark dust lanes (0..1)."""
    t = np.abs(fbm(warp(q, 10.0) * np.array([1.0, 1.0, 0.55]), 0.08, 3, seed) - 0.5)
    return 1 - smoothstep(0.008, 0.03, t)


def stars2d(x, y, scale=0.8, density=0.03, seed=0):
    """Star field on 2D plane coordinates (model units). Returns (brightness 0..1, sparkle mask)."""
    qx, qy = np.asarray(x) * scale, np.asarray(y) * scale
    ix, iy = np.floor(qx), np.floor(qy)
    z = np.zeros_like(ix)
    h = hash3(ix, iy, z, seed)
    on = h < density
    cx = hash3(ix, iy, z + 1, seed + 1) * 0.6 + 0.2
    cy = hash3(ix, iy, z + 2, seed + 2) * 0.6 + 0.2
    dx, dy = qx - ix - cx, qy - iy - cy
    d = np.sqrt(dx * dx + dy * dy)
    size = 0.2 + 0.34 * (h / max(density, 1e-6))
    b = np.where(on, np.clip(1 - d / size, 0, 1), 0.0)
    big = on & (h < density * 0.16)
    spark = big & (((np.abs(dx) < 0.09) & (np.abs(dy) < 0.8)) | ((np.abs(dy) < 0.09) & (np.abs(dx) < 0.8)))
    return b, spark


def add_stars(ctx, rgb, b, thresh=0.25, glow_t=0.6):
    on = b > thresh
    if on.any():
        rgb[on] = mix(rgb[on], np.broadcast_to(STAR, (int(on.sum()), 3)), np.clip(b[on] * 1.5, 0, 1))
    return b > glow_t


# ----------------------------------------------------------------------------- surface coordinates


def around_coords(ctx):
    """(u, v): u along the body axis (+Z, towards the tail), v around the cross-section measured from
    the bottom of the side faces (mirrored left/right so scale rows are bilaterally symmetric)."""
    lo, hi, p = ctx.lo, ctx.hi, ctx.p
    W, H = hi[0] - lo[0], hi[1] - lo[1]
    cx = (lo[0] + hi[0]) / 2
    ax = np.abs(p[:, 0] - cx)
    f = ctx.face
    if f in ("east", "west"):
        return p[:, 2], p[:, 1] - lo[1]
    if f == "up":
        return p[:, 2], H + (W / 2 - ax)
    if f == "down":
        return p[:, 2], -(W / 2 - ax)
    return -p[:, 1] * 1.0, ax  # caps


def fish_scales(u, v, P, seed=0):
    """Overlapping fish scales: rings of scales around the body (ring spacing along u = 0.5 P, scale
    spacing around v = P, alternate rings offset by half a scale). The ring nearer the head (smaller u)
    lies on top, so each scale shows its rounded rear margin. Returns du, dv (normalised to the radius),
    d, shadow (0..1 cast by the scale in front) and a per-scale id hash."""
    Pu, Pv, R = P * 0.5, P, P * 0.56
    c0 = np.floor(u / Pu)
    cands = []
    for dc in (-1, 0, 1):
        c = c0 + dc
        off = np.mod(c, 2) * 0.5 * Pv
        r0 = np.floor((v - off) / Pv)
        for dr in (-1, 0, 1):
            r = r0 + dr
            cu = (c + 0.5) * Pu
            cv = (r + 0.5) * Pv + off
            du = (u - cu) / R
            dv = (v - cv) / R
            cands.append((cu, du, dv, np.sqrt(du * du + dv * dv), c, r))
    CU = np.stack([c[0] for c in cands])
    D = np.stack([c[3] for c in cands])
    key = np.where(D < 1.0, CU + 1e-3 * D, np.inf)      # same ring: the nearer centre wins
    own = np.argmin(key, axis=0)
    idx = np.arange(len(u))
    cu_o = CU[own, idx]
    du = np.stack([c[1] for c in cands])[own, idx]
    dv = np.stack([c[2] for c in cands])[own, idx]
    d = D[own, idx]
    cc = np.stack([c[4] for c in cands])[own, idx]
    rr = np.stack([c[5] for c in cands])[own, idx]
    dant = np.where(CU < cu_o[None, :] - 1e-6, D, np.inf).min(axis=0)
    # distances in model units: to the own rim and to the edge of the covering scale in front
    rim_u = (1 - d) * R
    sh_u = (dant - 1.0) * R
    sid = hash3(cc, rr, np.zeros_like(cc), seed)
    return dict(du=du, dv=dv, d=d, rim_u=rim_u, sh_u=sh_u, id=sid)


def roundness(ctx):
    """Fake a rounded cross-section on boxes: a lit band high on the sides, darker lower sides,
    top face darkening towards its long edges."""
    f = ctx.face
    if f in ("east", "west"):
        t = ctx.t
        return 0.08 * np.exp(-((t - 0.28) / 0.2) ** 2) - 0.13 * smoothstep(0.6, 1.0, t)
    if f == "up":
        x = np.abs(ctx.s - 0.5) * 2
        return 0.05 - 0.1 * x ** 2
    if f == "down":
        return -0.04
    return 0.0


# ----------------------------------------------------------------------------- body materials


def scales(ctx, P=None, dark=0.0, star_density=0.004, seed=0):
    P = P or ctx.params.get("P", 3.6)
    u, v = around_coords(ctx)
    sc = fish_scales(u, v, P, seed + ctx.index * 3)
    rim_u, sh_u, du, dv = sc["rim_u"], sc["sh_u"], sc["du"], sc["dv"]
    # clean scale relief: per-scale tint, gentle bulge towards the free margin, dark rim line,
    # a lit band just inside the rim (upper half), and the shadow cast by the scale in front
    outline = rim_u < 0.5
    lit = (rim_u >= 0.5) & (rim_u < 1.0) & (dv > -0.35)
    rel = (sc["id"] - 0.5) * 0.08 + 0.1 * np.clip(du, -0.3, 1.0) - 0.24 * outline + 0.1 * lit - 0.13 * (sh_u < 0.5)
    q = ctx.pw
    hb, cloud, mg = nebula_fields(ctx)
    lum = 0.11 * np.clip((cloud - 0.5) / 0.12, -1, 1) + 0.17 * smoothstep(0.56, 0.72, cloud) - dust(q) * 0.1
    val = 0.42 + rel + lum - dark + roundness(ctx) + tone(ctx) + bevel(ctx, 1.4, 0.04, 0.07)
    rgb = nebula_colour(val, hb, mg)
    sheen = lit & (sc["id"] > 0.3)
    rgb[sheen] = mix(rgb[sheen], sramp(P_EDGE, np.clip(val[sheen] + 0.12, 0, 1)), 0.28)
    glow = np.zeros(ctx.N, dtype=bool)
    if star_density > 0 and ctx.face != "down":
        glow |= add_stars(ctx, rgb, stars(q, 1.0, star_density, 733 + seed), 0.35, 0.65)
    return rgb, 255, glow


def head_plates(ctx):
    """Armoured head: large symmetric scutes (worley cells mirrored about the midline, evaluated in 3D
    so they run continuously over the faces); the down faces inside the mouth are the glowing palate."""
    if ctx.face == "down" and ctx.params.get("palate"):
        return maw(ctx, base=0.5)
    pw = ctx.pw
    q = np.c_[np.abs(pw[:, 0]), pw[:, 1], pw[:, 2]]
    f1, f2, cid = worley(q * np.array([1.0, 1.1, 0.8]), ctx.params.get("plate_f", 0.3), 911)
    e = f2 - f1
    seam = e < 0.075
    hb, cloud, mg = nebula_fields(ctx)
    v = 0.43 + (cid - 0.5) * 0.08 + 0.1 * np.clip((cloud - 0.5) / 0.12, -1, 1) + 0.12 * smoothstep(0.56, 0.72, cloud) + 0.14 * np.clip(e, 0, 0.6) - seam * 0.24
    v = v + tone(ctx) + bevel(ctx, 1.4, 0.06, 0.1) + roundness(ctx) + dither(ctx, 0.015)
    rgb = nebula_colour(v, hb, mg * 0.6)
    rim = (e > 0.075) & (e < 0.14)
    rgb[rim] = mix(rgb[rim], sramp(P_EDGE, np.clip(v[rim] + 0.12, 0, 1)), 0.22)
    return rgb, 255, np.zeros(ctx.N, dtype=bool)


def belly(ctx, Pb=None, glow_seams=False):
    """Pale ventral scutes: transverse plates with a lit front lip and a dark overlap line behind."""
    Pb = Pb or ctx.params.get("Pb", 1.8)
    p = ctx.p
    u = p[:, 2]
    if ctx.face in ("north", "south"):
        u = p[:, 1] * 1.3
    f = np.mod(u / Pb, 1.0)
    pid = np.floor(u / Pb)
    W = ctx.hi[0] - ctx.lo[0]
    cx = (ctx.hi[0] + ctx.lo[0]) / 2
    ax = np.abs(p[:, 0] - cx) / max(W / 2, 1e-6)
    v = 0.5 + 0.14 * f - 0.24 * (f > 0.84) + 0.08 * (f < 0.12) - 0.12 * ax ** 2
    v = v + (hash3(pid, np.full(ctx.N, ctx.index), pid * 0, 951) - 0.5) * 0.05
    v = v + (fbm(ctx.pw, 0.08, 3, 953) - 0.5) * 0.18 + tone(ctx, 0.05, 0.05, 0.45) + dither(ctx, 0.025)
    if ctx.face in ("east", "west"):
        v = v - 0.08
    rgb = sramp(P_BELLY, v)
    hb, cloud, mg = nebula_fields(ctx)
    rgb = mix(rgb, nebula_colour(v + 0.05, hb, mg), 0.3)
    glow = np.zeros(ctx.N, dtype=bool)
    if glow_seams:
        seam = (f > 0.86) & (ax < 0.88)
        if ctx.face in ("east", "west"):
            seam &= ctx.t < 0.85
        rgb[seam] = sramp(P_MAW, 0.4 + 0.18 * (1 - ax[seam]))
        glow |= seam
    return rgb, 255, glow


# ----------------------------------------------------------------------------- head features


def maw(ctx, base=0.55):
    """Glowing mouth interior: dark magenta at the lips, white-hot deep in the throat, with transverse
    palate ridges (dark grooves) and darker sides so the open mouth reads as a deep cavity."""
    p = ctx.p
    W = ctx.hi[0] - ctx.lo[0]
    cx = (ctx.hi[0] + ctx.lo[0]) / 2
    ax = np.abs(p[:, 0] - cx) / max(W / 2, 1e-6)
    z0, z1 = ctx.params.get("maw_z", (ctx.lo[2], ctx.hi[2]))
    deep = np.clip((p[:, 2] - z0) / max(z1 - z0, 1e-6), 0, 1)
    groove = np.mod(p[:, 2], 2.2) < 0.55
    v = base - 0.28 + 0.62 * deep ** 1.3 - 0.32 * ax ** 2.2 - groove * 0.12 * (1 - deep)
    v = v + (fbm(p, 0.4, 2, 961) - 0.5) * 0.08
    return sramp(P_MAW, v + dither(ctx, 0.03)), 255, np.ones(ctx.N, dtype=bool)


def tongue(ctx):
    """Jaw: scaled sides with a dim glowing lip line, glowing tongue on top, glowing gular seams below."""
    f = ctx.face
    if f == "up":
        p = ctx.p
        W = ctx.hi[0] - ctx.lo[0]
        cx = (ctx.hi[0] + ctx.lo[0]) / 2
        x = (p[:, 0] - cx) / (W / 2)
        z0, z1 = ctx.params.get("tongue_z", (ctx.lo[2], ctx.hi[2]))
        fr = np.clip((p[:, 2] - z0) / (z1 - z0), 0, 1)   # 0 = front tip, 1 = back
        tw = 0.34 * (0.4 + 0.6 * fr)
        fork = (fr < 0.2) & (np.abs(x) < 0.1 + (0.2 - fr) * 0.7) & (np.abs(x) > (0.2 - fr) * 0.6)
        tng = ((np.abs(x) < tw) & (fr > 0.18)) | fork
        v = 0.3 + 0.5 * fr ** 1.3 - 0.3 * np.abs(x) ** 2.2
        v = np.where(tng, 0.2 + 0.32 * fr - 0.1 * (np.abs(x) / np.maximum(tw, 1e-3)) ** 2, v)
        groove = tng & (np.abs(x) < 0.06) & (fr > 0.22)
        v = v - groove * 0.1
        return sramp(P_MAW, v + dither(ctx, 0.04)), 255, np.ones(ctx.N, dtype=bool)
    if f == "down":
        return belly(ctx, Pb=1.5, glow_seams=True)
    rgb, a, glow = head_plates(ctx)
    if f in ("east", "west"):
        lip = ctx.j < 1
        rgb[lip] = sramp(P_MAW, np.full(int(lip.sum()), 0.5))
        glow = glow | lip
    return rgb, a, glow


def eye(ctx):
    """Almond eye on the outward face (west for the right eye, east for the left): icy cyan iris with
    a dark slit pupil and a dark lid rim; other faces are the dark socket."""
    side = ctx.params.get("side", 1)
    outward = "east" if side > 0 else "west"
    if ctx.face != outward:
        v = 0.14 + tone(ctx) * 0.5 + dither(ctx, 0.03)
        return sramp(P_VIOLET, v), 255, np.zeros(ctx.N, dtype=bool)
    front = ctx.s if outward == "west" else 1 - ctx.s       # 1 at the front corner
    x = (0.5 - front) * 2                                   # -1 front .. 1 back
    y = (0.5 - ctx.t) * 2
    yc = 0.25 * x                                           # slanted: the back corner is higher
    half = 0.98 * np.clip(1 - x * x, 0, 1) ** 0.5
    inside = np.abs(y - yc) < half
    r = np.sqrt((x * 0.8) ** 2 + ((y - yc) * 1.2) ** 2)
    v = 0.95 - 0.4 * r + 0.06 * np.cos(np.arctan2(y - yc, x) * 9) * (r > 0.3)
    rgb = sramp(P_EYE, v + dither(ctx, 0.03))
    glow = inside.copy()
    pupil = inside & (np.abs(x + 0.02) < 0.1 * np.clip(1 - ((y - yc) / 0.95) ** 2, 0, 1) + 0.03) & (np.abs(y - yc) < 0.8)
    rgb[pupil] = np.array([10, 4, 24])
    glow &= ~pupil
    hl = inside & (np.sqrt((x + 0.42) ** 2 + (y - yc - 0.32) ** 2) < 0.15)
    rgb[hl] = np.array([255, 255, 255])
    lid = ~inside
    rgb[lid] = sramp(P_VIOLET, 0.1 + 0.08 * (y[lid] > yc[lid]) + dither(ctx, 0.03)[lid])
    return rgb, 255, glow


def horn(ctx):
    """Curved horn: near-black violet root fading to a pale starlit tip, with growth rings."""
    pr0 = ctx.params.get("curve_prog0", 0.0)
    pr1 = ctx.params.get("curve_prog1", 1.0)
    lo, hi = ctx.lo, ctx.hi
    fy = np.clip((ctx.p[:, 1] - lo[1]) / max(hi[1] - lo[1], 1e-6), 0, 1)
    prog = pr0 + (pr1 - pr0) * fy
    if ctx.face in ("up", "down"):
        prog = np.full(ctx.N, pr1 if ctx.face == "up" else pr0)
    ring = np.mod(prog * 10.0, 1.0) < 0.2
    side = {"east": 0.05, "north": 0.04, "west": -0.05, "south": -0.04}.get(ctx.face, 0.0)
    v = 0.12 + 0.82 * prog ** 1.4 - ring * 0.08 * (1 - prog) + side + tone(ctx, 0.04, 0.06, 0.3)
    v = v + bevel(ctx, 1.2, 0.07, 0.07) + (fbm(ctx.p, 0.6, 2, 971) - 0.5) * 0.06 + dither(ctx, 0.02)
    rgb = sramp(P_HORN, v)
    rgb = mix(rgb, sramp(P_VIOLET, v + 0.05), 0.35 * (1 - prog))
    return rgb, 255, np.zeros(ctx.N, dtype=bool)


def teeth(ctx):
    """Row of cutout teeth on a plane; params: down (teeth hang from the top edge), fangs = plane-x
    positions (units) of big fangs, tw = tooth width (units), only_fangs."""
    w = ctx.tw / 2.0
    h = ctx.th / 2.0
    x = ctx.s * w
    down = ctx.params.get("down", True)
    y = ctx.t * h if down else (1 - ctx.t) * h          # distance from the gum line
    TW = ctx.params.get("tw", 1.5)
    k = np.floor(x / TW)
    fx = x / TW - k
    L = h * (0.45 + 0.2 * hash3(k, k * 0 + ctx.index, k * 0, 981))
    tooth = y < L * np.clip(1 - np.abs(2 * fx - 1), 0, 1) ** 0.9
    if ctx.params.get("only_fangs"):
        tooth[:] = False
    for fp in ctx.params.get("fangs", []):
        fw = ctx.params.get("fang_w", 1.3)
        fxx = (x - fp) / fw
        tooth |= (np.abs(fxx) < 1) & (y < h * np.clip(1 - np.abs(fxx), 0, 1) ** 0.7)
    v = 0.86 - 0.3 * np.clip(1 - y / h, 0, 1) ** 4 + 0.06 * (y / h) - 0.1 * np.abs(2 * fx - 1)
    rgb = sramp(P_TOOTH, v + dither(ctx, 0.03))
    return rgb, np.where(tooth, 255, 0), np.zeros(ctx.N, dtype=bool)


# ----------------------------------------------------------------------------- membranes (planes)


def _membrane_colour(ctx, x, y, inside, ray, edge, radial, seed=0, star_d=0.045):
    q = ctx.pw
    hb, cloud, mg = nebula_fields(ctx)
    v = 0.18 + 0.2 * radial + (cloud - 0.5) * 0.4 + dither(ctx, 0.025)
    rgb = mix(nebula_colour(v, hb, mg), sramp(P_BLUE, v + 0.05), 0.35 * smoothstep(0.4, 1.0, radial))
    glow = np.zeros(ctx.N, dtype=bool)
    if ray.any():
        rgb[ray] = mix(sramp(P_VIOLET, 0.36 + 0.14 * radial[ray]), sramp(P_HORN, 0.4 + 0.2 * radial[ray]), 0.35)
    b, spark = stars2d(x, y, 0.85, star_d, 811 + seed + ctx.index)
    b = np.where(ray, 0, b)
    glow |= add_stars(ctx, rgb, b, 0.22, 0.52)
    sp = spark & inside & ~ray
    rgb[sp] = mix(rgb[sp], np.broadcast_to(STAR, (int(sp.sum()), 3)), 0.7)
    glow |= sp
    if edge.any():
        rgb[edge] = sramp(P_EDGE, 0.2 + 0.2 * radial[edge])
        glow |= edge
    return rgb, glow


def constellation(ctx, x, y, inside, pts, line_w=0.26, star_r=0.62):
    """Faint constellation figure: star points (plane units) joined in order by thin lines.
    Returns (line mask, star mask) limited to the inside of the shape."""
    from bosslib import seg_dist
    line = np.zeros(ctx.N, dtype=bool)
    star = np.zeros(ctx.N, dtype=bool)
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        line |= seg_dist(x, y, ax, ay, bx, by) < line_w
    for (px, py) in pts:
        star |= (x - px) ** 2 + (y - py) ** 2 < star_r ** 2
    return line & inside & ~star, star & inside


def _polar_fin(ctx, x, y, phis, rmax_fn, scallop=0.1, spine=0.0, edge_w=0.55, seed=0, ray_w=0.3, figure=None):
    """Generic fan-shaped fin around the origin (x, y in units). phis = ray angles (radians);
    rmax_fn(phi) = boundary radius before scalloping. Rays run from the root to each phi and may
    poke out past the membrane by `spine` (fraction)."""
    r = np.sqrt(x * x + y * y)
    a = np.arctan2(y, x)
    phis = np.asarray(phis, dtype=float)
    lo, hi = phis.min(), phis.max()
    dphi = (hi - lo) / max(len(phis) - 1, 1)
    fpos = (a - lo) / dphi
    frac = fpos - np.floor(fpos)
    rb = rmax_fn(np.clip(a, lo, hi)) * (1 - scallop * np.sin(np.pi * frac) ** 0.8)
    within = (a >= lo - 0.02) & (a <= hi + 0.02)
    mem = within & (r < rb)
    k = np.clip(np.round(fpos), 0, len(phis) - 1)
    ak = lo + k * dphi
    perp = np.abs(r * np.sin(a - ak))
    along = r * np.cos(a - ak)
    rk = rmax_fn(ak) * (1 + spine)
    taper = ray_w * (1 - 0.6 * np.clip(along / np.maximum(rk, 1e-3), 0, 1))
    ray = (perp < np.maximum(taper, 0.22)) & (along > 0) & (along < rk)
    inside = mem | ray
    edge = mem & (r > rb - edge_w)
    ray = ray & ~edge
    radial = np.clip(r / np.maximum(rmax_fn(np.clip(a, lo, hi)), 1e-3), 0, 1)
    rgb, glow = _membrane_colour(ctx, x, y, inside, ray & inside, edge, radial, seed)
    if figure:
        # figure = [(phi_deg, radial_frac), ...] placed in the fin's own polar frame
        pts = []
        for fd, fr in figure:
            fa = np.radians(fd)
            rr = float(rmax_fn(np.array([fa]))[0]) * fr
            pts.append((rr * np.cos(fa), rr * np.sin(fa)))
        ln, st = constellation(ctx, x, y, inside & ~edge, pts)
        rgb[ln] = mix(rgb[ln], sramp(P_EDGE, np.full(int(ln.sum()), 0.5)), 0.55)
        rgb[st] = np.array([240.0, 236.0, 255.0])
        glow |= st | ln
    return rgb, np.where(inside, 255, 0), glow & inside


def fin(ctx):
    kind = ctx.params.get("kind", "pectoral")
    w = ctx.tw / 2.0
    h = ctx.th / 2.0
    s, t = ctx.s, ctx.t
    if kind == "dorsal":
        # sail along the back: s runs head -> tail, t down; profile from h0 (front) to h1 (back)
        x = s * w
        y = (1 - t) * h
        h0, h1 = ctx.params.get("h0", h), ctx.params.get("h1", h)
        SP = ctx.params.get("sp", 3.0)
        prof = h0 + (h1 - h0) * np.clip(x / w, 0, 1)
        xs = x + ctx.params.get("xoff", 0.0) - y * 0.6          # raked-back spine coordinate
        fr = np.mod(xs / SP, 1.0)
        edge_y = prof * (0.95 - 0.13 * np.sin(np.pi * fr) ** 0.8)
        mem = y < edge_y
        sd = np.minimum(fr, 1 - fr) * SP
        yy = np.clip(y / np.maximum(prof, 1e-3), 0, 1)
        spine = (sd < 0.3 * (1 - 0.5 * yy) + 0.08) & (y < prof * 1.0)
        inside = mem | spine
        edge = mem & (y > edge_y - 0.55)
        spine = spine & ~edge
        radial = yy
        rgb, glow = _membrane_colour(ctx, x + ctx.params.get("xoff", 0.0), y, inside, spine & inside, edge,
                                     radial, seed=3, star_d=0.035)
        return rgb, np.where(inside, 255, 0), glow & inside
    if kind == "pectoral":
        # root at the top-left corner; s outward along the leading edge, t backwards
        x = s * w
        y = t * h
        phis = np.radians(np.linspace(3, 86, 10))
        R = ctx.params.get("R", w)

        def rmax(a):
            f = np.clip((a - phis[0]) / (phis[-1] - phis[0]), 0, 1)
            return R * (1.0 - 0.55 * f ** 0.85)
        fig = [(14, 0.78), (24, 0.52), (40, 0.62), (58, 0.42), (70, 0.66)] if ctx.params.get("figure", True) else None
        return _polar_fin(ctx, x, y, phis, rmax, scallop=0.09, spine=0.03, seed=11, figure=fig)
    if kind == "frill":
        x = s * w
        y = (0.5 - t) * h
        phis = np.radians(np.linspace(-62, 62, 7))
        R = w / 1.12

        def rmax(a):
            return R * (0.62 + 0.38 * np.cos(a * 1.1)) * (1 - 0.06 * (a > 0))
        return _polar_fin(ctx, x, y, phis, rmax, scallop=0.15, spine=0.07, seed=21, ray_w=0.34)
    if kind == "fan":
        # small vertical crest: upper lobe tall, lower lobe short
        x = s * w
        y = (0.5 - t) * h
        phis = np.radians(np.linspace(-34, 50, 8))
        R = w / 1.04

        def rmax(a):
            f = np.clip((a + np.radians(34)) / np.radians(84), 0, 1)
            return R * (0.42 + 0.58 * f ** 1.6)
        return _polar_fin(ctx, x, y, phis, rmax, scallop=0.1, spine=0.04, seed=31)
    if kind == "fluke":
        # main horizontal swallowtail: two long lobes, short notched middle
        x = s * w
        y = (0.5 - t) * h
        phis = np.radians(np.linspace(-50, 50, 13))
        R = w / 1.04

        def rmax(a):
            f = np.abs(a) / np.radians(50)
            return R * (0.34 + 0.66 * f ** 1.8)
        return _polar_fin(ctx, x, y, phis, rmax, scallop=0.08, spine=0.03, seed=41,
                          figure=[(-40, 0.72), (-22, 0.5), (0, 0.28), (20, 0.48), (38, 0.7), (44, 0.88)])
    if kind == "whisker":
        x = s * w
        y = (0.5 - t) * h
        f = np.clip(x / w, 0, 1)
        amp = ctx.params.get("amp", 2.2)
        ph = ctx.params.get("ph", 0.0)
        yc = amp * np.sin(f * 2.2 * np.pi + ph) * f ** 0.7 - 0.8 * f ** 2
        th = 1.7 * (1 - f) + 0.55
        dy = y - yc
        inside = (np.abs(dy) < th / 2) & (x < w * 0.985)
        v = 0.32 + 0.4 * f + 0.12 * (dy > 0) + dither(ctx, 0.025)
        rgb = mix(sramp(P_VIOLET, v + 0.08), sramp(P_HORN, v + 0.05), 0.3 + 0.4 * f)
        tip = inside & (f > 0.9)
        bead = inside & (np.abs(np.mod(x, 4.0) - 2.0) < 0.4) & (f > 0.3) & (f < 0.88)
        rgb[bead] = sramp(P_EDGE, np.full(int(bead.sum()), 0.5))
        rgb[tip] = sramp(P_EYE, 0.55 + 0.35 * (f[tip] - 0.9) / 0.1)
        return rgb, np.where(inside, 255, 0), tip | bead
    raise ValueError(kind)


# ----------------------------------------------------------------------------- evolution stage parts


def _spike_prog(ctx):
    """0 at the base of a spike / curve_spike, 1 at its tip (per texel)."""
    prm = ctx.params
    loc = ctx.p[:, 1] - ctx.lo[1]
    if "curve_prog0" in prm:
        f = np.clip(loc / max(prm["spike_len"], 1e-6), 0, 1)
        prog = prm["curve_prog0"] + (prm["curve_prog1"] - prm["curve_prog0"]) * f
    elif "spike_len" in prm:
        prog = np.clip((prm["spike_y0"] + loc) / prm["spike_len"], 0, 1)
    else:
        prog = np.clip(1 - ctx.t, 0, 1)
    if ctx.face == "up":
        prog = np.full(ctx.N, float(prog.max()))
    elif ctx.face == "down":
        prog = np.full(ctx.N, float(prog.min()))
    return prog


def spine(ctx):
    """Stage spines and crown spikes: dark violet crystal (the horn ramp) growing paler towards the
    tip, with a glowing magenta core running up each face and a white-hot starlit tip."""
    prog = _spike_prog(ctx)
    side = {"east": 0.05, "north": 0.04, "west": -0.05, "south": -0.04}.get(ctx.face, 0.0)
    v = 0.14 + 0.62 * prog ** 1.3 + side + tone(ctx, 0.04, 0.06, 0.3)
    v = v + bevel(ctx, 1.2, 0.08, 0.08) + (fbm(ctx.p, 0.6, 2, 991) - 0.5) * 0.06 + dither(ctx, 0.02)
    rgb = mix(sramp(P_HORN, v), sramp(P_VIOLET, v + 0.05), 0.3 * (1 - prog))
    glow = np.zeros(ctx.N, dtype=bool)
    last = ctx.params.get("seg", 0) == ctx.params.get("nseg", 1) - 1
    if ctx.face not in ("up", "down"):
        w = np.abs(ctx.s - 0.5) * 2
        k = np.clip(1 - w / (0.46 - 0.2 * prog), 0, 1) * smoothstep(0.04, 0.2, prog)
        rgb = mix(rgb, sramp(P_MAW, 0.3 + 0.25 * k), np.clip(k * 1.4, 0, 1) * 0.55)
        core = k > 0.3
        rgb[core] = sramp(P_MAW, 0.48 + 0.3 * k[core] + 0.18 * prog[core])
        glow |= core
        tip = last & (prog > 0.9)
        rgb[tip] = sramp(P_EDGE, 0.42 + 0.3 * (prog[tip] - 0.9) / 0.1)
        glow |= tip
    elif ctx.face == "up" and last:
        rgb = sramp(P_EDGE, np.full(ctx.N, 0.6))
        glow |= True
    return rgb, 255, glow


def orb(ctx):
    """Stage 3 nebula orb set into the flank: each face shows a round glowing orb (corners cut away so
    the box reads rounded) with a swirling magenta-violet nebula, pin stars and a white-hot heart,
    ringed by a dark violet socket rim."""
    x, y = (ctx.s - 0.5) * 2, (0.5 - ctx.t) * 2
    r = np.sqrt(x * x + y * y)
    a = np.arctan2(y, x)
    sw = fbm(np.c_[np.cos(a + 2.2 * r) * r * 3, np.sin(a + 2.2 * r) * r * 3, np.full(ctx.N, ctx.index * 1.7)], 1.0, 3, 997)
    v = 0.98 - 0.5 * r + (sw - 0.5) * 0.45
    hb = np.clip(0.5 + (sw - 0.5) * 1.6, 0, 1)
    rgb = mix(sramp(P_MAGENTA, v), sramp(P_VIOLET, v + 0.06), hb)
    heart = r < 0.32
    rgb[heart] = sramp(P_MAW, 0.82 + 0.18 * (1 - r[heart] / 0.32))
    st = (hash3(ctx.i, ctx.j, np.full(ctx.N, ctx.index), 1001) < 0.06) & (r < 0.85) & ~heart
    rgb[st] = STAR
    rim = r > 0.9
    rgb[rim] = sramp(P_VIOLET, 0.16 + 0.08 * (r[rim] < 1.0) + dither(ctx, 0.03)[rim])
    inside = r < 1.22
    return rgb, np.where(inside, 255, 0), inside & ~rim


# ----------------------------------------------------------------------------- shader table


def _sh(fn, **kw):
    def s(ctx):
        return fn(ctx, **kw)
    return s


SHADERS = {
    "scales": scales,
    "scales_plain": _sh(scales),
    "ridge": _sh(scales, dark=0.06, star_density=0.01, seed=17),
    "head": head_plates,
    "belly": belly,
    "throat": _sh(belly, glow_seams=True),
    "maw": maw,
    "maw_deep": _sh(maw, base=0.72),
    "jaw": tongue,
    "eye": eye,
    "horn": horn,
    "teeth": teeth,
    "fin": fin,
    # evolution stages
    "spine": spine,
    "orb": orb,
}
