# -*- coding: utf-8 -*-
"""从原始 exe 提取真实 group_animation_entries，用假 Qt 层跑一遍新函数，验证菜单树。"""
import struct, marshal, zlib, os, types

SRC = r'D:\dshpet\dsh-pet-standalone-webm-chat.exe.orig'
pyz = open(SRC, 'rb').read()[759811:]
tocoff = struct.unpack('!i', pyz[8:12])[0]
TOC = dict(marshal.loads(pyz[tocoff:]))
typ, off, ln = TOC['pet.context_menus.shared']
MOD = marshal.loads(zlib.decompress(pyz[off:off + ln]))

# 模块级常量
import dis
consts = {}
prev = None
for ins in dis.get_instructions(MOD):
    if ins.opname == 'LOAD_CONST':
        prev = ins.argval
    elif ins.opname == 'STORE_NAME' and str(ins.argval).startswith('ANIMATION_'):
        consts[ins.argval] = prev

fnmap = {c.co_name: c for c in MOD.co_consts if hasattr(c, 'co_code')}
print('ANIMATION_* =', consts)
print('has fns:', [n for n in ('group_animation_entries', 'build_animation_categories') if n in fnmap])

G = dict(consts)
G.update({'len': len, 'sorted': sorted, 'tuple': tuple, 'isinstance': isinstance,
          'list': list, 'str': str})
for name in ('_dash_family_key', '_prefix_family_key'):
    G[name] = types.FunctionType(fnmap[name], G)
G['group_animation_entries'] = types.FunctionType(fnmap['group_animation_entries'], G)


class FakeAction:
    def __init__(self, text, menu=None):
        self._t = text
        self._m = menu

    def text(self):
        return self._t

    def menu(self):
        return self._m

    def isSeparator(self):
        return False


class _Sig:
    def __init__(self):
        self.fns = []

    def connect(self, fn):
        self.fns.append(fn)


class FakeMenu:
    def __init__(self, text='', parent=None):
        self._text = text
        self._actions = []
        self.aboutToShow = _Sig()

    def addMenu(self, sub):
        self._actions.append(FakeAction(sub._text, sub))

    def addAction(self, text):
        self._actions.append(FakeAction(text))

    def setIcon(self, *a):
        pass

    def actions(self):
        return self._actions


populated = []


def fake_populate(submenu, pet, entries, callback, leaf_role_icons, close_on_trigger):
    assert hasattr(pet, 'switch_clip'), 'pet 位置错了: %r' % (pet,)
    assert isinstance(entries, (list, tuple)), 'entries 位置错了: %r' % (entries,)
    assert callable(callback), 'callback 位置错了: %r' % (callback,)
    names = list(entries)
    populated.append((submenu._text, len(names)))
    for n in names:
        submenu.addAction(n)
    return None


G2 = dict(G)
G2.update({
    '_crash_sink': None,
    'QMenu': FakeMenu,
    'add_submenu': lambda parent, text, icon_name=None: (lambda m: (parent.addMenu(m), m)[1])(FakeMenu(text)),
    'inherit_menu_style': lambda *a: None,
    'vector_menu_icon': lambda *a: None,
    'animation_menu_stay_open': lambda p: False,
    '_populate_animation_category': fake_populate,
})

newmod = compile(open(os.path.join(os.path.dirname(__file__), 'build', 'newfn.py'),
                      encoding='utf-8').read().split("NEW_SRC = r'''")[1].split("'''")[0],
                 'shared.py', 'exec')
newfn = [c for c in newmod.co_consts if getattr(c, 'co_name', '') == 'build_animation_categories'][0]
G2['build_animation_categories'] = types.FunctionType(newfn, G2)

VID = r'D:\dshpet\_internal\assets\characters\shenshen\videos'


def names(sub):
    p = os.path.join(VID, sub)
    return sorted(os.path.splitext(f)[0] for f in os.listdir(p) if f.endswith('.webm'))


class Pet:
    idles = names('idle')
    turns = names('turn')
    moves = names('move')
    clicks = names('click')
    acts = names('random')

    def switch_clip(self, *a, **k):
        pass

    def trigger_move(self, *a, **k):
        pass


root = FakeMenu('root')
fnc = G2['build_animation_categories']
print('argcount', fnc.__code__.co_argcount, 'kwonly', fnc.__code__.co_kwonlyargcount)
# FunctionType 不会带上 kwdefaults，手动补（真实环境由 MAKE_FUNCTION 注入）
fnc.__kwdefaults__ = {'legacy_labels': False, 'leaf_role_icons': False}
fnc(root, Pet(), icons=True)

print('\n=== 一级菜单 ===')
total = 0
for a in root.actions():
    sm = a.menu()
    # 触发 aboutToShow 连锁
    for fn in sm.aboutToShow.fns:
        fn()
    kids = sm.actions()
    print(f'  {a.text():<12} ({len(kids)})')
    total += len(kids)

print('\n动作总数:', total)
print('填充回调次数:', len(populated))
print('素材总数:', len(Pet.idles) + len(Pet.turns) + len(Pet.moves) + len(Pet.clicks) + len(Pet.acts))
assert total == 101, total
print('\n断言通过：101 项零遗漏，全部一级平铺')
