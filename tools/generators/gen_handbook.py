#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成《Slint 16 集学习手册》Markdown + 可打印 HTML。

素材全部取自课程现有数据与配套仓库实测结果，不新写知识点：
  slint-video/merge.py      -> 逐镜 narration / rules / statement
  slint-video/deep_*.py    -> objectives / quiz / recap
  slint-video/publish.csv  -> 章节、时长、视频时间轴
  slint-course-kit/tools/entries.json -> 编译校验过的示例、摘录、反例
"""
import csv
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path('/Users/rain9/WorkBuddy/2026-11-09-15-16-30')
COURSE = ROOT / 'slint-video'
REPO = ROOT / 'slint-course-kit'
sys.path.insert(0, str(COURSE))
from merge import load_packs, full_eps  # noqa: E402

PACKS = load_packs()
EPS = full_eps()
ENTRIES = json.loads((REPO / 'tools' / 'entries.json').read_text(encoding='utf-8'))

META = {}
with open(COURSE / 'publish.csv', encoding='utf-8-sig') as f:
    for row in list(csv.reader(f))[1:]:
        ep = int(row[0][1:])
        META[ep] = dict(title=row[1], chap=row[2], minutes=row[3],
                        video=row[4], cover=row[5], timeline=row[6])

GAME_OF_EP = {2: 'step01-hello', 3: 'step02-tile', 4: 'step03-interaction',
              5: 'step04-grid', 6: 'step05-shuffle', 7: 'step06-game-logic',
              16: 'step06-game-logic'}


def strip_tags(s):
    return html.unescape(re.sub(r'<[^>]+>', '', str(s))).strip()


def md_esc(s):
    return (strip_tags(s).replace('|', '\\|').replace('\n', ' ')
            .replace('<', '\\<').replace('>', '\\>'))


def timeline_short(t, limit=9):
    parts = [p.strip() for p in t.split('|') if p.strip()]
    if len(parts) <= limit:
        return parts
    step = len(parts) / limit
    return [parts[min(int(i * step), len(parts) - 1)] for i in range(limit)]


def build(ep):
    n = ep['id']
    m, pack = META[n], PACKS[n]
    scenes = ep['scenes']

    rules, statements = [], []
    for s in scenes:
        v = s.get('view') or {}
        if v.get('k') == 'rules':
            for item in v['items']:
                pair = (strip_tags(item[0]), strip_tags(item[1]))
                if pair not in rules:
                    rules.append(pair)
        elif v.get('k') == 'statement':
            big = strip_tags(v.get('big', ''))
            chips = [strip_tags(c) for c in v.get('chips', [])]
            if big:
                statements.append((big, chips))

    pitfalls = []
    for s in scenes:
        text = s['narration']
        for pat in (r'容易错在([^。]+)', r'注意([^。]{6,60})', r'别([^。]{6,60})',
                    r'坑在([^。]{4,60})', r'容易([^。]{6,60})'):
            for hit in re.findall(pat, text):
                p = hit.strip('，。； ')
                if 8 < len(p) < 90 and p not in pitfalls:
                    pitfalls.append(p)
    pitfalls = pitfalls[:5]

    ex = sorted([e for e in ENTRIES if e['ep'] == n and e['kind'] == 'example'],
                key=lambda x: x['slide'])
    cf = sorted([e for e in ENTRIES if e['ep'] == n and e['kind'] == 'compile-fail'],
                key=lambda x: x['slide'])
    sn = [e for e in ENTRIES if e['ep'] == n and e['kind'] == 'snippet']
    q = pack['quiz']
    m = dict(m)
    raw_timeline = m.pop('timeline')
    return dict(n=n, **m,
                objectives=[(strip_tags(a), strip_tags(b)) for a, b in pack['objectives']],
                rules=rules[:8], statements=statements[:4], pitfalls=pitfalls,
                quiz=(strip_tags(q[0]), strip_tags(q[1]), strip_tags(q[2])),
                recap=[(strip_tags(a), strip_tags(b), strip_tags(c)) for a, b, c in pack['recap']],
                examples=ex, compile_fail=cf, snippets=sn,
                timeline=timeline_short(raw_timeline))


DATA = [build(ep) for ep in EPS]
DIAGS = [e for e in ENTRIES if e['kind'] == 'compile-fail']
COMMANDS = []
for e in ENTRIES:
    if e['kind'] != 'snippet':
        continue
    for line in e['src'].splitlines():
        line = line.strip()
        if re.match(r'^(cargo |wasm-pack |npx |npm |slint-viewer |rustup )', line):
            cmd = line.split('#')[0].strip()
            if cmd and cmd not in COMMANDS and len(cmd) < 90:
                COMMANDS.append(cmd)
TOTAL_MIN = sum(float(d['minutes']) for d in DATA)
N_EX = sum(len(d['examples']) for d in DATA)
N_SNIP = sum(len(d['snippets']) for d in DATA)

GAME_STEPS = [
    ('step01-hello', 'P02', 'Hello World', 'Cargo.toml / build.rs / ui / include_modules! 四件套'),
    ('step02-tile', 'P03', '第一块瓷砖', 'component MemoryTile inherits Rectangle、@image-url'),
    ('step03-interaction', 'P04', '幕布、点击与动画', 'TouchArea、callback、animate width / x'),
    ('step04-grid', 'P05', '从一块到网格', 'struct TileData、for tile[i] in ... repeater'),
    ('step05-shuffle', 'P06', '规则回到 Rust', 'VecModel、rand 洗牌、set_memory_tiles'),
    ('step06-game-logic', 'P07', '完整游戏', 'check_if_pair_solved、disable_tiles、Timer'),
]

# ---------------- Markdown ----------------
md = [
    '# Slint 声明式 UI · 16 集学习手册', '',
    f'> 配套 B 站中文系统课 · 依据 Slint 官方文档整理 · 16 集 / {TOTAL_MIN:.0f} 分钟',
    '> 文档与示例代码为 MIT（Copyright © SixtyFPS GmbH）；框架本身为三重许可，详见仓库 NOTICE.md',
    '',
    '## 这本手册怎么用', '',
    '每一集一节，结构是固定的：', '',
    '1. **本集目标** —— 看完应该能讲清楚的三件事',
    '2. **核心规则 / 关键结论** —— 直接从逐镜脚本里抽出的规则与要记的一句话',
    '3. **容易踩的坑** —— 旁白里点名过的典型误区',
    '4. **随堂练习** —— 视频里暂停让你自己先做的那道题，附讲解',
    '5. **知识地图** —— 三条把本集连回全课的主线',
    '6. **配套代码** —— 编译校验过的示例、摘录、反例，带视频时间点',
    '7. **视频导航** —— 本集主要节点的时间点（完整时间轴见课程 publish.csv）', '',
    f'配套仓库 `slint-course-kit`：6 个渐进可运行工程、{N_EX} 个通过 Slint 编译器校验的示例、'
    f'{N_SNIP} 段讲解摘录、3 个反例。文件名 `p09_s03` 表示 P09 第 3 张幻灯片。', '',
    '## 全课速查', '',
    '### 16 集 × 章节', '',
    '| 集 | 标题 | 对应章节 | 时长(分) | 示例 | 摘录 | 反例 |',
    '| --- | --- | --- | --- | --- | --- | --- |',
]
for d in DATA:
    md.append(f"| P{d['n']:02d} | {md_esc(d['title'])} | {md_esc(d['chap'])} | {d['minutes']} | "
              f"{len(d['examples'])} | {len(d['snippets'])} | {len(d['compile_fail'])} |")

md += ['', '### Memory Game 六个渐进工程', '',
       'P02–P07 是同一个项目逐集长大。仓库里把它还原成 6 个**各自能 `cargo run` 的完整工程**，'
       '代码来自官方教程源文件，只拆开 `slint!` 宏并去掉本机不支持的 edition 属性。', '',
       '| 工程 | 视频 | 阶段 | 这一阶段新增 | 运行命令 |', '| --- | --- | --- | --- | --- |']
for name, ep, stage, desc in GAME_STEPS:
    md.append(f"| `{name}` | {ep} | {stage} | {desc} | `cargo run -p {name}` |")

md += ['', '### 编译诊断速查', '',
       '课程里 3 个「故意写错」的反例，完整说明与本机实测见 `compile-fail/README.md`。', '',
       '| 文件 | 视频定位 | 讲的是什么 | 课程标注的诊断 |', '| --- | --- | --- | --- |']
for x in DIAGS:
    md.append(f"| `{x['base']}.slint` | {x['stamp']} | {md_esc(x['title'])} | {md_esc(x['err'])} |")

md += ['', '### 常用命令速查', '', '```bash']
for c in COMMANDS[:24]:
    md.append(c)
md += ['```', '', '### 配套仓库怎么用', '', '```bash',
       'cargo check --workspace --all-targets              # 校验 6 个渐进工程',
       'cargo run -p step06-game-logic                    # 跑完整的记忆游戏',
       'slint-viewer examples/p09_s03.slint               # 单独预览某个语法示例',
       'cargo run -p slintcheck -- examples/p09_s03.slint # 只做语法编译校验',
       '```', '',
       '### 版本说明（务必读）', '',
       '课程依据 Slint 官方文档讲解，文档以 **edition 1.20** 为例；'
       '本仓库制作时 crates.io 可获得的最高版本是 **Slint 1.18.1**，'
       '因此所有工程锁 `=1.18.1` 并用该版本实测。', '',
       '- 官方示例里的 `#[edition = "1.20"]` 属性在 1.18.1 下会直接解析失败，'
       '还原工程时已移除；其余代码逐字未改。',
       '- 「1.19 起 `if` 里的 Text 也参与父元素尺寸计算」这类行为变化，1.18.1 仍按旧规则，'
       '所以课程 P04 / P14 讲的两处绑定环诊断在本机不会复现。',
       '- 若你使用 Slint 1.20 或更新版本，把 `Cargo.toml` 里的版本改回对应版本并加回 edition 属性即可；'
       '语法主体不受影响。', '',
       '---', '']

for d in DATA:
    n = d['n']
    md += [f"## P{n:02d} · {d['title']}", '',
           f"**{d['chap']}** · 视频 {d['minutes']} 分钟 · `{d['video']}`", '',
           '### 本集目标', '']
    for i, (a, b) in enumerate(d['objectives'], 1):
        md.append(f"{i}. **{md_esc(a)}** —— {md_esc(b)}")
    md.append('')
    if d['rules']:
        md += ['### 核心规则', '']
        for a, b in d['rules']:
            md.append(f"- **{md_esc(a)}** —— {md_esc(b)}")
        md.append('')
    if d['statements']:
        md += ['### 关键结论', '']
        for big, chips in d['statements']:
            md.append(f"- **{md_esc(big)}**" + ('：' + '、'.join(md_esc(c) for c in chips) if chips else ''))
        md.append('')
    if d['pitfalls']:
        md += ['### 容易踩的坑', '']
        md += [f"- {md_esc(p)}。" for p in d['pitfalls']]
        md.append('')
    md += ['### 随堂练习', '', f"**题目**：{md_esc(d['quiz'][0])}", '']
    if d['quiz'][2]:
        md += [f"提示：{md_esc(d['quiz'][2])}", '']
    md += [f"**答案讲解**：{md_esc(d['quiz'][1])}", '', '### 知识地图', '']
    for i, (a, b, tag) in enumerate(d['recap'], 1):
        md.append(f"{i}. **{md_esc(a)}**（{md_esc(tag)}）—— {md_esc(b)}")
    md.append('')
    md += ['### 配套代码', '']
    if n in GAME_OF_EP:
        g = GAME_OF_EP[n]
        md += [f"- 本集完整工程：`memory-game/{g}/`（`cargo run -p {g}`）", '']
    if d['examples']:
        md += ['编译校验通过的独立示例：', '', '| 文件 | 讲解点 | 视频定位 | 预览命令 |',
               '| --- | --- | --- | --- |']
        for x in d['examples']:
            md.append(f"| `{x['base']}.slint` | {md_esc(x['title'])} | {x['stamp']} | "
                      f"`slint-viewer examples/{x['base']}.slint` |")
        md.append('')
    if d['snippets']:
        md.append(f"- 讲解摘录 {len(d['snippets'])} 段：`docs/snippets/p{n:02d}.md`（命令行、配置、宿主语言或局部语法）")
    for x in d['compile_fail']:
        md.append(f"- 反例：`compile-fail/{x['base']}.slint` · {md_esc(x['title'])} · {x['stamp']}")
    md.append('')
    md += ['### 视频导航', '', ' · '.join(md_esc(t) for t in d['timeline']), '', '---', '']

md += ['## 许可', '',
       '内容依据 Slint 官方文档与教程示例（MIT，Copyright © SixtyFPS GmbH）整理，'
       '保留原版权与许可声明；Slint 框架本身采用 Royalty-free / GPLv3 / 商业三重许可。',
       '详见仓库 `LICENSE` 与 `NOTICE.md`。', '']

(REPO / 'docs' / '学习手册.md').write_text('\n'.join(md), encoding='utf-8')


# ---------------- HTML (A4 可打印) ----------------
def h(s):
    return html.escape(strip_tags(s))


def table(headers, rows):
    out = ['<table><thead><tr>' + ''.join(f'<th>{h(x)}</th>' for x in headers) + '</tr></thead><tbody>']
    for r in rows:
        out.append('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>')
    out.append('</tbody></table>')
    return ''.join(out)


parts = []
for d in DATA:
    n = d['n']
    b = [f'<section class="ep"><h2>P{n:02d} · {h(d["title"])}</h2>',
         f'<p class="meta">{h(d["chap"])} · 视频 {d["minutes"]} 分钟 · {h(d["video"])}</p>',
         '<h3>本集目标</h3><ol>']
    for a, bb in d['objectives']:
        b.append(f'<li><strong>{h(a)}</strong> —— {h(bb)}</li>')
    b.append('</ol>')
    if d['rules']:
        b.append('<h3>核心规则</h3><ul>')
        for a, bb in d['rules']:
            b.append(f'<li><strong>{h(a)}</strong> —— {h(bb)}</li>')
        b.append('</ul>')
    if d['statements']:
        b.append('<h3>关键结论</h3><ul>')
        for big, chips in d['statements']:
            b.append(f'<li><strong>{h(big)}</strong>' + ('：' + '、'.join(h(c) for c in chips) if chips else '') + '</li>')
        b.append('</ul>')
    if d['pitfalls']:
        b.append('<h3>容易踩的坑</h3><ul>')
        b += [f'<li>{h(p)}。</li>' for p in d['pitfalls']]
        b.append('</ul>')
    b += ['<h3>随堂练习</h3>', f'<p><strong>题目</strong>：{h(d["quiz"][0])}</p>']
    if d['quiz'][2]:
        b.append(f'<p class="hint">提示：{h(d["quiz"][2])}</p>')
    b.append(f'<p><strong>答案讲解</strong>：{h(d["quiz"][1])}</p>')
    b.append('<h3>知识地图</h3><ol>')
    for a, bb, tag in d['recap']:
        b.append(f'<li><strong>{h(a)}</strong>（{h(tag)}）—— {h(bb)}</li>')
    b.append('</ol>')
    b.append('<h3>配套代码</h3>')
    if n in GAME_OF_EP:
        g = GAME_OF_EP[n]
        b.append(f'<p>完整工程：<code>memory-game/{g}/</code>（<code>cargo run -p {g}</code>）</p>')
    if d['examples']:
        b.append('<p>编译校验通过的独立示例：</p>')
        b.append(table(['文件', '讲解点', '视频定位', '预览命令'], [
            [f'<code>{h(x["base"])}.slint</code>', h(x['title']), h(x['stamp']),
             f'<code>slint-viewer examples/{h(x["base"])}.slint</code>']
            for x in d['examples']]))
    extras = []
    if d['snippets']:
        extras.append(f'讲解摘录 {len(d["snippets"])} 段：<code>docs/snippets/p{n:02d}.md</code>')
    for x in d['compile_fail']:
        extras.append(f'反例 <code>compile-fail/{h(x["base"])}.slint</code> · {h(x["title"])}')
    if extras:
        b.append('<ul>' + ''.join(f'<li>{e}</li>' for e in extras) + '</ul>')
    b += ['<h3>视频导航</h3>', f'<p class="timeline">{" · ".join(h(t) for t in d["timeline"])}</p>',
          '</section>']
    parts.append(''.join(b))

overview = [
    '<h2>这本手册怎么用</h2>',
    '<p>每一集一节：本集目标 → 核心规则 / 关键结论 → 容易踩的坑 → 随堂练习 → 知识地图 → '
    '配套代码（带视频时间点与预览命令）→ 视频导航。文件名 <code>p09_s03</code> 表示 P09 第 3 张幻灯片。</p>',
    '<h2>全课速查 · 16 集 × 章节</h2>',
    table(['集', '标题', '对应章节', '时长(分)', '示例', '摘录', '反例'], [
        [f'P{d["n"]:02d}', h(d['title']), h(d['chap']), d['minutes'],
         str(len(d['examples'])), str(len(d['snippets'])), str(len(d['compile_fail']))] for d in DATA]),
    '<h2>Memory Game 六个渐进工程</h2>',
    '<p>P02–P07 是同一个项目逐集长大。仓库还原为 6 个各自能 <code>cargo run</code> 的完整工程，'
    '代码来自官方教程源文件。</p>',
    table(['工程', '视频', '阶段', '这一阶段新增', '运行命令'], [
        [f'<code>{h(name)}</code>', ep, h(stage), h(desc), f'<code>cargo run -p {h(name)}</code>']
        for name, ep, stage, desc in GAME_STEPS]),
    '<h2>编译诊断速查</h2>',
    table(['文件', '视频定位', '讲的是什么', '课程标注的诊断'], [
        [f'<code>{h(x["base"])}.slint</code>', h(x['stamp']), h(x['title']), h(x['err'])]
        for x in DIAGS]),
    '<h2>常用命令速查</h2>', '<pre>' + h('\n'.join(COMMANDS[:24])) + '</pre>',
    '<h2>配套仓库怎么用</h2>',
    '<pre>' + h('cargo check --workspace --all-targets              # 校验 6 个渐进工程\n'
                'cargo run -p step06-game-logic                    # 跑完整的记忆游戏\n'
                'slint-viewer examples/p09_s03.slint               # 单独预览某个语法示例\n'
                'cargo run -p slintcheck -- examples/p09_s03.slint # 只做语法编译校验') + '</pre>',
    '<h2>版本说明（务必读）</h2>',
    '<p>课程依据 Slint 官方文档讲解，文档以 edition 1.20 为例；本仓库制作时 crates.io 可获得的最高版本是 '
    'Slint 1.18.1，因此所有工程锁 <code>=1.18.1</code> 并用该版本实测。</p>',
    '<ul><li>官方示例里的 <code>#[edition = "1.20"]</code> 在 1.18.1 下会解析失败，还原工程时已移除，其余代码逐字未改。</li>'
    '<li>「1.19 起 if 里的 Text 也参与父元素尺寸计算」这类行为变化，1.18.1 仍按旧规则，'
    '课程 P04 / P14 讲的两处绑定环诊断在本机不会复现。</li>'
    '<li>若使用 Slint 1.20 或更新版本，把 Cargo.toml 里的版本改回对应版本并加回 edition 属性即可，语法主体不受影响。</li></ul>',
]

CSS = """
@page { size: A4; margin: 16mm 15mm 18mm; }
* { box-sizing: border-box; }
body { font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
       font-size: 10.5pt; line-height: 1.7; color: #1f2328; margin: 0; }
.cover { padding: 55mm 0 20mm; page-break-after: always; border-bottom: none; }
.cover .kicker { color: #0B6E99; font-size: 12pt; letter-spacing: .12em; margin-bottom: 14mm; }
.cover h1 { font-size: 30pt; line-height: 1.35; margin: 0 0 8mm; font-weight: 600; }
.cover .sub { font-size: 13pt; color: #57606a; margin-bottom: 24mm; }
.cover .facts { border-top: 2px solid #0B6E99; padding-top: 6mm; font-size: 11pt; color: #57606a; }
h2 { font-size: 17pt; color: #0B6E99; border-bottom: 1.5px solid #d0d7de;
     padding-bottom: 2mm; margin: 10mm 0 5mm; }
h3 { font-size: 12pt; color: #0A4F78; margin: 6mm 0 2.5mm; }
p { margin: 2mm 0; }
ul, ol { margin: 2mm 0; padding-left: 6mm; }
li { margin: 1mm 0; }
code { font-family: "SF Mono", Menlo, Consolas, monospace; font-size: 9pt;
       background: #f1f3f5; padding: 0 1.2mm; border-radius: 2px; }
pre { background: #f6f8fa; border: 1px solid #d0d7de; border-radius: 4px;
      padding: 4mm; font-size: 9pt; line-height: 1.5; white-space: pre-wrap; }
table { width: 100%; border-collapse: collapse; font-size: 9pt; margin: 3mm 0 5mm; }
th { background: #E3F2FB; color: #084B6B; text-align: left; font-weight: 600; }
th, td { border: 0.5px solid #d0d7de; padding: 1.8mm 2mm; vertical-align: top; }
tr:nth-child(even) td { background: #fafbfc; }
.meta { color: #57606a; font-size: 9.5pt; }
.hint { color: #854F0B; }
.timeline { color: #57606a; font-size: 9pt; }
.ep { page-break-before: always; }
.ep:first-of-type { page-break-before: auto; }
strong { font-weight: 600; }
@media screen { body { padding: 0 15mm 10mm; } .cover { padding-top: 30mm; } }
"""

doc = f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">
<title>Slint 声明式 UI · 16 集学习手册</title><style>{CSS}</style></head><body>
<div class="cover">
  <div class="kicker">B 站中文系统课 · 配套资料</div>
  <h1>Slint 声明式 UI<br>16 集学习手册</h1>
  <div class="sub">依据 Slint 官方文档整理 · 目标 / 规则 / 坑 / 练习 / 知识地图 / 代码索引</div>
  <div class="facts">16 集 · {TOTAL_MIN:.0f} 分钟视频 · 6 个渐进工程 · {N_EX} 个编译校验示例<br>
  文档与示例代码：MIT（Copyright © SixtyFPS GmbH）</div>
</div>
<section>{''.join(overview)}</section>
{''.join(parts)}
</body></html>"""
(REPO / 'docs' / '学习手册.html').write_text(doc, encoding='utf-8')

print(f'handbook: {len(md)} lines, {TOTAL_MIN:.0f} min, examples {N_EX}, snippets {N_SNIP}, '
      f'diags {len(DIAGS)}, commands {len(COMMANDS)}')
