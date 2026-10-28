# -*- coding: utf-8 -*-
"""把 pet.context_menus.registry::_build_chat 换成气泡版，重建 PYZ 并写回 exe。

特点：所有偏移全部从文件现场解析，不硬编码（exe 已被改过一次，长度变了）。
"""
import struct, marshal, zlib, shutil, os, sys

EXE = r'D:\dshpet\dsh-pet-standalone-webm-chat.exe'
BAK = r'D:\dshpet\dsh-pet-standalone-webm-chat.exe.bak-bubble'
MAGIC = b'MEI\x0c\x0b\x0a\x0b\x0e'
TARGET_MOD = 'pet.context_menus.registry'
TARGET_FN = '_build_chat'


def load_new_code():
    src = open(os.path.join(os.path.dirname(__file__), 'newfn_chat.py'), encoding='utf-8').read()
    ns = {}
    exec(compile(src, 'newfn_chat.py', 'exec'), ns)
    mod = compile(ns['NEW_SRC'], 'pet\\context_menus\\registry.py', 'exec')
    fn = [c for c in mod.co_consts if getattr(c, 'co_name', '') == TARGET_FN]
    assert len(fn) == 1, 'new fn not found'
    fn = fn[0]
    assert fn.co_argcount == 2 and fn.co_kwonlyargcount == 0, 'signature mismatch'
    return fn, ns


def main():
    data = open(EXE, 'rb').read()
    pos = data.rfind(MAGIC)
    assert pos > 0, 'PyInstaller cookie not found'
    pkg_len, toc_off, toc_len, pyver = struct.unpack('!iiii', data[pos + 8:pos + 24])
    arch = len(data) - pkg_len
    toc = bytearray(data[arch + toc_off: arch + toc_off + toc_len])

    # 解析 TOC，定位 PYZ
    i, pyz_rel, pyz_len, pyz_entry_rel = 0, None, None, None
    while i < len(toc):
        elen, off, dlen, ulen = struct.unpack('!iiii', toc[i:i + 16])
        if elen <= 0:
            break
        name = toc[i + 18:i + elen].rstrip(b'\x00').decode('utf-8', 'replace')
        if name.lower().endswith('.pyz'):
            pyz_rel, pyz_len, pyz_entry_rel = off, dlen, i
        i += elen
    assert pyz_rel is not None, 'PYZ entry not found'
    pyz_abs = arch + pyz_rel
    assert pyz_abs + pyz_len == arch + toc_off, 'PYZ is not the last member'
    print('exe %d, arch %d, pyz abs %d len %d, toc abs %d'
          % (len(data), arch, pyz_abs, pyz_len, arch + toc_off))

    old_pyz = data[pyz_abs:pyz_abs + pyz_len]
    old_tocoff = struct.unpack('!i', old_pyz[8:12])[0]
    old_toc = marshal.loads(old_pyz[old_tocoff:])
    header = old_pyz[:12]
    # 原文件 header 与首个模块之间有 5 字节对齐空隙，保持一致
    body = bytearray(old_pyz[12:old_toc[0][1][1]])
    print('header gap =', len(body))

    new_fn, _ = load_new_code()
    new_toc, patched = [], 0
    for name, (typ, off, ln) in old_toc:
        raw = old_pyz[off:off + ln]
        if name == TARGET_MOD:
            mod = marshal.loads(zlib.decompress(raw))
            consts = []
            for c in mod.co_consts:
                if getattr(c, 'co_name', '') == TARGET_FN:
                    consts.append(new_fn)
                    patched += 1
                else:
                    consts.append(c)
            assert patched == 1, 'target function not found in %s' % TARGET_MOD
            mod = mod.replace(co_consts=tuple(consts))
            raw = zlib.compress(marshal.dumps(mod), 6)
        new_off = 12 + len(body)
        body += raw
        new_toc.append((name, (typ, new_off, len(raw))))
    assert patched == 1

    new_toc_bytes = marshal.dumps(new_toc)
    new_tocoff = 12 + len(body)
    new_pyz = header[:8] + struct.pack('!i', new_tocoff) + bytes(body) + new_toc_bytes

    # 自检：新 PYZ 能被解析回同样数量的模块，且目标函数已是新版
    chk_tocoff = struct.unpack('!i', new_pyz[8:12])[0]
    chk = dict(marshal.loads(new_pyz[chk_tocoff:]))
    assert len(chk) == len(old_toc), (len(chk), len(old_toc))
    typ, off, ln = chk[TARGET_MOD]
    code = marshal.loads(zlib.decompress(new_pyz[off:off + ln]))
    got = [c for c in code.co_consts if getattr(c, 'co_name', '') == TARGET_FN][0]
    assert 'on_open_quick_chat' in got.co_consts and '快速对话' in got.co_consts
    assert got.co_argcount == 2 and got.co_kwonlyargcount == 0
    print('self-check ok, modules', len(chk), 'new pyz len', len(new_pyz))

    delta = len(new_pyz) - pyz_len
    struct.pack_into('!i', toc, pyz_entry_rel + 8, len(new_pyz))
    struct.pack_into('!i', toc, pyz_entry_rel + 12, len(new_pyz))

    cookie = bytearray(data[pos:pos + 88])
    struct.pack_into('!i', cookie, 8, pkg_len + delta)
    struct.pack_into('!i', cookie, 12, toc_off + delta)

    out = data[:pyz_abs] + new_pyz + bytes(toc) + bytes(cookie)
    print('delta %+d, new size %d' % (delta, len(out)))

    if not os.path.exists(BAK):
        shutil.copy2(EXE, BAK)
        print('backup ->', BAK)
    open(EXE, 'wb').write(out)
    print('written')


main()
