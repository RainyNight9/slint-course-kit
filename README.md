# Slint 16 集系统课 · 配套资料包

B 站地址：https://space.bilibili.com/481359926/lists/5192447?type=series

> 一个链接覆盖：**可运行的渐进工程 / 编译校验过的语法示例 / 学习手册 / 图文长文**。
> 配合 B 站《Slint 声明式 UI》16 集中文系统课使用；所有内容依据 Slint 官方文档整理，中文讲解。

## 里面有什么

| 内容 | 数量 | 位置 | 说明 |
| --- | --- | --- | --- |
| Memory Game 渐进工程 | 6 个 | `memory-game/` | P02–P07 同一个项目逐集长大，每个都能 `cargo run` |
| 独立语法示例 | 85 个 | `examples/` | 逐个交给 Slint 编译器验证通过，可用 `slint-viewer` 预览 |
| 讲解摘录 | 83 段 | `docs/snippets/` | 命令行、Cargo.toml、宿主语言、局部语法，按集整理 |
| 故意报错反例 | 3 个 | `compile-fail/` | 附课程标注与本机实测诊断 |
| 学习手册 | 36 页 | `docs/学习手册.pdf` | 另有 `.md` / `.html`；每集目标、规则、坑、练习、知识地图、代码索引 |
| 图文长文 | 5 篇 | `articles/` | 把口语旁白改写成书面长文，适合发专栏引流 |
| 语法校验器 | 1 个 | `tools/slintcheck/` | 离线 Rust 小工具，逐个编译 `.slint` 并输出诊断 |

## 快速开始

```bash
# 需要 Rust 工具链（本仓库实测 rustc 1.99.1 / cargo 1.99.1）
cargo check --workspace --all-targets     # 校验 6 个渐进工程（含 .slint 编译）
cargo run -p step06-game-logic           # 跑完整的记忆游戏

# 单独预览某个语法示例（需安装 slint-viewer：cargo install slint-viewer）
slint-viewer examples/p09_s03.slint

# 只想做语法编译校验，不装 viewer 也可以
cargo run -p slintcheck -- examples/p09_s03.slint
```

> 本仓库使用 Slint `=1.18.1`（本机 crates.io 可获得的最高版本）；首次构建会下载依赖，之后可加 `CARGO_NET_OFFLINE=true`。

## 16 集导航

| 集 | 标题 | 时长(分) | 完整工程 | 示例 | 摘录 | 长文 |
| --- | --- | --- | --- | --- | --- | --- |
| P01 | 为什么是 Slint | 10.44 | — | 3 | 4 | 01 |
| P02 | 搭好环境，跑起第一个程序 | 9.22 | `step01-hello` | 3 | 8 | — |
| P03 | 第一块瓷砖 | 9.72 | `step02-tile` | 5 | 3 | — |
| P04 | 幕布、点击与动画 | 9.56 | `step03-interaction` | 6 | 5 | 03 |
| P05 | 从一块到一片网格 | 9.74 | `step04-grid` | 2 | 9 | — |
| P06 | 游戏规则回到 Rust | 10.09 | `step05-shuffle` | 1 | 10 | 05 |
| P07 | 跑进浏览器与课程收束 | 9.02 | `step06-game-logic` | 2 | 8 | 05 |
| P08 | .slint 文件与组件 | 9.47 | — | 3 | 6 | — |
| P09 | 属性与绑定 | 9.57 | — | 10 | 1 | 01 / 02 |
| P10 | 类型系统 | 10.36 | — | 11 | 2 | 02 |
| P11 | 表达式、语句与函数 | 10.02 | — | 9 | 2 | 02 |
| P12 | 回调与全局单例 | 10.32 | — | 8 | 4 | 03 |
| P13 | 状态与动画 | 9.79 | — | 9 | 3 | 03 |
| P14 | 显式定位与布局元素 | 9.56 | — | 8 | 2 | 04 |
| P15 | std-widgets 与造轮子 | 9.31 | — | 5 | 7 | 05 |
| P16 | 数据模型与跨平台发布 | 9.98 | `step06-game-logic` | 0 | 9 | 05 |

## Memory Game 六步演进

P02–P07 不是六个孤立 demo，而是同一个项目连续长出来的六个快照。想看清「每一步到底新增了什么」，按顺序 diff 相邻两个 `ui/app-window.slint` 最直观。

| 工程 | 视频 | 阶段 | 这一阶段新增 | 运行 |
| --- | --- | --- | --- | --- |
| [`step01-hello`](memory-game/step01-hello/) | P02 | Hello World | Cargo.toml / build.rs / ui / include_modules! 四件套 | `cargo run -p step01-hello` |
| [`step02-tile`](memory-game/step02-tile/) | P03 | 第一块瓷砖 | component MemoryTile inherits Rectangle、@image-url | `cargo run -p step02-tile` |
| [`step03-interaction`](memory-game/step03-interaction/) | P04 | 幕布、点击与动画 | TouchArea、callback、animate width / x | `cargo run -p step03-interaction` |
| [`step04-grid`](memory-game/step04-grid/) | P05 | 从一块到网格 | struct TileData、for tile[i] in ... repeater | `cargo run -p step04-grid` |
| [`step05-shuffle`](memory-game/step05-shuffle/) | P06 | 规则回到 Rust | VecModel、rand 洗牌、set_memory_tiles | `cargo run -p step05-shuffle` |
| [`step06-game-logic`](memory-game/step06-game-logic/) | P07 | 完整游戏 | check_if_pair_solved、disable_tiles、Timer | `cargo run -p step06-game-logic` |

## 目录结构

```
slint-course-kit/
├── Cargo.toml                  # workspace：6 个渐进工程
├── memory-game/                # P02–P07 六个可运行快照
│   └── stepNN-xxx/             # Cargo.toml + build.rs + ui/ + src/ + icons/
├── examples/                   # 85 个编译校验通过的 .slint 示例
├── docs/
│   ├── 学习手册.pdf / .md / .html
│   ├── EXAMPLE_INDEX.md        # 示例 × 视频时间点对照表
│   ├── 版本说明.md             # edition 1.20 与本机 1.18.1 的差异
│   └── snippets/               # 按集整理的 83 段摘录
├── compile-fail/               # 3 个反例 + 实测诊断
├── articles/                   # 5 篇图文长文
├── icons/                      # 8 张自制占位图标（非官方素材）
└── tools/                      # 语法校验器、原始清单、重建脚本
```

## 准确性是怎么保证的

1. **代码有出处**：渐进工程逐字取自 Slint 官方教程源文件 （`slint-video/assets/code/`，MIT）；示例与摘录逐字取自课程逐镜脚本，每个文件头都写了来源、`Pxx mm:ss` 视频定位和「补了什么外壳」。
2. **真的编译过**：6 个工程跑通 `cargo check --workspace --all-targets` 与 `cargo build --workspace`；85 个示例逐个交给 `slint-interpreter 1.18.1` 编译通过。分类不靠猜关键字，靠编译器判定。
3. **时间点来自成品**：`Pxx mm:ss` 取自 `subs/epNN/segments.json` 的真实 TTS 时间轴，并与 `publish.csv` 逐集核对；时长与 `ffprobe` 实测一致。
4. **不硬凑**：引用 `MemoryTile`、`root.rows`、`slider`、`Logic` 的局部片段没有为了编译通过而编造上下文，而是原样保留在摘录里，并指向 `memory-game/` 中的真实完整工程。

**版本差异务必读**：课程依据官方文档（以 edition 1.20 为例），本机可得 crate 最高为 1.18.1。详见 [`docs/版本说明.md`](docs/版本说明.md)。

## 许可

官方文档与教程示例代码为 **MIT**（Copyright © SixtyFPS GmbH）；Slint 框架本体为三重许可。图标为自建占位素材。完整声明见 [`NOTICE.md`](NOTICE.md) 与 [`LICENSE`](LICENSE)。
