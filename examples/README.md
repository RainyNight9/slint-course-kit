# 独立语法示例

共 85 个 `.slint` 文件，全部经 `slint-interpreter 1.18.1` **编译通过**。

这些文件由课程逐镜脚本里的代码片段整理而来：核心片段**逐字保留**，只为让它成为独立可编译的单元，补了最小外壳（例如 `export component Example inherits Window { ... }` 或 `import { ... } from "std-widgets.slint";`）。每个文件头都写明补的是哪一种外壳。

依赖上下文的局部片段（引用 `MemoryTile`、`TileData`、`root.rows`、`slider`、`Logic` 等）没有硬补一个假组件，而是原样放在 [`docs/snippets/`](../docs/snippets/) 并指向 [`memory-game/`](../memory-game/) 里的真实工程。

## 预览与校验

```bash
slint-viewer examples/p09_s03.slint                 # 需要 cargo install slint-viewer
cargo run -p slintcheck -- examples/p09_s03.slint  # 只编译，不开窗口
cargo run -p slintcheck -- examples/*.slint        # 批量校验全部示例
```

完整清单（含视频时间点）见 [`docs/EXAMPLE_INDEX.md`](../docs/EXAMPLE_INDEX.md)。
