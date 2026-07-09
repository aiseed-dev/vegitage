#!/usr/bin/env python3
"""Noto Sans CJK JP をアプリで使う文字だけにサブセット化して assets/fonts/ に出力する。

Web版で外部フォント(fonts.gstatic.com)を取得しないための同梱フォントを生成する。
アセットデータ(assets/data/**/*.json)と Dartソース(lib/**/*.dart)に現れる
全文字 + 基本レンジ(ASCII/かな/全角記号など)を収録する。

野菜データを追加・更新したら再実行すること。収録外の文字が画面に出ると
Flutter は Google Fonts へのフォールバック取得を試みてしまう。

使い方:
    python3 -m venv .venv-fonts && .venv-fonts/bin/pip install fonttools
    .venv-fonts/bin/python tool/subset_fonts.py

入力フォント: システムの fonts-noto-cjk パッケージ(OFL 1.1)。
"""

import glob
import io
import os
import sys

from fontTools.subset import Options, Subsetter
from fontTools.ttLib import TTCollection

APP_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TTC_DIR = "/usr/share/fonts/opentype/noto"
OUT_DIR = os.path.join(APP_ROOT, "assets", "fonts")

# Material のテキストスタイルが使う 400/500/700 の3ウェイトを収録
WEIGHTS = {
    "Regular": "NotoSansCJK-Regular.ttc",
    "Medium": "NotoSansCJK-Medium.ttc",
    "Bold": "NotoSansCJK-Bold.ttc",
}

# データに無くても必ず収録する基本レンジ
BASE_RANGES = [
    (0x0020, 0x007E),  # ASCII
    (0x00A1, 0x00FF),  # Latin-1 補助
    (0x2000, 0x206F),  # 一般句読点(…‥“”など)
    (0x3000, 0x303F),  # CJK記号(、。「」など)
    (0x3041, 0x309F),  # ひらがな
    (0x30A0, 0x30FF),  # カタカナ
    (0xFF00, 0xFFEF),  # 全角英数・半角カナ
]


def collect_chars():
    chars = set()
    patterns = [
        os.path.join(APP_ROOT, "assets", "data", "**", "*.json"),
        os.path.join(APP_ROOT, "lib", "**", "*.dart"),
    ]
    for pattern in patterns:
        for path in glob.glob(pattern, recursive=True):
            with open(path, encoding="utf-8") as f:
                chars.update(f.read())
    for lo, hi in BASE_RANGES:
        chars.update(chr(cp) for cp in range(lo, hi + 1))
    return {c for c in chars if ord(c) >= 0x20}


def find_jp_font(ttc_path):
    collection = TTCollection(ttc_path, lazy=True)
    for font in collection.fonts:
        names = font["name"]
        # Regular は "Noto Sans CJK JP"、他は "Noto Sans CJK JP Medium" 等
        family = names.getDebugName(1) or ""
        if family.startswith("Noto Sans CJK JP"):
            return font
    raise SystemExit(f"Noto Sans CJK JP not found in {ttc_path}")


def main():
    chars = collect_chars()
    print(f"収録文字数: {len(chars)}")
    os.makedirs(OUT_DIR, exist_ok=True)

    for style, ttc_name in WEIGHTS.items():
        font = find_jp_font(os.path.join(TTC_DIR, ttc_name))
        options = Options()
        options.name_IDs = ["*"]  # ライセンス表記等の name テーブルは残す
        subsetter = Subsetter(options)
        subsetter.populate(text="".join(chars))
        subsetter.subset(font)

        out_path = os.path.join(OUT_DIR, f"NotoSansCJKjp-{style}.otf")
        # TTC メンバーは直接 save できないためメモリ経由で書き出す
        buf = io.BytesIO()
        font.save(buf)
        with open(out_path, "wb") as f:
            f.write(buf.getvalue())
        print(f"{out_path}: {os.path.getsize(out_path) / 1024:.0f} KB")


if __name__ == "__main__":
    sys.exit(main())
