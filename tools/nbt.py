"""Minimal NBT writer (big-endian, gzip) for structure templates."""
import gzip
import struct

TAG_END, TAG_BYTE, TAG_SHORT, TAG_INT, TAG_LONG, TAG_FLOAT, TAG_DOUBLE, TAG_BYTE_ARRAY, TAG_STRING, TAG_LIST, TAG_COMPOUND = range(11)


class Int(int):
    pass


class Byte(int):
    pass


def _tag_type(v):
    if isinstance(v, Byte):
        return TAG_BYTE
    if isinstance(v, bool):
        return TAG_BYTE
    if isinstance(v, int):
        return TAG_INT
    if isinstance(v, float):
        return TAG_DOUBLE
    if isinstance(v, str):
        return TAG_STRING
    if isinstance(v, list):
        return TAG_LIST
    if isinstance(v, dict):
        return TAG_COMPOUND
    raise TypeError(type(v))


def _payload(v, out):
    t = _tag_type(v)
    if t == TAG_BYTE:
        out += struct.pack('>b', int(v))
    elif t == TAG_INT:
        out += struct.pack('>i', v)
    elif t == TAG_DOUBLE:
        out += struct.pack('>d', v)
    elif t == TAG_STRING:
        b = v.encode('utf-8')
        out += struct.pack('>H', len(b)) + b
    elif t == TAG_LIST:
        et = _tag_type(v[0]) if v else TAG_END
        out += struct.pack('>bi', et, len(v))
        for e in v:
            _payload(e, out)
    elif t == TAG_COMPOUND:
        for k, e in v.items():
            kb = k.encode('utf-8')
            out += struct.pack('>bH', _tag_type(e), len(kb)) + kb
            _payload(e, out)
        out += b'\x00'


def write(path, root):
    out = bytearray()
    out += struct.pack('>bH', TAG_COMPOUND, 0)
    _payload(root, out)
    with gzip.open(path, 'wb') as f:
        f.write(bytes(out))


def structure(size, palette, blocks, data_version=3955):
    """palette: list of {'Name': ..., 'Properties': {...}}; blocks: list of (x, y, z, palette_index[, nbt])."""
    bl = []
    for b in blocks:
        e = {'pos': [b[0], b[1], b[2]], 'state': b[3]}
        if len(b) > 4 and b[4]:
            e['nbt'] = b[4]
        bl.append(e)
    return {'DataVersion': data_version, 'size': list(size), 'palette': palette, 'blocks': bl, 'entities': []}
