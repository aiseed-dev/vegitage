#!/usr/bin/env python3
"""2つのカタログをまとめてビルドする(aiseed.page 公開用)。

  build.py       … イタリア図鑑(Markdown・69) → web/site/{index,italian/}
  build_dict.py  … 世界の伝統野菜辞典(JSON・332) → web/site/vegetables/

build.py がルート index と italian/ を、build_dict.py が vegetables/ を書く。
出力先が分かれているので順序に依存しない。

Usage: python3 web/build_all.py
"""

import subprocess
import sys
from pathlib import Path

WEB = Path(__file__).resolve().parent
PY = sys.executable

for script in ("build.py", "build_dict.py"):
    print(f"\n=== {script} ===")
    r = subprocess.run([PY, str(WEB / script)])
    if r.returncode != 0:
        sys.exit(f"{script} が失敗しました")

print("\n✓ 2カタログのビルド完了 → web/site/")
