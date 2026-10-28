# 大肥鱼桌宠 · 个人修改版备份

这是 **dsh-pet-indesktop（大肥鱼桌宠独立版）** 的个人改造版本备份，不是官方发布。

## 上游

| 项 | 值 |
|---|---|
| 仓库 | https://github.com/MerZlin/dsh-pet-indesktop |
| 版本 | v4.4.0 · `dsh-pet-standalone-webm-chat-portable.zip` |
| 许可证 | MIT（允许修改与再分发，保留版权声明即可） |
| 角色素材 | shenshen（102 段 webm） |

上游发布的是 **PyInstaller onedir 打包产物**，没有 `.py` 源码可改。本仓库的修改是**直接改写 exe 内嵌的 Python 字节码**（`PYZ-00.pyz` 归档），不是改配置。

## 改了什么

### 1. 右键「播放动画」大类重构（改字节码）

**原版**：5 个一级分类，4 个瘦的 + 1 个胖的，头重脚轻。

```
播放动画 ▸
  待机(1)  转向(1)  移动(3)  点击回应(5)
  随机动作 ▸ 日常(21) 吃货(20) 表演(17) 节日(13) 玩乐(12) 工作(8)
```

**改后**：10 个分类全部平铺在一级，零遗漏 101 项。

```
播放动画 ▸
  日常(21)  吃货(20)  表演(17)  节日(13)  玩乐(12)  工作(8)
  待机(1)   转向(1)   移动(3)   点击回应(5)
```

改的是 `pet/context_menus/shared.py::build_animation_categories`。

**关键：函数签名必须严格一致**

```python
def build_animation_categories(menu, pet, *, icons,
                               legacy_labels=False, leaf_role_icons=False)
```

- `co_argcount = 2`（menu, pet）
- `co_kwonlyargcount = 3`（icons 必填 / legacy_labels / leaf_role_icons）
- `close_on_trigger` 不是参数，是函数体内第一行赋值的局部变量
- 写成 6 个普通位置参数会导致调用方绑定失败 → 菜单构建错位 → Qt/shiboken 层 `0xC0000005` 崩溃

### 2. 右键「AI 对话」→ 改名「快速对话」，开小气泡而不是完整聊天窗（改字节码）

**原版**：右键菜单「AI 对话」直接 `PetInstance.open_chat`，弹一个 900×600 级的完整聊天窗。

**改后**：菜单项改名「快速对话」，点开的是锚定在鱼头顶的 `QuickChatBubble`（320×162，带输入框 + 发送按钮），回车即发，回复也在气泡里滚动，不弹大窗。

改的是 `pet/context_menus/registry.py::_build_chat`（`co_argcount=2`、`co_kwonlyargcount=0`，与原版签名一致）。

**踩坑（第一次改失败的原因）**：菜单建造器的 `pet` 参数有两种形态——

- legacy 单窗拓扑：`PetWindow` / `PetInstance`，有 app 注入的 `on_open_quick_chat`
- overlay 合成窗拓扑（本机就是这个，`PET_RENDER_TOPOLOGY=overlay`）：传进来的是 `SpriteMenuFacade`，**只有 `on_open_chat`**，气泡入口挂在它持有的 `OverlayShell.open_quick_chat(sprite)` 上

第一版只写了 `getattr(pet, 'on_open_quick_chat', None) or pet.on_open_chat`，在 facade 上必然取不到 → 回落到完整窗 → 仍然是「大窗」。现版按鸭子类型三级探测：`on_open_quick_chat` → `pet._shell.open_quick_chat(pet._sprite)` → `open_quick_chat` → `on_open_chat`。

注意 `SpriteMenuFacade.on_open_chat` 是 **property**（返回宿主 callable），不是 method。

### 3. 物理开关（改配置，不动字节码）

`config-slot-0.json`：

| 键 | 出厂 | 现设 | 作用 |
|---|---|---|---|
| `drag_physics` | false | **true** | 拖拽跟手（弹簧）+ 松手抛掷 |
| `drop_gravity` | false | **true** | 自由落体 + 撞墙反弹 + 落地弹跳 |

物理引擎本来就是独立版原生模块（`pet.physics`），插件版 dsh-pet 的 `physics.ts` 注释写明「参数与取值依据移植自 dsh-pet-indesktop 的 physics.py」，即独立版才是源头。

实测常量：重力 1400 px/s²、弹性恢复 0.68、地面摩擦 2.5、甩速上限 6000 px/s、弹簧 k=200 c=30、弹弓拉伸 24~160px / 初速 900。

## 文件清单

| 文件 | 说明 |
|---|---|
| `dsh-pet-standalone-webm-chat.exe` | 改好的主程序（16,421,908 字节）。原版是 16,421,283 字节 |
| `patch/newfn.py` | 新的 `build_animation_categories` 源码 |
| `patch/newfn_chat.py` | 新的 `_build_chat` 源码（气泡版） |
| `patch/repack.py` | 重打包脚本（硬编码偏移，针对原版） |
| `patch/repack_chat.py` | 重打包脚本（**现场解析偏移**，可反复叠加修改） |
| `patch/dryrun2.py` | 离屏验证菜单树（用真实 group_animation_entries + 真实素材） |
| `patch/physdemo.py` | 从 exe 提取物理常量并模拟抛掷轨迹 |
| `patch/dump_orig.py` | 反汇编原版函数（用于还原真实签名） |
| `config/config-slot-0.json` | 当前配置（含物理开关、缩放、相对位置） |

## 怎么用

1. 把 `dsh-pet-standalone-webm-chat.exe` 覆盖到安装目录（本机是 `D:\开源skill\dsh-pet-indesktop\app\`，通过 Junction `D:\dshpet` 访问）
2. 配置放 `%APPDATA%\dsh-pet-standalone-webm-chat\config-slot-0.json`
3. 双击启动器（本机：桌面 `启动大肥鱼.vbs`）

## 怎么回滚

上游原版 exe 备份在本机 `dsh-pet-standalone-webm-chat.exe.orig`（16,421,283 字节），覆盖回去即恢复原样；物理开关改回 `false` 即可。

## 复现修改所需的归档坐标

针对 v4.4.0 这份 exe（原版 16,421,283 字节）：

- `PYZ-00.pyz` 绝对偏移 **759811**，其后紧跟 CArchive TOC（640 B）@ 16,420,555、MEI cookie（88 B）@ 16,421,195
- `arch_start = filesize - pkg_len = 728064`（pkg_len **含** 88 B cookie）
- TOC 条目格式：`!iiii B c + name`（elen / off / dlen / ulen / flag / typ / name）；PYZ 条目在 TOC 内相对偏移 **608**
- 改完只需同步 3 处：TOC 里 PYZ 的 dlen 与 ulen、cookie 的 pkg_len（加 Δ）、cookie 的 toc_off（加 Δ）
- PYZ 结构：`PYZ\0` + pyc magic(4) + tocoff(4, 大端) + 数据 + `marshal.dumps(list[(name, (typ, off, len))])`，off 是绝对偏移，typ 1 = package
- 必须用 **Python 3.11** 编译与解析（系统 Python 3.13 读 3.11 字节码会乱码）

## 免责

个人备份用途。角色素材与原始代码版权归上游作者所有，遵循 MIT 许可。
