# 生成脚本

本仓库全部内容可由课程逐镜数据自动重建，四个脚本按依赖顺序执行：

1. `gen_memory_game.py` —— 用官方教程源文件（`slint-video/assets/code/`）
   还原 Memory Game 六个渐进工程（`memory-game/step01..06`）。
2. `gen_examples.py` —— 把课程 171 个代码镜头逐个交给 `slint-interpreter`
   真编译，能编译的进 `examples/`，不能的按集归入 `docs/snippets/`，
   故意报错的进 `compile-fail/`（附本机实测诊断）。
3. `gen_handbook.py` —— 从课程深潜数据生成 `docs/学习手册.md` / `.html`。
4. `gen_docs.py` —— 生成 `README.md`、`docs/EXAMPLE_INDEX.md`、`NOTICE.md`、
   `docs/版本说明.md` 等索引与版权文档。

注意事项：

- 脚本里的路径写死了本机制作时的目录（`ROOT` 常量），迁移环境时需要改。
- `slintcheck` 校验器需先 `cargo build --release -p slintcheck`。
- `gen_examples.py` 的分类结论依赖本机 Slint 1.18.1 的实际诊断输出，
  换版本重跑，`compile-fail/` 的实测结论表会如实更新。
- `gen_docs.py` 会覆盖 README / NOTICE 等文档，手工改动请先备份。
