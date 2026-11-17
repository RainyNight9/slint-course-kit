"""从 Slint 官方教程源文件还原 6 个可编译的 Memory Game 渐进工程。

代码逐字来自 slint-video/assets/code/ 下的官方文件，仅做两处必要整理：
1. 去掉 #[edition = "1.20"] —— 本机可得的 Slint 1.18.1 不支持该属性；
2. 去掉 // ANCHOR / // ANCHOR_END —— 官方文档的片段锚点，不是代码。
另外把 slint! 宏体拆成独立 ui/app-window.slint（真实项目结构，课程 P02 讲的正是这条路）。
"""
import re
import shutil
import struct
import zlib
from pathlib import Path

SRC = Path('/Users/rain9/WorkBuddy/2026-11-09-15-16-30/slint-video/assets/code')
REPO = Path('/Users/rain9/WorkBuddy/2026-11-09-15-16-30/slint-course-kit')
GAME = REPO / 'memory-game'

ICON_NAMES = ['at', 'balance-scale', 'bicycle', 'bus', 'cloud', 'cogs', 'motorcycle', 'video']
COLORS = [
    (0xE8, 0x5D, 0x4A), (0x3E, 0x9B, 0xD0), (0x4C, 0xAF, 0x6D), (0xE0, 0xA3, 0x2E),
    (0x8E, 0x6B, 0xC8), (0x2F, 0x8F, 0x9E), (0xC2, 0x4B, 0x75), (0x5B, 0x6B, 0x8C),
]
FONT = {
    '1': ['00100', '01100', '00100', '00100', '00100', '00100', '01110'],
    '2': ['01110', '10001', '00001', '00010', '00100', '01000', '11111'],
    '3': ['11110', '00001', '00001', '01110', '00001', '00001', '11110'],
    '4': ['00010', '00110', '01010', '10010', '11111', '00010', '00010'],
    '5': ['11111', '10000', '10000', '11110', '00001', '00001', '11110'],
    '6': ['00110', '01000', '10000', '11110', '10001', '10001', '01110'],
    '7': ['11111', '00001', '00010', '00100', '01000', '01000', '01000'],
    '8': ['01110', '10001', '10001', '01110', '10001', '10001', '01110'],
}


def make_png(path, idx):
    """纯标准库生成 64x64 RGBA 占位图标：不同底色 + 白框 + 白色数字。"""
    w = h = 64
    r, g, b = COLORS[idx]
    pix = [[(r, g, b, 255) for _ in range(w)] for _ in range(h)]
    # 白色边框
    for y in range(h):
        for x in range(w):
            if x < 3 or y < 3 or x >= w - 3 or y >= h - 3:
                pix[y][x] = (255, 255, 255, 255)
    # 中央大号数字（5x7 点阵放大 5 倍）
    glyph = FONT[str(idx + 1)]
    for gy, row in enumerate(glyph):
        for gx, c in enumerate(row):
            if c != '1':
                continue
            for dy in range(5):
                for dx in range(5):
                    yy, xx = 17 + gy * 5 + dy, 17 + gx * 5 + dx
                    pix[yy][xx] = (255, 255, 255, 255)
    raw = b''.join(b'\x00' + bytes(v for px in row for v in px) for row in pix)

    def chunk(tag, data):
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)

    blob = (b'\x89PNG\r\n\x1a\n'
            + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(raw, 9))
            + chunk(b'IEND', b''))
    path.write_bytes(blob)


def clean(text):
    lines = []
    for line in text.splitlines():
        s = line.strip()
        if s.startswith('#[edition'):
            continue
        if s.startswith('// ANCHOR:') or s.startswith('// ANCHOR_END:'):
            continue
        lines.append(line)
    return '\n'.join(lines).strip('\n') + '\n'


def split_macro(text):
    marker = 'slint::slint! {'
    i = text.index(marker)
    rust = text[:i].strip('\n')
    rest = text[i + len(marker):]
    j = rest.rfind('\n}')
    return rust, clean(rest[:j])


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')


HEADER_SLINT = ('// 来源：Slint 官方教程（MIT，Copyright © SixtyFPS GmbH）\n'
                '// 整理：拆出 slint! 宏体为独立 .slint 文件；移除 edition 属性与文档锚点注释。\n'
                '// 视频定位：{stamp}\n\n')
HEADER_RUST = ('// 来源：Slint 官方教程（MIT，Copyright © SixtyFPS GmbH）\n'
               '// 视频定位：{stamp}\n\n')

CARGO = '''[package]
name = "{name}"
version = "0.1.0"
edition = "2021"
publish = false

[dependencies]
slint = "=1.18.1"
{deps}
[build-dependencies]
slint-build = "=1.18.1"
'''
BUILD_RS = '''fn main() {{
    slint_build::compile("ui/app-window.slint").unwrap();
}}
'''

# 6 个阶段：目录名、官方来源文件、对应视频集、说明
STEPS = [
    ('step01-hello',       'app-window.slint',            2, 'Hello World：Cargo.toml / build.rs / ui / include_modules! 四件套'),
    ('step02-tile',        'memory_tile.slint',           3, '第一块瓷砖：component MemoryTile inherits Rectangle 与 @image-url'),
    ('step03-interaction', 'main_polishing_the_tile.rs',  4, '幕布与点击：TouchArea、callback、animate width / x'),
    ('step04-grid',        'main_multiple_tiles.rs',      5, '网格与数据模型：struct TileData、for tile[i] in ... repeater'),
    ('step05-shuffle',     'main_tiles_from_rust.rs',     6, '规则回到 Rust：VecModel、rand 洗牌、set_memory_tiles'),
    ('step06-game-logic',  'main_game_logic_in_rust.rs',  7, '完整游戏：check_if_pair_solved 回调、disable_tiles、Timer 翻回'),
]


def main():
    GAME.mkdir(parents=True, exist_ok=True)
    (REPO / 'icons').mkdir(exist_ok=True)
    for i, name in enumerate(ICON_NAMES):
        make_png(REPO / 'icons' / f'{name}.png', i)

    members = []
    for dirname, srcname, ep, desc in STEPS:
        d = GAME / dirname
        d.mkdir(exist_ok=True)
        src_text = (SRC / srcname).read_text(encoding='utf-8')

        if srcname.endswith('.slint'):
            slint_code = clean(src_text)
            rust_code = ('slint::include_modules!();\n\n'
                         'fn main() {\n'
                         '    MainWindow::new().unwrap().run().unwrap();\n'
                         '}\n')
        else:
            rust_code, slint_code = split_macro(src_text)
            rust_code = 'slint::include_modules!();\n\n' + rust_code + '\n'

        need_rand = 'rand::' in rust_code
        deps = 'rand = "0.9"\n' if need_rand else ''
        write(d / 'Cargo.toml', CARGO.format(name=dirname, deps=deps))
        write(d / 'build.rs', BUILD_RS)
        write(d / 'src' / 'main.rs', HEADER_RUST.format(stamp=f'P{ep:02d}') + rust_code)
        write(d / 'ui' / 'app-window.slint', HEADER_SLINT.format(stamp=f'P{ep:02d}') + slint_code)
        # 官方代码里的 @image-url("icons/...") 相对 .slint 文件解析
        if '@image-url' in slint_code:
            (d / 'ui' / 'icons').mkdir(parents=True, exist_ok=True)
            for name in ICON_NAMES:
                shutil.copy(REPO / 'icons' / f'{name}.png', d / 'ui' / 'icons' / f'{name}.png')
        members.append(f'    "memory-game/{dirname}",')
    members.append('    "tools/slintcheck",')

    write(REPO / 'Cargo.toml',
          '# Slint 16 集课程配套：Memory Game 六个渐进工程\n'
          '# 运行：cargo run -p step06-game-logic\n'
          '[workspace]\nresolver = "2"\nmembers = [\n' + '\n'.join(members) + '\n]\n')

    for dirname, srcname, ep, desc in STEPS:
        print(f'{dirname:22s} P{ep:02d} <- {srcname:32s} {desc}')
    print('icons:', len(ICON_NAMES), 'PNG')


if __name__ == '__main__':
    main()
