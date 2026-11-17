#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 slint-course-kit 的全部索引、版权与说明文档。"""
import csv
import json
import re
from pathlib import Path

ROOT = Path('/Users/rain9/WorkBuddy/2026-11-09-15-16-30')
REPO = ROOT / 'slint-course-kit'
VIDEO = ROOT / 'slint-video'
E = json.loads((REPO / 'tools' / 'entries.json').read_text(encoding='utf-8'))

META = {}
with open(VIDEO / 'publish.csv', encoding='utf-8-sig') as f:
    for row in list(csv.reader(f))[1:]:
        META[int(row[0][1:])] = dict(title=row[1], chap=row[2], minutes=row[3],
                                     video=row[4], timeline=row[6])

STEPS = [
    ('step01-hello', 'P02', 'Hello World', 'Cargo.toml / build.rs / ui / include_modules! 四件套'),
    ('step02-tile', 'P03', '第一块瓷砖', 'component MemoryTile inherits Rectangle、@image-url'),
    ('step03-interaction', 'P04', '幕布、点击与动画', 'TouchArea、callback、animate width / x'),
    ('step04-grid', 'P05', '从一块到网格', 'struct TileData、for tile[i] in ... repeater'),
    ('step05-shuffle', 'P06', '规则回到 Rust', 'VecModel、rand 洗牌、set_memory_tiles'),
    ('step06-game-logic', 'P07', '完整游戏', 'check_if_pair_solved、disable_tiles、Timer'),
]
GAME_OF_EP = {2: 'step01-hello', 3: 'step02-tile', 4: 'step03-interaction',
              5: 'step04-grid', 6: 'step05-shuffle', 7: 'step06-game-logic',
              16: 'step06-game-logic'}
ARTICLE_OF_EP = {
    1: '01', 9: '01 / 02', 10: '02', 11: '02', 4: '03', 12: '03', 13: '03',
    14: '04', 6: '05', 7: '05', 15: '05', 16: '05',
}
ARTICLES = [
    ('01-声明式与响应式.md', 'P01 + P09', '为什么单独造一门语言、绑定与依赖追踪'),
    ('02-属性类型与表达式.md', 'P09–P11', 'property 可见性、类型系统、表达式与函数'),
    ('03-回调状态与动画.md', 'P04 + P12 + P13', 'callback、global、states、animate 与幕布动画'),
    ('04-布局系统.md', 'P14', '显式定位、布局元素、绑定环与取舍'),
    ('05-组件模型与跨平台发布.md', 'P06/P07 + P15/P16', '控件库、数据模型、多语言宿主与发布'),
]

N_EX = sum(x['kind'] == 'example' for x in E)
N_SNIP = sum(x['kind'] == 'snippet' for x in E)
N_CF = sum(x['kind'] == 'compile-fail' for x in E)
TOTAL_MIN = sum(float(m['minutes']) for m in META.values())


def w(path, text):
    p = REPO / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding='utf-8')


# ---------------- README ----------------
lines = [
    '# Slint 16 集系统课 · 配套资料包', '',
    '> 一个链接覆盖：**可运行的渐进工程 / 编译校验过的语法示例 / 学习手册 / 图文长文**。',
    '> 配合 B 站《Slint 声明式 UI》16 集中文系统课使用；所有内容依据 Slint 官方文档整理，中文讲解。', '',
    '## 里面有什么', '',
    '| 内容 | 数量 | 位置 | 说明 |', '| --- | --- | --- | --- |',
    '| Memory Game 渐进工程 | 6 个 | `memory-game/` | P02–P07 同一个项目逐集长大，每个都能 `cargo run` |',
    f'| 独立语法示例 | {N_EX} 个 | `examples/` | 逐个交给 Slint 编译器验证通过，可用 `slint-viewer` 预览 |',
    f'| 讲解摘录 | {N_SNIP} 段 | `docs/snippets/` | 命令行、Cargo.toml、宿主语言、局部语法，按集整理 |',
    f'| 故意报错反例 | {N_CF} 个 | `compile-fail/` | 附课程标注与本机实测诊断 |',
    '| 学习手册 | 36 页 | `docs/学习手册.pdf` | 另有 `.md` / `.html`；每集目标、规则、坑、练习、知识地图、代码索引 |',
    '| 图文长文 | 5 篇 | `articles/` | 把口语旁白改写成书面长文，适合发专栏引流 |',
    '| 语法校验器 | 1 个 | `tools/slintcheck/` | 离线 Rust 小工具，逐个编译 `.slint` 并输出诊断 |', '',
    '## 快速开始', '', '```bash',
    '# 需要 Rust 工具链（本仓库实测 rustc 1.99.1 / cargo 1.99.1）',
    'cargo check --workspace --all-targets     # 校验 6 个渐进工程（含 .slint 编译）',
    'cargo run -p step06-game-logic           # 跑完整的记忆游戏', '',
    '# 单独预览某个语法示例（需安装 slint-viewer：cargo install slint-viewer）',
    'slint-viewer examples/p09_s03.slint', '',
    '# 只想做语法编译校验，不装 viewer 也可以',
    'cargo run -p slintcheck -- examples/p09_s03.slint',
    '```', '',
    '> 本仓库使用 Slint `=1.18.1`（本机 crates.io 可获得的最高版本）；'
    '首次构建会下载依赖，之后可加 `CARGO_NET_OFFLINE=true`。', '',
    '## 16 集导航', '',
    '| 集 | 标题 | 时长(分) | 完整工程 | 示例 | 摘录 | 长文 |', '| --- | --- | --- | --- | --- | --- | --- |',
]
for n, m in sorted(META.items()):
    ex = sum(x['ep'] == n and x['kind'] == 'example' for x in E)
    sn = sum(x['ep'] == n and x['kind'] == 'snippet' for x in E)
    game = f'`{GAME_OF_EP[n]}`' if n in GAME_OF_EP else '—'
    art = ARTICLE_OF_EP.get(n, '—')
    lines.append(f"| P{n:02d} | {m['title']} | {m['minutes']} | {game} | {ex} | {sn} | {art} |")

lines += ['', '## Memory Game 六步演进', '',
          'P02–P07 不是六个孤立 demo，而是同一个项目连续长出来的六个快照。'
          '想看清「每一步到底新增了什么」，按顺序 diff 相邻两个 `ui/app-window.slint` 最直观。', '',
          '| 工程 | 视频 | 阶段 | 这一阶段新增 | 运行 |', '| --- | --- | --- | --- | --- |']
for name, ep, stage, desc in STEPS:
    lines.append(f"| [`{name}`](memory-game/{name}/) | {ep} | {stage} | {desc} | `cargo run -p {name}` |")

lines += ['', '## 目录结构', '', '```',
          'slint-course-kit/',
          '├── Cargo.toml                  # workspace：6 个渐进工程',
          '├── memory-game/                # P02–P07 六个可运行快照',
          '│   └── stepNN-xxx/             # Cargo.toml + build.rs + ui/ + src/ + icons/',
          '├── examples/                   # 85 个编译校验通过的 .slint 示例',
          '├── docs/',
          '│   ├── 学习手册.pdf / .md / .html',
          '│   ├── EXAMPLE_INDEX.md        # 示例 × 视频时间点对照表',
          '│   ├── 版本说明.md             # edition 1.20 与本机 1.18.1 的差异',
          '│   └── snippets/               # 按集整理的 83 段摘录',
          '├── compile-fail/               # 3 个反例 + 实测诊断',
          '├── articles/                   # 5 篇图文长文',
          '├── icons/                      # 8 张自制占位图标（非官方素材）',
          '└── tools/                      # 语法校验器、原始清单、重建脚本',
          '```', '',
          '## 准确性是怎么保证的', '',
          '1. **代码有出处**：渐进工程逐字取自 Slint 官方教程源文件 '
          '（`slint-video/assets/code/`，MIT）；示例与摘录逐字取自课程逐镜脚本，'
          '每个文件头都写了来源、`Pxx mm:ss` 视频定位和「补了什么外壳」。',
          '2. **真的编译过**：6 个工程跑通 `cargo check --workspace --all-targets` 与 '
          '`cargo build --workspace`；85 个示例逐个交给 `slint-interpreter 1.18.1` 编译通过。'
          '分类不靠猜关键字，靠编译器判定。',
          '3. **时间点来自成品**：`Pxx mm:ss` 取自 `subs/epNN/segments.json` 的真实 TTS 时间轴，'
          '并与 `publish.csv` 逐集核对；时长与 `ffprobe` 实测一致。',
          '4. **不硬凑**：引用 `MemoryTile`、`root.rows`、`slider`、`Logic` 的局部片段没有为了编译通过'
          '而编造上下文，而是原样保留在摘录里，并指向 `memory-game/` 中的真实完整工程。', '',
          '**版本差异务必读**：课程依据官方文档（以 edition 1.20 为例），'
          '本机可得 crate 最高为 1.18.1。详见 [`docs/版本说明.md`](docs/版本说明.md)。', '',
          '## 许可', '',
          '官方文档与教程示例代码为 **MIT**（Copyright © SixtyFPS GmbH）；Slint 框架本体为三重许可。'
          '图标为自建占位素材。完整声明见 [`NOTICE.md`](NOTICE.md) 与 [`LICENSE`](LICENSE)。', '']
w('README.md', '\n'.join(lines))

# ---------------- EXAMPLE_INDEX ----------------
lines = ['# 示例索引 · 85 个编译校验过的 .slint', '',
         '每个文件都在 `examples/` 下，文件名 `p09_s03` 表示 **P09 第 3 张幻灯片**。'
         '全部经 `slint-interpreter 1.18.1` 编译通过。', '',
         '预览：`slint-viewer examples/p09_s03.slint`（或用 `cargo run -p slintcheck -- <文件>` 只做校验）。', '']
for n in sorted(META):
    xs = sorted([x for x in E if x['ep'] == n and x['kind'] == 'example'], key=lambda x: x['slide'])
    if not xs:
        continue
    lines += [f"## P{n:02d} · {META[n]['title']}（{len(xs)} 个）", '',
              '| 文件 | 视频定位 | 讲解点 | 外壳 |', '| --- | --- | --- | --- |']
    for x in xs:
        lines.append(f"| `{x['base']}.slint` | {x['stamp']} | "
                     f"{x['title'].replace('|', '\\|')} | {x['style']} |")
    lines.append('')
w('docs/EXAMPLE_INDEX.md', '\n'.join(lines))

# ---------------- 版本说明 ----------------
w('docs/版本说明.md', '\n'.join([
    '# 版本说明：课程讲的 1.20 与仓库跑的 1.18.1', '',
    '这一页解释一个容易被误解的地方：**课程里的概念没有错，仓库里也没有偷偷改代码**，'
    '只是两者依据的 Slint 版本不同。', '',
    '## 事实', '',
    '| | 课程视频 | 本仓库 |', '| --- | --- | --- |',
    '| 依据 | Slint 官方文档 latest（以 `edition 1.20` 为例） | 本机 crates.io 可获得的最高版本 `slint 1.18.1` |',
    '| 用途 | 讲清语言设计与语法语义 | 提供能真的编译、能真的跑的配套代码 |',
    '| 声明方式 | 文档示例里写 `#[edition = "1.20"]` | `Cargo.toml` 锁 `slint = "=1.18.1"` |', '',
    '本机 `cargo info slint` 返回 1.18.1，`cargo info slint@1.20.0` 报「registry 中找不到该版本」。'
    '也就是说制作时无法用 1.20 实测，因此仓库选择与**可验证环境一致**的版本，而不是写一个没跑过的工程。', '',
    '## 具体改了什么', '',
    '1. 官方教程的 Rust 单文件示例用 `slint::slint! { ... }` 宏，宏体第一行是 `#[edition = "1.20"]`。'
    '1.18.1 的解析器不认识该属性，会直接报 '
    '`Parse error: expected a top-level item such as a component, a struct, or a global`。'
    '还原工程时**只移除这一行**，其余代码逐字未改。',
    '2. 为了贴合课程 P02 讲的真实项目结构，把宏体拆成独立的 `ui/app-window.slint`，'
    '配 `build.rs` + `slint::include_modules!()`。这是结构整理，不是语法改写。',
    '3. 删除官方文档里的 `// ANCHOR:` / `// ANCHOR_END:` 片段锚点注释（它们不是代码）。', '',
    '## 哪些差异会真的看得见', '',
    '- **绑定环诊断**：课程 P04 / P14 讲「子元素撑起父元素」造成的绑定环，'
    '依据是「**1.19 起 `if` 里的 Text 也参与父元素尺寸计算**」。1.18.1 仍按旧行为，'
    '因此 `compile-fail/p04_s17.slint`、`p14_s11.slint` 在本机不会报课程里那条错误。',
    '- **赋值覆盖绑定警告**：课程 P01 讲的 `assignment will overwrite the binding`，'
    '1.18.1 未输出该警告。', '',
    '这三条反例的**课程标注**、**本机实测输出**与差异原因都在 '
    '[`compile-fail/README.md`](../compile-fail/README.md) 里逐条列出，没有为了凑报错而改写官方片段。', '',
    '## 如果你用的是 1.20 或更新版本', '',
    '1. 把 6 个工程的 `Cargo.toml` 里 `slint` / `slint-build` 的 `=1.18.1` 改成你的版本；',
    '2. 在 `ui/app-window.slint` 顶部加回 `#[edition = "1.20"]`（或按官方文档用项目文件 / '
    '`CompilerConfiguration::with_edition` 声明）；',
    '3. 语法主体不受影响，课程 P08 专门讲了 edition 的作用与声明位置。', '',
    '## 图标', '',
    '官方教程引用 `icons/at.png` 等 8 张图标，本仓库没有分发官方素材，'
    '而是用纯标准库生成了 8 张不同底色 + 编号的**占位 PNG**（`icons/` 及每个工程的 `ui/icons/`）。'
    '文件名与官方一致以便对照，游戏配对逻辑照常工作；想换成官方图标，直接覆盖对应 PNG 即可。', '',
]))

# ---------------- memory-game/README ----------------
lines = ['# Memory Game · 六个渐进工程', '',
         '课程 P02–P07 用同一个记忆翻牌游戏串起 Slint 基础：从 Hello World 一路长到完整游戏逻辑。'
         '这里把它还原成 6 个**各自独立、各自能跑**的 Cargo 工程。', '',
         '每个工程结构一致：', '', '```',
         'stepNN-xxx/',
         '├── Cargo.toml            # slint 运行时依赖 + slint-build 构建依赖（P06 起另加 rand）',
         '├── build.rs              # 编译期把 ui/app-window.slint 编进来',
         '├── ui/app-window.slint   # 界面（本阶段重点看这个）',
         '├── ui/icons/             # 8 张占位图标（@image-url 用）',
         '└── src/main.rs           # 宿主逻辑（P01–P05 只有几行，P06 起有游戏规则）',
         '```', '',
         '| 工程 | 视频 | 阶段 | 这一阶段新增 | 运行 |', '| --- | --- | --- | --- | --- |']
for name, ep, stage, desc in STEPS:
    lines.append(f"| [`{name}`]({name}/) | {ep} | {stage} | {desc} | `cargo run -p {name}` |")
lines += ['', '## 怎么对照视频', '',
          '按集顺序，把相邻两个工程的 `ui/app-window.slint` 做 diff：', '',
          '```bash',
          'diff -u memory-game/step02-tile/ui/app-window.slint \\',
          '          memory-game/step03-interaction/ui/app-window.slint',
          '```', '',
          '课程里那些只露出半截的片段（引用 `MemoryTile`、`TileData`、`MainWindow` 的），'
          '完整定义都在这里；[`docs/snippets/`](../docs/snippets/) 的每集文档也指到了对应工程。', '',
          '## 代码来源与改动', '',
          '逐字来自 Slint 官方教程示例（`slint-video/assets/code/`，'
          'MIT / Copyright © SixtyFPS GmbH）。仅三处整理：', '',
          '1. 把 `slint::slint! { ... }` 宏体拆成独立 `.slint` 文件；',
          '2. 移除 `#[edition = "1.20"]`（本机 1.18.1 不支持，详见 '
          '[`docs/版本说明.md`](../docs/版本说明.md)）；',
          '3. 移除 `// ANCHOR` 文档锚点注释。', '',
          '`cargo check --workspace --all-targets` 与 `cargo build --workspace` 均已实测通过。', '']
w('memory-game/README.md', '\n'.join(lines))

# ---------------- examples/README ----------------
w('examples/README.md', '\n'.join([
    '# 独立语法示例', '',
    f'共 {N_EX} 个 `.slint` 文件，全部经 `slint-interpreter 1.18.1` **编译通过**。', '',
    '这些文件由课程逐镜脚本里的代码片段整理而来：核心片段**逐字保留**，'
    '只为让它成为独立可编译的单元，补了最小外壳（例如 `export component Example inherits Window { ... }` '
    '或 `import { ... } from "std-widgets.slint";`）。每个文件头都写明补的是哪一种外壳。', '',
    '依赖上下文的局部片段（引用 `MemoryTile`、`TileData`、`root.rows`、`slider`、`Logic` 等）'
    '没有硬补一个假组件，而是原样放在 [`docs/snippets/`](../docs/snippets/) 并指向 '
    '[`memory-game/`](../memory-game/) 里的真实工程。', '',
    '## 预览与校验', '', '```bash',
    'slint-viewer examples/p09_s03.slint                 # 需要 cargo install slint-viewer',
    'cargo run -p slintcheck -- examples/p09_s03.slint  # 只编译，不开窗口',
    'cargo run -p slintcheck -- examples/*.slint        # 批量校验全部示例',
    '```', '',
    '完整清单（含视频时间点）见 [`docs/EXAMPLE_INDEX.md`](../docs/EXAMPLE_INDEX.md)。', '',
]))

# ---------------- articles/README ----------------
lines = ['# 配套图文长文', '',
         '5 篇文章对应课程里最值得单独展开的主题。口语旁白已改写成书面语，'
         '每篇含视频时间点、可运行示例与渐进工程的引用，适合发 B 站专栏 / 掘金 / 知乎当引流入口。', '',
         '| # | 文章 | 对应视频 | 主题 |', '| --- | --- | --- | --- |']
for i, (fn, ep, topic) in enumerate(ARTICLES, 1):
    lines.append(f"| {i:02d} | [`{fn}`]({fn}) | {ep} | {topic} |")
lines += ['', '## 发布顺序建议', '',
          '1. 视频发到 P01–P03 时先发 01（认知铺垫，最容易被转发）；',
          '2. P09–P11 期间发 02，配合「属性与类型」的搜索长尾；',
          '3. P12–P14 期间发 03、04，这两篇偏实战，适合嵌视频卡片；',
          '4. P15–P16 收官时发 05，把合集与代码仓一起收口。', '',
          '每篇结尾都留了引导位，发布时把视频卡片与仓库链接补上即可（仓库地址由你自己的托管决定，'
          '文章里没有写死 URL）。', '',
          '## 准确性约定', '',
          '- 所有 `pNN_sNN.slint` 引用、视频时间点、代码块均经过逐项比对，'
          '代码块逐字来自仓库文件；',
          '- 版本差异（edition 1.20 vs 本机 1.18.1）、wasm / 打包未做本机编译验证等，'
          '文中都如实标注，没有把未验证的东西写成「已跑通」。', '']
w('articles/README.md', '\n'.join(lines))

# ---------------- tools/README ----------------
w('tools/README.md', '\n'.join([
    '# 生成与校验工具', '',
    '## 数据文件', '',
    '- `code_inventory.json`：从课程 16 集逐镜数据中抽出的 **171 个代码镜头**原始清单'
    '（集数、镜号、标题、语言、代码、说明、错误标注）。',
    '- `entries.json`：分类结果，每条含 `kind`（example / snippet / compile-fail）、'
    '`stamp`（`Pxx mm:ss` 视频定位）、`style`（补了哪种外壳）、实测诊断等。', '',
    '## slintcheck/', '',
    '离线 Rust 小工具，依赖本地缓存的 `slint-interpreter =1.18.1`，'
    '用 `Compiler::build_from_path` 编译 `.slint` 并输出 JSON 诊断：', '',
    '```bash',
    'cd tools/slintcheck && cargo build --release',
    './target/release/slintcheck path/to/a.slint path/to/b.slint',
    '# {"path":"...","ok":false,"errors":["3:5: Unknown element ..."],"warnings":[],"components":[]}',
    '```', '',
    '它做的是**语法 / 类型层面的编译校验**，不打开窗口、不执行界面逻辑。'
    '`--include DIR` 可追加导入搜索路径。', '',
    '## 重建脚本', '',
    '| 脚本 | 作用 |', '| --- | --- |',
    '| `generate_game.py` | 从官方教程源文件还原 6 个渐进工程 + 占位图标 |',
    '| `generate_examples.py` | 抽 171 段代码、生成包装候选、逐个编译校验、写 examples / snippets / compile-fail |',
    '| `generate_handbook.py` | 生成学习手册 Markdown + HTML |',
    '| `generate_docs.py` | 生成 README、索引、版权与说明文档 |', '',
    '执行顺序：`generate_game.py` → `generate_examples.py` → `generate_handbook.py` → '
    'Chrome 导出 PDF → `generate_docs.py`。', '',
    '**注意**：`generate_examples.py` 会重建 `examples/`、`docs/snippets/`、`compile-fail/` '
    '三个目录的内容，但不会删除 README / LICENSE / 手册 / 文章。'
    '手工改动请先同步进脚本。', '',
]))

# ---------------- NOTICE / LICENSE / .gitignore ----------------
w('NOTICE.md', '\n'.join([
    '# 来源与许可声明', '',
    '本仓库是 B 站《Slint 声明式 UI》16 集中文系统课的配套资料，'
    '内容来源于 Slint 官方文档与教程示例，并做了中文讲解与结构化整理。', '',
    '## 1. Slint 官方文档与教程示例代码', '',
    '- 版权：Copyright © SixtyFPS GmbH <info@slint.dev>',
    '- 许可：**MIT**（官方源文件头部标注 `SPDX-License-Identifier: MIT`）',
    '- 来源：`slint-ui/slint` 仓库的 `docs/astro/src/content/docs/` 与教程示例',
    '  （本地副本：`slint-video/assets/docs/`、`slint-video/assets/code/`）',
    '- 使用方式：摘取、翻译为中文讲解；把官方 `slint!` 宏示例拆成独立的 `.slint` 与 Rust 工程；'
    '移除 edition 属性与文档锚点注释。所有改动在文件头与 `docs/版本说明.md` 中说明。', '',
    '## 2. 中文课程逐镜脚本', '',
    '本仓库的示例、摘录与学习手册内容取自该课程的逐镜脚本，'
    '而该脚本本身是依据上述 MIT 文档改编的中文讲解。', '',
    '## 3. Slint 框架本体', '',
    '`slint` / `slint-build` / `slint-interpreter` 等 crate 采用三重许可：', '',
    '`GPL-3.0-only OR LicenseRef-Slint-Royalty-free-2.0 OR LicenseRef-Slint-Software-3.0`', '',
    '本仓库**不分发框架源码或二进制**，只在 `Cargo.toml` 中声明依赖，'
    '由使用者自行通过 Cargo 获取并遵守其许可。', '',
    '## 4. 图标', '',
    '`icons/` 与各工程 `ui/icons/` 下的 8 张 PNG 是本仓库用纯标准库自制的**占位图标**'
    '（不同底色 + 编号），不是 Slint 官方素材。文件名与官方教程一致以便对照。', '',
    '## 5. 本仓库新增部分', '',
    '生成脚本、索引文档、学习手册排版、图文长文、占位图标等新增内容，'
    '同样以 MIT 许可提供，见 `LICENSE`。', '',
    '## 6. 保留声明', '',
    '官方源文件头部的版权与 SPDX 标识在还原工程里予以保留；'
    '本文件与 `LICENSE` 一并随仓库分发，以满足 MIT 的署名与许可文本随附要求。', '',
]))

MIT = '''MIT License

Copyright (c) SixtyFPS GmbH <info@slint.dev> (Slint official documentation and examples)
Copyright (c) 2026 slint-course-kit contributors (Chinese course materials, generated scripts, docs)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''
w('LICENSE', MIT)
w('.gitignore', '\n'.join(['/target/', '/tools/slintcheck/target/', '.DS_Store',
                           '*.log', '']))

print(f'README/index/notice done: {N_EX} examples, {N_SNIP} snippets, {N_CF} compile-fail, '
      f'{TOTAL_MIN:.0f} min')
