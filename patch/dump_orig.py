# -*- coding: utf-8 -*-
import struct, marshal, zlib, dis, sys

SRC = r'D:/dshpet/dsh-pet-standalone-webm-chat.exe.orig'
data = open(SRC,'rb').read()
PYZ_ABS = 759811
pyz = data[PYZ_ABS:]
tocoff = struct.unpack('!i', pyz[8:12])[0]
TOC = dict(marshal.loads(pyz[tocoff:]))
typ, off, ln = TOC['pet.context_menus.shared']
MOD = marshal.loads(zlib.decompress(pyz[off:off+ln]))

def walk(c):
    yield c
    for x in c.co_consts:
        if hasattr(x, 'co_code'):
            yield from walk(x)

names = [c.co_name for c in walk(MOD)]
print('ALL DEFS:', names)

# 模块级 ANIMATION_* 赋值
print('\n--- module level ANIMATION_* ---')
prev = None
for ins in dis.get_instructions(MOD):
    if ins.opname == 'LOAD_CONST':
        prev = ins.argval
    elif ins.opname in ('STORE_NAME','STORE_GLOBAL') and str(ins.argval).startswith('ANIMATION'):
        print(' ', ins.argval, '=', repr(prev))

for target in ('build_animation_categories',):
    for c in walk(MOD):
        if c.co_name == target:
            print('\n' + '='*70)
            print(target, 'argcount', c.co_argcount)
            print('varnames:', c.co_varnames)
            print('names:', c.co_names)
            print('consts:', [x for x in c.co_consts if isinstance(x,(str,int,float))])
            print('='*70)
            dis.dis(c, depth=0)
            break
