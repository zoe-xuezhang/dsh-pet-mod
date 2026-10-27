# -*- coding: utf-8 -*-
import struct, marshal, zlib, shutil, os, sys

SRC_EXE = r'D:/dshpet/dsh-pet-standalone-webm-chat.exe'
BAK_EXE = r'D:/dshpet/dsh-pet-standalone-webm-chat.exe.orig'
PYZ_ABS   = 759811
ARCH      = 728064
TOC_ABS   = 16420555
TOC_LEN   = 640
COOKIE    = 16421195
PYZ_TOC_ENTRY_REL = 608   # 16421163 - 16420555

def build_new_pyz(old_pyz, new_fn_code):
    tocoff = struct.unpack('!i', old_pyz[8:12])[0]
    toc = marshal.loads(old_pyz[tocoff:])
    header = old_pyz[:12]
    body = bytearray(b'\x00' * 5)   # 保留原 5 字节对齐空隙
    new_toc = []
    patched = 0
    for name, (typ, off, ln) in toc:
        raw = old_pyz[off:off+ln]
        if name == 'pet.context_menus.shared':
            mod = marshal.loads(zlib.decompress(raw))
            consts = []
            for c in mod.co_consts:
                if getattr(c, 'co_name', '') == 'build_animation_categories':
                    consts.append(new_fn_code); patched += 1
                else:
                    consts.append(c)
            assert patched == 1, 'target function not found'
            mod = mod.replace(co_consts=tuple(consts))
            raw = zlib.compress(marshal.dumps(mod), 6)
        new_off = 12 + len(body)
        body += raw
        new_toc.append((name, (typ, new_off, len(raw))))
    assert patched == 1
    tbytes = marshal.dumps(new_toc)
    new_tocoff = 12 + len(body)
    out = header[:8] + struct.pack('!i', new_tocoff) + bytes(body) + tbytes
    return out, patched, len(toc)

def main():
    data = open(SRC_EXE, 'rb').read()
    old_pyz = data[PYZ_ABS:TOC_ABS]
    print('old pyz len', len(old_pyz))

    src = open(os.path.join(os.path.dirname(__file__), 'newfn.py'), encoding='utf-8').read()
    ns = {}
    exec(compile(src, 'newfn.py', 'exec'), ns)
    mod = compile(ns['NEW_SRC'], 'pet\\context_menus\\shared.py', 'exec')
    fn = [c for c in mod.co_consts if getattr(c, 'co_name', '') == 'build_animation_categories'][0]

    new_pyz, patched, nmods = build_new_pyz(old_pyz, fn)
    print('new pyz len', len(new_pyz), 'patched', patched, 'modules', nmods)
    L = len(new_pyz)

    # 校验新 PYZ 自洽
    t2 = marshal.loads(new_pyz[struct.unpack('!i', new_pyz[8:12])[0]:])
    assert len(t2) == nmods, (len(t2), nmods)
    d2 = dict(t2)
    typ, off, ln = d2['pet.context_menus.shared']
    chk = marshal.loads(zlib.decompress(new_pyz[off:off+ln]))
    assert any(getattr(c,'co_name','')=='build_animation_categories' for c in chk.co_consts)
    print('self-check ok')

    toc = bytearray(data[TOC_ABS:COOKIE])
    struct.pack_into('!i', toc, PYZ_TOC_ENTRY_REL + 8,  L)
    struct.pack_into('!i', toc, PYZ_TOC_ENTRY_REL + 12, L)

    cookie = bytearray(data[COOKIE:])
    new_toc_off = (PYZ_ABS + L) - ARCH
    new_pkg_len = (PYZ_ABS + L + TOC_LEN + 88) - ARCH
    struct.pack_into('!i', cookie, 8,  new_pkg_len)
    struct.pack_into('!i', cookie, 12, new_toc_off)

    out = data[:PYZ_ABS] + new_pyz + bytes(toc) + bytes(cookie)
    print('new exe size', len(out), 'delta', len(out)-len(data))
    print('toc_off', new_toc_off, 'pkg_len', new_pkg_len)

    if not os.path.exists(BAK_EXE):
        shutil.copy2(SRC_EXE, BAK_EXE)
        print('backup ->', BAK_EXE)
    open(SRC_EXE, 'wb').write(out)
    print('written')

main()
