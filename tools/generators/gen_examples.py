"""把 Slint 课程 171 个代码镜头分类成可编译示例 / 摘录 / 故意报错反例。

分类依据不是关键字猜测，而是「逐个交给 slint-interpreter 真编译」：
每个片段生成若干种最小包装（补组件外壳、补 std-widgets 导入等），
第一个能编译通过的包装即为 examples/*.slint；全部失败的进 docs/snippets/。
"""
import html
import json
import re
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path('/Users/rain9/WorkBuddy/2026-11-09-15-16-30')
VIDEO = ROOT / 'slint-video'
REPO = ROOT / 'slint-course-kit'
CHECKER = REPO / 'tools/slintcheck/target/release/slintcheck'
CAND = REPO / 'tools' / '_cand'
INV = REPO / 'tools' / 'code_inventory.json'


def ensure_inventory():
    """清单不在仓库里时，直接从课程逐镜数据重新抽取，保证脚本可独立重跑。"""
    if INV.exists():
        return
    sys.path.insert(0, str(VIDEO))
    from merge import full_eps
    items = []
    for e in full_eps():
        for i, s in enumerate(e['scenes'], 1):
            v = s.get('view') or {}
            if v.get('k') == 'code':
                items.append(dict(ep=e['id'], slide=i + 1, title=s.get('title', ''),
                                  lang=v.get('lang', 'slint'), src=v.get('src', ''),
                                  cap=v.get('cap', ''), err=v.get('err', '')))
    INV.parent.mkdir(parents=True, exist_ok=True)
    INV.write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding='utf-8')


ensure_inventory()

WIDGET_IMPORT = ('import { Button, VerticalBox, HorizontalBox, GridBox, Slider, '
                 'CheckBox, LineEdit, Palette, StandardButton, ProgressIndicator, '
                 'SpinBox, ComboBox, TabWidget, GroupBox, TextEdit, ScrollView, '
                 'ListView, Switch, AboutSlint } from "std-widgets.slint";\n')


def clean_title(t):
    return html.unescape(re.sub(r'<[^>]+>', '', str(t))).strip()


def stamp_of(ep, slide):
    f = VIDEO / 'subs' / f'ep{ep:02d}' / 'segments.json'
    if not f.exists():
        return f'P{ep:02d} --:--'
    segs = json.loads(f.read_text(encoding='utf-8'))
    hit = next((s for s in segs if s['n'] == slide), None)
    if hit is None:
        return f'P{ep:02d} --:--'
    sec = int(hit['start'])
    return f'P{ep:02d} {sec // 60:02d}:{sec % 60:02d}'


def indent(src, n=4):
    return '\n'.join((' ' * n + l if l.strip() else '') for l in src.strip('\n').splitlines())


def candidates(src):
    """按优先级返回包装候选；核心片段逐字保留，只在外部补最小外壳。"""
    s = src.strip('\n')
    out = []
    # 1. 原样（已经是完整顶层声明）
    out.append(('原样', s + '\n'))
    # 2. 纯声明/片段：后面补一个空组件，保证有可导出组件
    out.append(('补空组件', s + '\n\nexport component App inherits Window { }\n'))
    # 3. 包进 Window / 普通组件（属性声明、元素、repeat、动画等）
    for kind, head in [('包进 Window', 'export component Example inherits Window {'),
                       ('包进组件', 'export component Example {')]:
        out.append((kind, head + '\n' + indent(s) + '\n}\n'))
        out.append((kind + '+控件库', WIDGET_IMPORT + head + '\n' + indent(s) + '\n}\n'))
    # 4. 原样但补控件库导入
    out.append(('补控件库导入', WIDGET_IMPORT + s + '\n'))
    # 5. 含 import 的局部片段：把 import 提到顶层，其余包进 Window（只重排，不改代码）
    imp = [l for l in s.splitlines() if l.strip().startswith('import ')]
    rest = '\n'.join(l for l in s.splitlines() if not l.strip().startswith('import '))
    if imp and rest.strip():
        out.append(('import 置顶+包进 Window',
                    '\n'.join(imp) + '\nexport component Example inherits Window {\n'
                    + indent(rest) + '\n}\n'))
    return out


def cf_wrappers(src):
    """反例片段的最小上下文补全：只为触发课程所讲的诊断，核心片段逐字不变。"""
    s = src.strip('\n')
    out = [('原样', s + '\n')]
    out.append(('包进 Window',
                'export component Example inherits Window {\n' + indent(s) + '\n}\n'))
    out.append(('包进 Window + TouchArea id',
                'export component Example inherits Window {\n'
                '    ta := TouchArea { }\n' + indent(s) + '\n}\n'))
    m = re.search(r'\bcomponent\s+(\w+)', s)
    if m:
        out.append(('实例化组件',
                    s + f'\n\nexport component App inherits Window {{ {m.group(1)} {{ }} }}\n'))
    return out


def run_checker(paths):
    """分批调用校验器，返回 path -> 结果。"""
    res = {}
    paths = list(paths)
    for i in range(0, len(paths), 120):
        batch = paths[i:i + 120]
        r = subprocess.run([str(CHECKER)] + [str(p) for p in batch],
                           capture_output=True, text=True, timeout=300)
        for line in r.stdout.splitlines():
            try:
                d = json.loads(line)
                res[d['path']] = d
            except Exception:
                pass
    return res


def main():
    items = json.loads(INV.read_text(encoding='utf-8'))
    EX = REPO / 'examples'
    SNIP = REPO / 'docs' / 'snippets'
    CF = REPO / 'compile-fail'
    for d in (EX, SNIP, CF):
        d.mkdir(parents=True, exist_ok=True)

    # 候选目录（含图标，供 @image-url 解析）
    if CAND.exists():
        shutil.rmtree(CAND)
    CAND.mkdir()
    (CAND / 'icons').mkdir()
    for p in (REPO / 'icons').glob('*.png'):
        shutil.copy(p, CAND / 'icons' / p.name)

    # 生成全部候选
    cands = {}
    for x in items:
        ep, slide = x['ep'], x['slide']
        base = f'p{ep:02d}_s{slide:02d}'
        x['base'] = base
        x['stamp'] = stamp_of(ep, slide)
        x['title'] = clean_title(x['title'])
        x['cap'] = clean_title(x['cap'])
        x['err'] = clean_title(x['err'])
        cands[base] = []
        for cidx, (style, code) in enumerate(candidates(x['src'])):
            p = CAND / f'{base}__{cidx}.slint'
            p.write_text(code, encoding='utf-8')
            cands[base].append((cidx, style, code, p))

    allpaths = [p for v in cands.values() for _, _, _, p in v]
    print('candidate files:', len(allpaths))
    results = run_checker(allpaths)
    print('checked:', len(results))

    entries = []
    chosen = {}
    for x in items:
        base = x['base']
        win = None
        for cidx, style, code, p in cands[base]:
            d = results.get(str(p))
            if d and d['ok']:
                win = (cidx, style, code)
                break
        x['candidates'] = len(cands[base])
        if x['err']:
            # 课程节选反例：逐字保留，不补外壳（补了就等于替官方编造上下文）
            x['kind'] = 'compile-fail'
            x['style'] = '故意报错（课程节选）'
            (CF / f'{base}.slint').write_text(
                f"// {x['title']}\n// 视频定位：{x['stamp']}\n"
                f"// 课程标注的诊断：{x['err']}\n"
                '// 来源：Slint 官方中文课程逐镜脚本，片段逐字保留，未补任何外壳。\n'
                '// 这是幻灯片上的节选，不是完整可编译单元；课程所讲的诊断需在完整组件中触发。\n'
                '// 本机 Slint 1.18.1 实测结果见 compile-fail/README.md。\n\n'
                + cands[base][0][2], encoding='utf-8')
        elif win:
            cidx, style, code = win
            x['kind'] = 'example'
            x['style'] = style
            (EX / f'{base}.slint').write_text(
                f'// {x["title"]}\n// 视频定位：{x["stamp"]}\n'
                f'// 来源：Slint 官方中文课程逐镜脚本；核心片段逐字保留，'
                f'仅为独立编译补了「{style}」外壳。\n'
                f'// 校验：slint-interpreter 1.18.1 编译通过\n\n' + code,
                encoding='utf-8')
            chosen[base] = style
        else:
            x['kind'] = 'snippet'
            x['style'] = '教学摘录'
            first_error = ''
            for cidx, style, code, p in cands[base]:
                d = results.get(str(p))
                if d and d['errors']:
                    first_error = d['errors'][0]
                    break
            x['reason'] = first_error or '命令行 / 配置 / 宿主语言或跨版本语法示例'
        entries.append(x)

    # 摘录文档按集汇总
    byep = {}
    for x in entries:
        if x['kind'] == 'snippet':
            byep.setdefault(x['ep'], []).append(x)
    GAME_OF_EP = {
        2: 'step01-hello', 3: 'step02-tile', 4: 'step03-interaction',
        5: 'step04-grid', 6: 'step05-shuffle', 7: 'step06-game-logic',
        16: 'step06-game-logic',
    }
    for ep, xs in sorted(byep.items()):
        lines = [f'# P{ep:02d} · 讲解摘录', '',
                 '以下片段是课程幻灯片上的教学摘录：命令行、Cargo.toml、宿主语言（Rust / C++ / JS / Python）、'
                 '跨版本语法对照、伪代码，或必须嵌在父组件里才有意义的局部语法。'
                 '它们**不是独立可编译的 .slint 文件**，代码片段按原样保留。', '']
        if ep in GAME_OF_EP:
            d = GAME_OF_EP[ep]
            lines += [f'> 本集的完整可运行上下文在 [`memory-game/{d}/`](../../memory-game/{d}/)，'
                      f'其中 `ui/app-window.slint` 与 `src/main.rs` 含这些片段引用的 '
                      '`MemoryTile`、`TileData`、`MainWindow` 等定义。运行：'
                      f'`cargo run -p {d}`', '']
        for x in xs:
            lines += [f"## P{ep:02d} {x['stamp'].split()[1]} · {x['title']}", '']
            if x['cap']:
                lines += [x['cap'], '']
            lang = 'rust' if x['lang'] == 'rust' else 'slint'
            if re.search(r'cargo |# 安装|\[package\]|\[dependencies\]|\[target\.', x['src']):
                lang = 'toml' if not x['src'].lstrip().startswith('#') else 'bash'
            lines += [f'```{lang}', x['src'].strip('\n'), '```', '',
                      f"- 镜号：第 {x['slide']} 镜 · 视频定位 `{x['stamp']}`",
                      f"- 未纳入独立示例的原因：{x['reason']}", '']
            if ep in GAME_OF_EP and re.search(r'MemoryTile|TileData|MainWindow|memory_tiles|check_if_pair_solved', x['src']):
                lines += [f"- 完整定义见 [`memory-game/{GAME_OF_EP[ep]}/ui/app-window.slint`]"
                          f"(../../memory-game/{GAME_OF_EP[ep]}/ui/app-window.slint)", '']
        (SNIP / f'p{ep:02d}.md').write_text('\n'.join(lines), encoding='utf-8')

    # compile-fail 索引
    cfs = [x for x in entries if x['kind'] == 'compile-fail']
    lines = ['# 故意报错的反例', '',
             '课程里用来讲解编译器诊断的片段。它们**应当编译失败**，不纳入 workspace，也不在 examples/ 里。', '',
             '| 文件 | 视频定位 | 标题 | 课程标注的错误 |', '|---|---|---|---|']
    for x in cfs:
        lines.append(f"| `{x['base']}.slint` | {x['stamp']} | {x['title']} | {x['err'][:70]} |")
    final_res = run_checker([CF / f"{x['base']}.slint" for x in cfs])
    lines += ['', '## 本机实测', '',
             '下表是**最终交付的 `.slint` 文件**逐个交给 `slint-interpreter 1.18.1` 编译得到的真实输出，'
             '不是照抄课程文案。', '',
             '| 文件 | Slint 1.18.1 实测 |', '|---|---|']
    for x in cfs:
        d = final_res.get(str(CF / f"{x['base']}.slint"), {})
        errs = d.get('errors', [])
        warns = d.get('warnings', [])
        if errs:
            msg = '；'.join(errs[:2])[:180]
        elif warns:
            msg = '（警告）' + '；'.join(warns[:2])[:180]
        else:
            msg = '编译通过'
        lines.append(f"| `{x['base']}.slint` | {msg} |")
    lines += ['', '## 为什么没有复现课程里的诊断', '',
              '- 课程依据 Slint 官方文档讲解，文档以 **edition 1.20** 为例；本机 crates.io 可获得的最高版本是 '
              '**slint 1.18.1**，两套编译行为并不相同。',
              '- `p04_s17` / `p14_s11` 讲的绑定环，来自「**1.19 起 `if` 里的 Text 也参与父元素尺寸计算**」'
              '这一布局行为变化（课程 P14 原文即如此说明）。1.18.1 仍按旧行为处理，因此不会报该错误。',
              '- `p01_s13` 的 `assignment will overwrite the binding` 是警告；1.18.1 未输出该警告。',
              '- 三条都是幻灯片上的**节选**，单独交给编译器会先报 parse error——那是「片段不是完整文件」的结果，'
              '并不是课程所讲的那类诊断。', '',
              '如需复现，请在 Slint 1.20 环境下把片段放进完整组件后编译。'
              '本仓库选择**逐字保留官方片段 + 如实标注差异**，不为凑出报错而改写或编造上下文。', '']
    (CF / 'README.md').write_text('\n'.join(lines), encoding='utf-8')

    (REPO / 'tools' / 'entries.json').write_text(
        json.dumps(entries, ensure_ascii=False, indent=1), encoding='utf-8')
    shutil.copy(INV, REPO / 'tools' / 'code_inventory.json')

    print('kinds:', dict(Counter(x['kind'] for x in entries)))
    print('styles:', dict(Counter(x['style'] for x in entries)))
    print('per ep examples:', dict(sorted(Counter(x['ep'] for x in entries if x['kind'] == 'example').items())))


if __name__ == '__main__':
    main()
