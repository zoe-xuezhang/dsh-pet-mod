# -*- coding: utf-8 -*-
import struct, marshal, zlib, dis, types

pyz = open(r'D:/dshpet/dsh-pet-standalone-webm-chat.exe','rb').read()[759811:]
tc = struct.unpack('!i', pyz[8:12])[0]
TOC = dict(marshal.loads(pyz[tc:]))
t,o,l = TOC['pet.physics']
M = marshal.loads(zlib.decompress(pyz[o:o+l]))

# 模块级常量
consts = {}
prev = None
for ins in dis.get_instructions(M):
    if ins.opname == 'LOAD_CONST': prev = ins.argval
    elif ins.opname in ('STORE_NAME','STORE_GLOBAL'): consts[ins.argval] = prev

print('--- pet.physics 模块级参数 ---')
for k, v in consts.items():
    if isinstance(v, (int, float, bool)) and not k.startswith('__'):
        print('  %-28s %r' % (k, v))

fns = {c.co_name: c for c in M.co_consts if hasattr(c,'co_code')}
G = dict(consts); G.update({'len':len,'abs':abs,'min':min,'max':max,'math':__import__('math'),
                            'tuple':tuple,'list':list,'isinstance':isinstance,'round':round})
for n in ('soft_clamp_speed','is_at_rest','throw_step','throw_speed_cap','normalize_throw_strength'):
    if n in fns: G[n] = types.FunctionType(fns[n], G)
if 'throw_step' not in G:
    print('!! throw_step 缺失'); raise SystemExit

# 模拟：从空中向斜上甩出，看弹跳轨迹
left, top, right, bottom = 0, 0, 1920-156, 1080-194
px, py = 600.0, 300.0
vx, vy = 900.0, -500.0
dt = 1/60
print('\n--- 模拟甩出（初速 %d,%d px/s，重力取自模块默认） ---' % (vx, vy))
bounces = 0
prev_vy = vy
for i in range(600):
    r = G['throw_step'](px, py, vx, vy, dt, left, top, right, bottom, 1400.0, 120.0, 60.0)
    px, py, vx, vy = r[0], r[1], r[2], r[3]
    if isinstance(r, dict):
        px, py, vx, vy = r['px'], r['py'], r['vx'], r['vy']
    if i % 6 == 0 and i < 120:
        print('  t=%5.2fs  pos=(%6.1f,%6.1f)  v=(%7.1f,%7.1f)' % (i*dt, px, py, vx, vy))
    if abs(vy) < 60 and py >= bottom-2: 
        print('  t=%5.2fs  静止 pos=(%.1f,%.1f)' % (i*dt, px, py)); break
print('  终点 pos=(%.1f,%.1f)' % (px, py))
