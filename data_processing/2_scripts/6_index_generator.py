import json
from typing import Dict, Any, List

import config

VEGETABLE_SUMMARY_DIR = config.APP_DATA / "vegetable_summary"
INDEX_JSON_FILE = config.PROCESSING_DATA / "_index.json"

class IndexGenerator:
    """
    野菜データから _index.json の内容を生成するためのクラス。
    """

    def __init__(self):
        self._index_items: List[Dict[str, Any]] = []
        self._processed_ids: set[str] = set()

    def add_vegetable(self, veg_data: Dict[str, Any]):
        """
        一つの野菜データを処理し、インデックス項目を追加して、成功したかどうかを返す。
        """
        # --- 1. 必須情報を抽出 ---
        global_info = veg_data.get("global_info", {})
        content_ja = veg_data.get("content", {}).get("ja", {})

        item_id = global_info.get("url")
        display_name = content_ja.get("display_name")
        oneliner = content_ja.get("oneliner")
        kana_name = global_info.get("kana_name")

        if not all([item_id, display_name, oneliner, kana_name]):
            print(f"警告: 必須項目(url, display_name, oneliner, kana_name)が不足。スキップします。")
            return

        # 重複チェック
        if item_id in self._processed_ids:
            print(f"警告: ID '{item_id}' が重複しています。スキップします。")
            return
        self._processed_ids.add(item_id)

        # --- 2. 検索キーを生成 ---
        search_keys = self._create_search_keys(veg_data)

        # --- 3. 本体ページのインデックス項目を作成 ---
        index_item = {
            "id": item_id,
            "type": "vegetable",
            "display_name": display_name,
            "oneliner": oneliner,
            "kana_name": kana_name,
            "search_keys": search_keys
        }
        self._index_items.append(index_item)

        # --- 4. 転送ページのインデックス項目を生成 ---
        for key in search_keys:
            if key != item_id and key not in self._processed_ids:
                redirect_item = {
                    "id": key,
                    "type": "redirect",
                    "redirect_to": item_id
                }
                self._index_items.append(redirect_item)
                self._processed_ids.add(key)
        return

    def get_sorted_index(self) -> List[Dict[str, Any]]:
        """
        蓄積されたインデックス項目をIDでソートして返す。
        """
        if not self._index_items:
            return []

        self._index_items.sort(key=lambda x: x["id"])
        return self._index_items

    def _create_search_keys(self, veg_data: Dict[str, Any]) -> list[str]:
        """
        野菜データから、検索用のキー（漢字、ひらがな、カタカナ）を生成する。
        (内部ヘルパーメソッド)
        """
        keys = set()

        global_info = veg_data.get("global_info", {})
        content_ja = veg_data.get("content", {}).get("ja", {})

        # 1. ID (url)
        url = global_info.get("url")
        if url:
            keys.add(url)

        # 2. 表示名 (display_name) から括弧を除いた部分
        display_name = content_ja.get("display_name", "")
        if "(" in display_name:
            keys.add(display_name.split("(", 1)[0].strip())
        else:
            keys.add(display_name.strip())

        # 3. カタカナ名 (kana_name)
        kana_name = global_info.get("kana_name")
        if kana_name:
            keys.add(kana_name)

        # 4. names.japanese.common から全ての別名を取得
        common_names = global_info.get("names", {}).get("japanese", {}).get("common", [])
        for name in common_names:
            keys.add(name)

        return sorted(list(filter(None, keys)))

def main():
    # ... ファイル読み込みロジック ...
    response_files = list(VEGETABLE_SUMMARY_DIR.glob("*.json"))

    # 1. IndexGeneratorのインスタンスを作成
    index_generator = IndexGenerator()

    for file_path in response_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            veg_data = json.load(f)
            if veg_data:
                # 2. 抽出したデータをジェネレーターに追加
                index_generator.add_vegetable(veg_data)


    # 3. 最終的なインデックスリストを取得
    final_index_list = index_generator.get_sorted_index()
    # 4. _index.json を保存
    with open(INDEX_JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_index_list, f, ensure_ascii=False, indent=2)

    print(f"✅ {len(final_index_list)}件のインデックス項目を {INDEX_JSON_FILE} に保存しました。")

if __name__ == "__main__":
    main()


