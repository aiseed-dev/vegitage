# DESIGN: Vegitage Web版の Cloudflare Pages 公開

日付: 2026-07-08(2026-07-09 決定反映)
状態: 承認済み・実装済み(デプロイ待ち)

## 決定事項(2026-07-09)

- 外部フェッチは全廃(案2): CanvasKit 同梱版 + Noto Sans CJK JP サブセット同梱
- 公開先は **aiseed.page 本体**(Pages プロジェクト `vegitage` にカスタムドメインを付与、
  GCE からの切替)

## 目的

vegitage(Flutter アプリ)の Web 版を Cloudflare Pages で公開する。
現行の GCE + Nginx(aiseed.page)からの移行第一歩。将来的な seed-project への
組み込みは本設計の範囲外(アプリ本体には手を入れない)。

## 現状把握(ローカル検証済み)

- アプリは完全静的: 野菜データ(12MB, JSON)と基本画像はアセット同梱。
  バックエンド API への依存なし(backend/ ディレクトリは空)。
- Flutter 3.44.4 でリリースビルド成功。成果物 55MB / 707 ファイルで
  Pages の制限(25MiB/ファイル、20,000 ファイル)内。
- ローカル配信で一覧・検索・詳細・ディープリンク(`/#/vegetables/{id}`)の
  動作を確認。ハッシュ戦略なので Pages 側の SPA フォールバックは不要。
- 詳細画面の写真カルーセルは実行時に
  `https://aiseed.page/images/{category}/{id}/info.json` を取得するが、
  1. aiseed.page に CORS ヘッダーがなく、**別オリジンからは全てブロックされる**
  2. そもそも本番サーバーでも info.json は 404(写真データ未配置)
  つまり写真は現状どこでも表示されておらず、Pages 移行で見た目の回帰はない。
  取得失敗時はカルーセル非表示で自然に劣化することを確認済み。
- QR コード生成は `https://aiseed.page/#/vegetables/{id}` を直書き
  (ドメインを将来 Pages に向ければそのまま生きる)。

## 方針(実装済み)

1. **ビルド**:
   ```bash
   flutter build web --release --dart-define=FLUTTER_WEB_CANVASKIT_URL=canvaskit/
   ```
   `--dart-define` で CanvasKit を gstatic CDN でなく同梱版から読む。
   成果物は `frontend/vegitage/build/web`。リポジトリにはコミットしない。
2. **フォント同梱**: `tool/subset_fonts.py` がシステムの Noto Sans CJK JP
   (fonts-noto-cjk、OFL 1.1)から、データ + ソース中の全文字 + 基本レンジ
   (計約3,800字、韓国語名のハングル含む)をサブセット化し
   `assets/fonts/NotoSansCJKjp-{Regular,Medium,Bold}.otf`(各約1.4MB)を生成。
   pubspec の fonts に登録し、テーマの fontFamily に指定。
   ライセンス表記は `assets/fonts/OFL.txt`。
   **野菜データを更新したら再実行**(収録外の文字は gstatic フォールバックを誘発)。
3. **デプロイ**: cf-publish で Pages プロジェクト `vegitage` へ Direct Upload。
   ```bash
   ~/dev/cf-publish/.venv/bin/cf-publish frontend/vegitage/build/web --project vegitage
   ```
   デプロイ実行はユーザー自身(外部接続の承認ルール)。
4. **ドメイン切替**(ユーザー作業、ダッシュボード):
   Pages プロジェクト `vegitage` → Custom domains → `aiseed.page` を追加
   (DNS は既に Cloudflare にあるためワンクリック)。切替後 GCE は停止可能。
   `aiseed.page/images/*` は 404 になるが、現状も 404 のため回帰なし。
   QR コードの `https://aiseed.page/#/vegetables/{id}` はそのまま生きる。
5. **index.html の小修正**(実施済み):
   - `<title>` 二重定義を解消(日本語タイトルを有効化)
   - `og:image` のドメイン誤記(vegitate.dev)を
     `https://aiseed.page/icons/Icon-512.png` に修正
6. **Zed タスク**: `.zed/tasks.json` に web ビルド / フォント再生成 /
   デプロイ(dry-run・本番) / ローカル確認を追加。

## 決定が必要な点

### A. 外部フェッチ(gstatic)の扱い

ローカル検証で確認した実行時の外部取得は以下(いずれも Google の gstatic):

- CanvasKit 本体(www.gstatic.com、wasm 約1.5MB)
  — ビルド成果物にも canvaskit/ は同梱されているが、既定では CDN を向く
- Roboto + Noto Sans JP のフォールバックフォント
  (fonts.gstatic.com、表示文字に応じたチャンク約40ファイル)

「Web フォントを使わない」方針との整合をどうするか。

- 案1: **現状のまま**(gstatic フェッチを許容)。追加作業ゼロ。
  方針はシステムフォントスタックが使える通常サイト向けで、
  文字を自前描画する Flutter Web は適用外という整理。CDN 側のキャッシュが
  効くので初回ロードはむしろ速い。
- 案2: **全て自己ホスト**。CanvasKit は
  `--dart-define=FLUTTER_WEB_CANVASKIT_URL=canvaskit/` で同梱版を使用、
  日本語フォントは Noto Sans JP をアセット同梱し既定 fontFamily に指定。
  外部フェッチは消えるが、初回ロードが +数MB(フォントのサブセット化で軽減可)。

### B. Pages プロジェクト名

`vegitage`(→ vegitage.pages.dev)を想定。変更あれば指定。

## やらないこと

- アプリ機能・画面の変更、seed-project 統合
- 写真の R2 移行と aiseed.page ドメイン切替(次フェーズ)
- wasm ビルド(COOP/COEP ヘッダー要件が増えるだけで今は利益なし)
