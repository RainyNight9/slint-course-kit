# 生成与校验工具

## 数据文件

- `code_inventory.json`：从课程 16 集逐镜数据中抽出的 **171 个代码镜头**原始清单（集数、镜号、标题、语言、代码、说明、错误标注）。
- `entries.json`：分类结果，每条含 `kind`（example / snippet / compile-fail）、`stamp`（`Pxx mm:ss` 视频定位）、`style`（补了哪种外壳）、实测诊断等。

## slintcheck/

离线 Rust 小工具，依赖本地缓存的 `slint-interpreter =1.18.1`，用 `Compiler::build_from_path` 编译 `.slint` 并输出 JSON 诊断：

```bash
cd tools/slintcheck && cargo build --release
./target/release/slintcheck path/to/a.slint path/to/b.slint
# {"path":"...","ok":false,"errors":["3:5: Unknown element ..."],"warnings":[],"components":[]}
```

它做的是**语法 / 类型层面的编译校验**，不打开窗口、不执行界面逻辑。`--include DIR` 可追加导入搜索路径。

## 重建脚本

| 脚本 | 作用 |
| --- | --- |
| `generate_game.py` | 从官方教程源文件还原 6 个渐进工程 + 占位图标 |
| `generate_examples.py` | 抽 171 段代码、生成包装候选、逐个编译校验、写 examples / snippets / compile-fail |
| `generate_handbook.py` | 生成学习手册 Markdown + HTML |
| `generate_docs.py` | 生成 README、索引、版权与说明文档 |

执行顺序：`generate_game.py` → `generate_examples.py` → `generate_handbook.py` → Chrome 导出 PDF → `generate_docs.py`。

**注意**：`generate_examples.py` 会重建 `examples/`、`docs/snippets/`、`compile-fail/` 三个目录的内容，但不会删除 README / LICENSE / 手册 / 文章。手工改动请先同步进脚本。
