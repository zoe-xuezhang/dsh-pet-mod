# -*- coding: utf-8 -*-
# 右键菜单「快速对话」：改成开气泡（QuickChatBubble），而不是完整聊天窗。
#
# 关键：菜单建造器的 pet 参数有两种形态
#   1) PetWindow / PetInstance（legacy 单窗拓扑）→ 有 on_open_quick_chat 回调（app 注入）
#   2) SpriteMenuFacade（overlay 合成窗拓扑，用户当前就是这条）→ 只有 on_open_chat，
#      气泡入口在它持有的 OverlayShell.open_quick_chat(sprite) 上
# 上一版只探测 1)，overlay 下必然落到 on_open_chat → 还是大窗。
NEW_SRC = r'''def _build_chat(menu, pet):
    cb = getattr(pet, 'on_open_quick_chat', None)
    if cb is None:
        shell = getattr(pet, '_shell', None)
        qc = getattr(shell, 'open_quick_chat', None)
        if callable(qc):
            sprite = getattr(pet, '_sprite', None)
            cb = lambda s=sprite: qc(s)
    if cb is None:
        cb = getattr(pet, 'open_quick_chat', None)
    if cb is None:
        cb = pet.on_open_chat
    return add_action(menu, '快速对话', 'chat', cb, close_on_trigger=True)
'''

if __name__ == '__main__':
    import dis
    code = compile(NEW_SRC, 'pet\\context_menus\\registry.py', 'exec')
    fn = [c for c in code.co_consts if getattr(c, 'co_name', '') == '_build_chat'][0]
    print('argcount', fn.co_argcount, 'kwonly', fn.co_kwonlyargcount, 'flags', hex(fn.co_flags))
    print('varnames', fn.co_varnames)
    print('consts', [x for x in fn.co_consts if isinstance(x, (str, bool))])
    assert fn.co_argcount == 2 and fn.co_kwonlyargcount == 0
    assert '快速对话' in fn.co_consts and '_shell' in fn.co_consts
    dis.dis(fn)
