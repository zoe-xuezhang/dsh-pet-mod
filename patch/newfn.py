# -*- coding: utf-8 -*-
NEW_SRC = r'''
def build_animation_categories(menu, pet, *, icons, legacy_labels=False, leaf_role_icons=False):
    close_on_trigger = not animation_menu_stay_open(pet)

    basics = (
        ('待机', pet.idles, pet.switch_clip),
        ('转向', pet.turns, pet.switch_clip),
        ('移动', pet.moves, pet.trigger_move),
        ('点击回应', pet.clicks, pet.switch_clip),
    )

    acts = pet.acts
    themes = ()
    if isinstance(acts, (list, tuple)):
        themes = group_animation_entries(acts)

    categories = []
    if themes:
        for family_label, family_entries in themes:
            categories.append((family_label, family_entries, pet.switch_clip, False))
    elif acts:
        categories.append(('随机动作', acts, pet.switch_clip, True))
    for label, entries, callback in basics:
        categories.append((label, entries, callback, False))

    for label, entries, callback, groupable in categories:
        if not entries:
            continue
        submenu = QMenu(('动画 · ' + label) if legacy_labels else label, menu)
        menu.addMenu(submenu)
        menu._owned_submenus = getattr(menu, '_owned_submenus', []) + [submenu]
        inherit_menu_style(menu, submenu)
        if icons:
            submenu.setIcon(vector_menu_icon(menu, 'play'))

        groups = ()
        if groupable and isinstance(entries, (list, tuple)):
            groups = group_animation_entries(entries)
        if groups:
            for family_label, family_entries in groups:
                family = add_submenu(submenu, family_label)
                family.aboutToShow.connect(
                    lambda s=family, e=family_entries, c=callback, l=leaf_role_icons,
                           p=pet, t=close_on_trigger:
                    _populate_animation_category(s, p, e, c, l, t))
        else:
            submenu.aboutToShow.connect(
                lambda s=submenu, e=entries, c=callback, l=leaf_role_icons,
                       p=pet, t=close_on_trigger:
                _populate_animation_category(s, p, e, c, l, t))
'''
