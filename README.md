# 大肥鱼桌宠 · 个人配置备份

> ## ⚠️ 这不是我的项目
>
> 本仓库**不是**任何原创作品。桌宠程序、角色素材、物理引擎、界面设计全部来自下面列出的上游开源项目，版权与著作权归原作者所有。
>
> 我做的事情只有一件：在自己的电脑上按个人习惯**改了两处菜单逻辑、开了两个配置开关**，然后把改好的文件存到这里，免得哪天重装系统丢了。
>
> 你可以随便看、随便下，但请**不要把功劳算到我头上**——真正的作者在下面。

---

## 一、这个桌宠是哪来的

这是一条**三层继承**的链子，每一层都值得尊重：

| 层级 | 项目 | 作者/地址 | 做了什么 |
|---|---|---|---|
| ① 原始项目 | `dsh-pet` | [PC2005-cloud/dsh-pet](https://github.com/PC2005-cloud/dsh-pet) | 蓝色大肥鱼桌宠的最初实现 |
| ② 跨平台移植版 | `dsh-pet-indesktop` | [MerZlin/dsh-pet-indesktop](https://github.com/MerZlin/dsh-pet-indesktop) | 基于①，把桌宠移植到 Windows / Linux / macOS，并额外实现了大量交互功能 |
| ③ **本仓库** | 个人配置备份 | 本人（GitHub: 18186878524） | 基于② 的 v4.4.0 打包产物，改了两处菜单、开了两个开关 |

上游②的项目自述（原文）：

> 基于项目 PC2005-cloud/dsh-pet.git，将桌宠移植到 Windows、Linux 和 MacOS 上，现在可以随时看到蓝色大肥鱼了：），本项目还额外实现了其他交互功能，欢迎体验

### 上游② 的准确信息

| 项 | 值 |
|---|---|
| 仓库 | https://github.com/MerZlin/dsh-pet-indesktop |
| 项目描述 | 基于 PC2005-cloud/dsh-pet，移植到 Windows/Linux/macOS |
| 许可证 | MIT |
| Star / Fork | 2,633 / 173（截至 2026-10-28） |
| 创建时间 | 2026-08-17 |
| 本人使用版本 | **v4.4.0**（2026-10-22 发布，release 标题「试验先行版：素材架构换代、功能模块化与全局记忆」） |
| 原始压缩包 | `dsh-pet-standalone-webm-chat-portable.zip`（约 349 MB） |
| 角色素材 | `shenshen`（102 段 webm 动画） |
| 技术栈 | Python + PySide6(Qt6) + ffmpeg，物理引擎参数源自上游 |

**建议**：想用桌宠的话，直接去上面这个仓库下最新版，别用我这个。上游持续更新（最近一次推送就在 2026-10-28），我这份是冻在某一天的快照。

---

## 二、我改了什么（全部改动，就这些）

改动总量：**2 个 Python 函数 + 3 个配置键**。

exe 体积从原版 16,421,283 字节变成 16,421,908 字节——**只增加了 625 字节**。这就是全部改动的物理大小。

### 2.1 右键「播放动画」：分类从 5 个改到 10 个平铺

**上游原样**：4 个很瘦的分类 + 1 个很胖的分类，头重脚轻。

```
播放动画 ▸
  待机(1)  转向(1)  移动(3)  点击回应(5)
  随机动作 ▸ 日常(21) 吃货(20) 表演(17) 节日(13) 玩乐(12) 工作(8)
```

**我改成**：10 个分类全部平铺在一级，101 项一个不少。

```
播放动画 ▸
  日常(21)  吃货(20)  表演(17)  节日(13)  玩乐(12)  工作(8)
  待机(1)   转向(1)   移动(3)   点击回应(5)
```

- 改的函数：`pet/context_menus/shared.py::build_animation_categories`
- 改法：**直接改写 exe 内嵌的 Python 字节码**（详见第四节）
- 动画素材、分类归属、图标全部沿用上游原样，我一个都没动

### 2.2 右键「AI 对话」：改名「快速对话」，从小窗变气泡

**上游原样**：菜单项「AI 对话」，点开是一个 900×600 级的完整聊天窗。

**我改成**：菜单项改名「快速对话」，点开是锚定在鱼头顶的小气泡（约 320×162，带输入框和发送按钮），回车即发，回复也在气泡里滚动。

- 改的函数：`pet/context_menus/registry.py::_build_chat`
- 完整聊天窗**没有删除也没破坏**，气泡里有个「去聊天窗」按钮，随时能回去
- 两边共用同一份会话历史（上游本来就是这么设计的）

> 补充说明：气泡本身（`pet.quick_chat.QuickChatBubble`）是上游**原生就有**的功能，原本只挂在托盘菜单和「点头顶气泡」两个入口上。我只是把它挪到了右键菜单第一屏，**没有新写任何气泡代码**。

### 2.3 物理开关：从关到开（纯配置，不动代码）

`config-slot-0.json` 里改了两个键：

| 键 | 上游出厂 | 我设成 | 作用 |
|---|---|---|---|
| `drag_physics` | `false` | `true` | 拖拽跟手（弹簧效果）+ 松手可抛掷 |
| `drop_gravity` | `false` | `true` | 自由落体 + 撞墙反弹 + 落地弹跳 |

物理引擎（`pet.physics`）是上游原生模块，我只是把开关打开了。实测常量：重力 1400 px/s²、弹性恢复 0.68、地面摩擦 2.5、甩速上限 6000 px/s、弹簧 k=200 c=30。

顺带调了几个显示参数（缩放 0.72、屏幕相对位置 rx/ry），这些纯属个人审美，无技术含量。

---

## 三、我**没有**改什么（划界）

以下全部是上游原版，一个字没动：

- 全部角色素材（`shenshen` 102 段 webm，以及 `_internal/assets/` 下的所有图片/音频）
- 全部 UI 视觉设计、图标、主题、动画曲线
- 物理引擎算法与常量
- 聊天功能（ChatService / SessionStore / PromptBuilder / Markdown 渲染）
- 所有 AI 相关能力（模型接入、记忆、识屏、语音、抽签、节日、天气、音乐、Agent 联动）
- 多屏 / 高 DPI / 窗口拓扑 / 焦点穿透等平台层实现
- 上游的任何 bug（比如识屏时 `AttributeError: '_identity_config'` 这个已知问题，我看到了但**没修**，保持原样）

换句话说：**除了那两个菜单函数和三个配置键，你看到的每一行代码都是别人的。**

---

## 四、技术上是怎么改的（给想复现的人）

上游发布的是 **PyInstaller onedir 打包产物**，压缩包里没有 `.py` 源码，只有编译好的 `.pyc` 塞在 `PYZ-00.pyz` 归档里。所以改法不是"改源码重新编译"，而是：

1. 从 exe 尾部找 MEI cookie（88 字节）→ 反推 CArchive 起点
2. 解析 CArchive TOC → 定位 `PYZ-00.pyz` 条目
3. 解包 PYZ → `marshal.loads` 取出目标模块的 code object
4. 把目标函数从 `co_consts` 里换掉（用 `code.replace(co_consts=...)`）
5. 重新 `marshal.dumps` + zlib 压缩 → 重建 PYZ
6. 同步三处长度：TOC 里 PYZ 的 `dlen`/`ulen`、cookie 的 `pkg_len`、cookie 的 `toc_off`

### 归档坐标（针对 v4.4.0，原版 16,421,283 字节这份）

- `PYZ-00.pyz` 绝对偏移 **759811**
- 其后：CArchive TOC（640 B）@ 16,420,555、MEI cookie @ 16,421,195
- `arch_start = filesize - pkg_len = 728064`（注意 `pkg_len` **含**那 88 字节 cookie）
- TOC 条目格式：`!iiii B c + name`（elen / off / dlen / ulen / flag / typ / name）
- PYZ 条目在 TOC 内的相对偏移是 **608**
- PYZ 内部结构：`PYZ\0` + pyc magic(4) + tocoff(4，大端) + 数据 + `marshal.dumps(list[(name, (typ, off, len))])`，其中 `off` 是**绝对**文件偏移，`typ=1` 表示 package
- **必须用 Python 3.11**（上游就是 3.11 编译的；用 3.13 解析会得到乱码字节码）

### 最重要的一条坑

**替换函数必须与原函数签名完全一致**，否则不是报错，是 Qt/shiboken 层的 `0xC0000005` 段错误——进程直接消失，连 traceback 都没有。

必须对齐三个字段：

- `co_argcount`（位置参数个数）
- `co_kwonlyargcount`（仅关键字参数个数）
- `co_flags`

两个函数的真实签名：

```python
# shared.py::build_animation_categories
def build_animation_categories(menu, pet, *, icons, legacy_labels=False, leaf_role_icons=False):
    # co_argcount=2, co_kwonlyargcount=3
    close_on_trigger = not animation_menu_stay_open(pet)   # 这是局部变量，不是参数

# registry.py::_build_chat
def _build_chat(menu, pet):
    # co_argcount=2, co_kwonlyargcount=0
```

还有一个坑：`add_action` 的关键字参数叫 `close_on_trigger`（下划线），不是 `closeOnTrigger`（驼峰）。写成驼峰会 `TypeError`，而这个异常发生在 Qt slot 里，同样表现为"进程静默退出"。**判断真实参数名的方法：抄 `co_consts` 里那个 tuple，不要凭印象拼。**

### 另一条坑（气泡那次翻车的原因）

菜单建造器传进来的 `pet` 参数有两种形态，取决于渲染拓扑：

| 渲染拓扑 | `pet` 实际类型 | 气泡入口在哪 |
|---|---|---|
| legacy 单窗 | `PetWindow` / `PetInstance` | `on_open_quick_chat`（app 注入的回调） |
| overlay 单合成窗 | `SpriteMenuFacade` | `pet._shell.open_quick_chat(pet._sprite)`，**facade 上没有** `on_open_quick_chat` |

我第一版只探测 `on_open_quick_chat`，在 overlay 拓扑下必然取不到 → 回落到完整窗 → 表现就是"改了等于没改，还是大窗"。现版按鸭子类型三级探测，两种拓扑都能正确落到气泡。

（附带一条：`SpriteMenuFacade.on_open_chat` 是 **property**，getter 返回宿主 callable，不是普通 method。）

---

## 五、文件清单

| 文件 | 说明 |
|---|---|
| `dsh-pet-standalone-webm-chat.exe` | 改好的主程序，16,421,908 字节（上游原版 16,421,283） |
| `config/config-slot-0.json` | 我的配置（物理开关、缩放、屏幕相对位置） |
| `patch/newfn.py` | 新版 `build_animation_categories` 源码 |
| `patch/newfn_chat.py` | 新版 `_build_chat` 源码（气泡版） |
| `patch/repack.py` | 重打包脚本（偏移硬编码，只对上游原版 exe 有效） |
| `patch/repack_chat.py` | 重打包脚本（**偏移现场解析**，可反复叠加修改） |
| `patch/dryrun2.py` | 离屏验证菜单树（用真实分组函数 + 真实素材数据） |
| `patch/physdemo.py` | 从 exe 提取物理常量并模拟抛掷轨迹 |
| `patch/dump_orig.py` | 反汇编上游原版函数（用于还原真实签名） |
| `LICENSE` | MIT（GitHub 建仓时生成，与上游一致） |

> `patch/` 下的脚本只服务于本仓库的复现，不属于上游项目，也没什么复用价值。

---

## 六、怎么用

1. 先按上游 README 安装原版（下 `dsh-pet-standalone-webm-chat-portable.zip` 解压）
2. 把本仓库的 `dsh-pet-standalone-webm-chat.exe` 覆盖进 `app/` 目录
3. 把 `config/config-slot-0.json` 放到 `%APPDATA%\dsh-pet-standalone-webm-chat\`
4. 双击 exe（或用压缩包里的 `启动.bat` / 自建 VBS 免黑框启动）

**版本对不上就别覆盖**。这份 exe 是基于 v4.4.0 改的，上游若已发新版，直接覆盖会因为内部归档结构变化而出问题——那种情况下请重新按第四节的方法在新版上改，别拿旧 exe 顶。

## 七、怎么回滚

- exe：用上游原版覆盖回去即可（16,421,283 字节那份）
- 配置：把 `drag_physics` / `drop_gravity` 改回 `false`
- 菜单：exe 换回去，两个改动同时消失

---

## 八、版权与许可

- **代码**：版权归 PC2005-cloud、MerZlin 及所有上游贡献者所有，遵循 **MIT License**
- **角色素材**：`shenshen` 等美术资源版权归原素材作者所有，随上游项目一并分发
- **本仓库的改动**：上述两处字节码修改与配置，同样以 MIT 释出，随便用，不用署名我
- **MIT 的要求**：保留原始版权声明与许可声明。本仓库的 `LICENSE` 与上游一致，原版权声明见上游仓库

我不是作者，只是使用者。如果上游作者认为这个仓库有不妥之处，请开 issue 或直接联系我，我会立刻删除。

---

## 九、免责

个人备份用途，**不提供任何担保**。改的是别人的二进制文件，出问题请先换回上游原版再判断是不是我的锅。
