# 故意报错的反例

课程里用来讲解编译器诊断的片段。它们**应当编译失败**，不纳入 workspace，也不在 examples/ 里。

| 文件 | 视频定位 | 标题 | 课程标注的错误 |
|---|---|---|---|
| `p01_s13.slint` | P01 04:59 | 赋值，会掐断绑定 | warning: assignment will overwrite the binding |
| `p04_s17.slint` | P04 05:33 | 两个尺寸谁是源头 | The binding for the property 'text' is part of a binding loop |
| `p14_s11.slint` | P14 03:47 | 子元素撑起父元素 | error: The binding for the property 'text' is part of a binding loop |

## 本机实测

下表是**最终交付的 `.slint` 文件**逐个交给 `slint-interpreter 1.18.1` 编译得到的真实输出，不是照抄课程文案。

| 文件 | Slint 1.18.1 实测 |
|---|---|
| `p01_s13.slint` | 8:1: Parse error: expected a top-level item such as a component, a struct, or a global |
| `p04_s17.slint` | （警告）8:1: Component is implicitly marked for export. This is deprecated and it should be explicitly exported；1:1: Exported component 'Tag' doesn't inherit Window. This is deprecated |
| `p14_s11.slint` | 8:1: Parse error: expected a top-level item such as a component, a struct, or a global |

## 为什么没有复现课程里的诊断

- 课程依据 Slint 官方文档讲解，文档以 **edition 1.20** 为例；本机 crates.io 可获得的最高版本是 **slint 1.18.1**，两套编译行为并不相同。
- `p04_s17` / `p14_s11` 讲的绑定环，来自「**1.19 起 `if` 里的 Text 也参与父元素尺寸计算**」这一布局行为变化（课程 P14 原文即如此说明）。1.18.1 仍按旧行为处理，因此不会报该错误。
- `p01_s13` 的 `assignment will overwrite the binding` 是警告；1.18.1 未输出该警告。
- 三条都是幻灯片上的**节选**，单独交给编译器会先报 parse error——那是「片段不是完整文件」的结果，并不是课程所讲的那类诊断。

如需复现，请在 Slint 1.20 环境下把片段放进完整组件后编译。本仓库选择**逐字保留官方片段 + 如实标注差异**，不为凑出报错而改写或编造上下文。
