"""Geometry helpers shared by the armor set builders (Bedrock coords: y up, front -Z, model right -X)."""
import numpy as np

import armorlib as al


def mirror_rot(rot):
    if rot is None:
        return None
    return [rot[0], -rot[1], -rot[2]]


def cube(bone, origin, size, mat, inflate=0.0, rot=None, pivot=None, **params):
    return bone.cube(origin, size, mat, inflate, pivot if rot is not None else None, rot, **params)


def mirror_cube(origin, size, rot=None, pivot=None):
    o = [-(origin[0] + size[0]), origin[1], origin[2]]
    pv = None if pivot is None else [-pivot[0], pivot[1], pivot[2]]
    return o, mirror_rot(rot), pv


def sym(br, bl, origin, size, mat, inflate=0.0, rot=None, pivot=None, **params):
    """Add a cube to the right-side bone and its mirror to the left-side bone."""
    if rot is not None and pivot is None:
        pivot = [origin[0] + size[0] / 2, origin[1] + size[1] / 2, origin[2] + size[2] / 2]
    a = cube(br, origin, size, mat, inflate, rot, pivot, side=-1, **params)
    o, r, pv = mirror_cube(origin, size, rot, pivot)
    b = cube(bl, o, size, mat, inflate, r, pv, side=1, **params)
    return a, b


def sym_spike(br, bl, base, direction, length, width, mat, **kw):
    a = br.spike(base, direction, length, width, mat, side=-1, **kw)
    b = bl.spike([-base[0], base[1], base[2]], [-direction[0], direction[1], direction[2]], length, width, mat,
                 side=1, **kw)
    return a, b


def boxc(bone, center, size, mat, inflate=0.0, rot=None, pivot=None, **params):
    c = np.asarray(center, dtype=float)
    s = np.asarray(size, dtype=float)
    o = c - s / 2
    if rot is not None and pivot is None:
        pivot = c
    return cube(bone, o.tolist(), s.tolist(), mat, inflate, rot, pivot, **params)


def sym_boxc(br, bl, center, size, mat, inflate=0.0, rot=None, pivot=None, **params):
    c = np.asarray(center, dtype=float)
    s = np.asarray(size, dtype=float)
    o = (c - s / 2).tolist()
    if rot is not None and pivot is None:
        pivot = c.tolist()
    return sym(br, bl, o, s.tolist(), mat, inflate, rot, pivot, **params)


def diamond(bone, center, size, mat, spin=(0, 0, 45), **params):
    """A small cube rotated 45 degrees (gem / star point look)."""
    return boxc(bone, center, size, mat, rot=list(spin), **params)
