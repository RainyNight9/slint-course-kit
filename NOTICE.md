# 来源与许可声明

本仓库是 B 站《Slint 声明式 UI》16 集中文系统课的配套资料，内容来源于 Slint 官方文档与教程示例，并做了中文讲解与结构化整理。

## 1. Slint 官方文档与教程示例代码

- 版权：Copyright © SixtyFPS GmbH <info@slint.dev>
- 许可：**MIT**（官方源文件头部标注 `SPDX-License-Identifier: MIT`）
- 来源：`slint-ui/slint` 仓库的 `docs/astro/src/content/docs/` 与教程示例
  （本地副本：`slint-video/assets/docs/`、`slint-video/assets/code/`）
- 使用方式：摘取、翻译为中文讲解；把官方 `slint!` 宏示例拆成独立的 `.slint` 与 Rust 工程；移除 edition 属性与文档锚点注释。所有改动在文件头与 `docs/版本说明.md` 中说明。

## 2. 中文课程逐镜脚本

本仓库的示例、摘录与学习手册内容取自该课程的逐镜脚本，而该脚本本身是依据上述 MIT 文档改编的中文讲解。

## 3. Slint 框架本体

`slint` / `slint-build` / `slint-interpreter` 等 crate 采用三重许可：

`GPL-3.0-only OR LicenseRef-Slint-Royalty-free-2.0 OR LicenseRef-Slint-Software-3.0`

本仓库**不分发框架源码或二进制**，只在 `Cargo.toml` 中声明依赖，由使用者自行通过 Cargo 获取并遵守其许可。

## 4. 图标

`icons/` 与各工程 `ui/icons/` 下的 8 张 PNG 是本仓库用纯标准库自制的**占位图标**（不同底色 + 编号），不是 Slint 官方素材。文件名与官方教程一致以便对照。

## 5. 本仓库新增部分

生成脚本、索引文档、学习手册排版、图文长文、占位图标等新增内容，同样以 MIT 许可提供，见 `LICENSE`。

## 6. 保留声明

官方源文件头部的版权与 SPDX 标识在还原工程里予以保留；本文件与 `LICENSE` 一并随仓库分发，以满足 MIT 的署名与许可文本随附要求。
