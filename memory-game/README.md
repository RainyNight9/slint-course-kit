# Memory Game · 六个渐进工程

课程 P02–P07 用同一个记忆翻牌游戏串起 Slint 基础：从 Hello World 一路长到完整游戏逻辑。这里把它还原成 6 个**各自独立、各自能跑**的 Cargo 工程。

每个工程结构一致：

```
stepNN-xxx/
├── Cargo.toml            # slint 运行时依赖 + slint-build 构建依赖（P06 起另加 rand）
├── build.rs              # 编译期把 ui/app-window.slint 编进来
├── ui/app-window.slint   # 界面（本阶段重点看这个）
├── ui/icons/             # 8 张占位图标（@image-url 用）
└── src/main.rs           # 宿主逻辑（P01–P05 只有几行，P06 起有游戏规则）
```

| 工程 | 视频 | 阶段 | 这一阶段新增 | 运行 |
| --- | --- | --- | --- | --- |
| [`step01-hello`](step01-hello/) | P02 | Hello World | Cargo.toml / build.rs / ui / include_modules! 四件套 | `cargo run -p step01-hello` |
| [`step02-tile`](step02-tile/) | P03 | 第一块瓷砖 | component MemoryTile inherits Rectangle、@image-url | `cargo run -p step02-tile` |
| [`step03-interaction`](step03-interaction/) | P04 | 幕布、点击与动画 | TouchArea、callback、animate width / x | `cargo run -p step03-interaction` |
| [`step04-grid`](step04-grid/) | P05 | 从一块到网格 | struct TileData、for tile[i] in ... repeater | `cargo run -p step04-grid` |
| [`step05-shuffle`](step05-shuffle/) | P06 | 规则回到 Rust | VecModel、rand 洗牌、set_memory_tiles | `cargo run -p step05-shuffle` |
| [`step06-game-logic`](step06-game-logic/) | P07 | 完整游戏 | check_if_pair_solved、disable_tiles、Timer | `cargo run -p step06-game-logic` |

## 怎么对照视频

按集顺序，把相邻两个工程的 `ui/app-window.slint` 做 diff：

```bash
diff -u memory-game/step02-tile/ui/app-window.slint \
          memory-game/step03-interaction/ui/app-window.slint
```

课程里那些只露出半截的片段（引用 `MemoryTile`、`TileData`、`MainWindow` 的），完整定义都在这里；[`docs/snippets/`](../docs/snippets/) 的每集文档也指到了对应工程。

## 代码来源与改动

逐字来自 Slint 官方教程示例（`slint-video/assets/code/`，MIT / Copyright © SixtyFPS GmbH）。仅三处整理：

1. 把 `slint::slint! { ... }` 宏体拆成独立 `.slint` 文件；
2. 移除 `#[edition = "1.20"]`（本机 1.18.1 不支持，详见 [`docs/版本说明.md`](../docs/版本说明.md)）；
3. 移除 `// ANCHOR` 文档锚点注释。

`cargo check --workspace --all-targets` 与 `cargo build --workspace` 均已实测通过。
