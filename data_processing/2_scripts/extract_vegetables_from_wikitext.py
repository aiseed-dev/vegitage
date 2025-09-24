import re
import json
from typing import List, Dict, Optional
import config

WIKITEXT_DIR = config.INPUT_DIR / "wikitext"
VEGETABLES_JSON_DIR = config.RAW_DATA_DIR / "wikipedia_vegetables"
WIKITEXT_FILE_NAME = "root_vegetables"

def extract_vegetables_from_wikitext(wikitext: str) -> List[Dict]:
    """
    Wikipedia野菜一覧のWikitextを解析してJSON形式に変換
    希少野菜を優先度高で設定
    """
    vegetables = []

    # テーブル行を分割（|-で始まる行区切り）
    rows = wikitext.split('|-')[1:]  # 最初の要素はヘッダーなので除外

    for row in rows:
        if not row.strip() in row:
            continue

        # 各列を抽出（||で区切り）
        columns = split_excluding_templates(row)

        if len(columns) < 4:  # 画像、名称、分類群、食用部位の最低4列必要
            print(columns)
            continue

        try:
            # 画像列（スキップ）
            image_col = columns[0] if columns[0].startswith('[') else None

            # 名称列（2列目）の解析
            name_col = columns[1]
            names_info = parse_name_column(name_col)

            # 分類群列（3列目）の解析
            classification_col = columns[2]
            classification_info = parse_classification_column(classification_col)

            # 食用部位列（4列目）の解析
            edible_parts_col = columns[3]
            edible_parts = parse_edible_parts(edible_parts_col)

            # 優先度の決定（希少野菜を高優先度に）
            priority = determine_priority(names_info.get('popularity_markers', []))

            vegetable_entry = {
                "names": names_info,
                "classification": classification_info,
                "edible_parts": edible_parts,
            }

            vegetables.append(vegetable_entry)

        except Exception as e:
            print(f"Error parsing row: {e}")
            continue

    return vegetables


def split_excluding_templates(row):
    """{{...}}内の||を除外して分割"""

    # 一時的な置換文字
    temp_marker = "__TEMP_PIPE__"

    # {{...}}内の||を一時的に置換
    def replace_pipes_in_templates(match):
        return match.group(0).replace('||', temp_marker)

    # {{...}}パターンにマッチする部分の||を置換
    temp_row = re.sub(r'\{\{[^}]*\}\}', replace_pipes_in_templates, row)

    # ||で分割
    columns = [col.strip() for col in temp_row.split('||') if col.strip()]

    # 各列で一時置換文字を||に戻す
    return [col.replace(temp_marker, '||') for col in columns]


def parse_name_column(name_col: str) -> Dict:
    """名称列を解析して日本語名、英語名、マーカーを抽出"""

    # 指定野菜等のマーカーを検出
    popularity_markers = []
    if '***' in name_col:
        popularity_markers.append('***')
    elif '**' in name_col:
        popularity_markers.append('**')
    elif '*' in name_col:
        popularity_markers.append('*')
    if '★' in name_col:
        popularity_markers.append('★')

    # 日本語名の抽出（[[リンク]]形式）
    japanese_names = re.findall(r'\[\[([^\]]+?)\]\]', name_col)
    main_japanese_name = japanese_names[0] if japanese_names else None

    # 英語名の抽出（[[:en:English|english]]形式）
    english_pattern = r'\[\[:en:[^\]]*?\|([^\]]+)\]\]'
    english_names = re.findall(english_pattern, name_col)
    main_english_name = english_names[0] if english_names else None

    # 別名・サブタイプの抽出
    # {{Fontsize|small|（別名）}}形式
    alt_names_pattern = r'\{\{Fontsize\|small\|\（([^）]+)\）\}\}'
    alt_names = re.findall(alt_names_pattern, name_col)

    return {
        "japanese_primary": main_japanese_name,
        "japanese_alternatives": alt_names,
        "english_primary": main_english_name,
        "popularity": determine_priority(popularity_markers)
    }


def parse_classification_column(classification_col: str) -> Dict:
    """分類群列を解析して科、属、学名を抽出"""

    # HTMLタグとリンクを除去してクリーンなテキストにする
    clean_text = re.sub(r'<[^>]+>', '', classification_col)  # HTMLタグ除去
    clean_text = re.sub(r'\[\[([^\]]+)\]\]', r'\1', clean_text)  # [[リンク]]を中身だけに

    # 科名の抽出
    family = None
    family_match = re.search(r'([^。、\s]*科)', clean_text)
    if family_match:
        family = family_match.group(1)

    # 属名の抽出（科名を除去した残りの部分から）
    genus = None
    if family:
        # 科名部分を除去
        remaining_text = clean_text.replace(family, '', 1)
        genus_match = re.search(r'([^。、\s]*属)', remaining_text)
        if genus_match:
            genus = genus_match.group(1)
    else:
        # 科名がない場合は全体から属名を抽出
        genus_match = re.search(r'([^。、\s]*属)', clean_text)
        if genus_match:
            genus = genus_match.group(1)

    # 学名の抽出（{{Snamei||学名}}形式）
    scientific_name_pattern = r'\{\{Snamei\|\|([^}]+)\}\}'
    scientific_name_match = re.search(scientific_name_pattern, classification_col)
    scientific_name = scientific_name_match.group(1).strip() if scientific_name_match else None

    return {
        "family": family,
        "genus": genus,
        "scientific_name": scientific_name
    }

def parse_edible_parts(edible_parts_col: str) -> List[str]:
    """食用部位を解析"""
    # 基本的な食用部位
    parts = []

    # リンク形式の部位を抽出
    linked_parts = re.findall(r'\[\[([^\]]+)\]\]', edible_parts_col)
    parts.extend(linked_parts)

    # 通常テキストの部位（、で区切られている）
    clean_text = re.sub(r'\[\[([^\]]+)\]\]', '', edible_parts_col)
    clean_text = re.sub(r'<[^>]+>', '', clean_text)  # HTMLタグ除去
    clean_text = re.sub(r'\{\{[^}]+\}\}', '', clean_text)  # テンプレート除去

    if clean_text.strip():
        additional_parts = [part.strip() for part in clean_text.split('、') if part.strip()]
        parts.extend(additional_parts)

    return list(set(parts))  # 重複除去


def determine_priority(popularity_markers: List[str]) -> int:
    """
    0: その他
    1: 地域特産野菜生産状況調査の対象種（*）
    2: 特定野菜（**）
    3: 指定野菜（***）
    """
    if not popularity_markers:
        return 0  # マークなし

    if '***' in popularity_markers:
        return 3  # 超メジャー野菜
    elif '**' in popularity_markers:
        return 2  # 一般的野菜
    elif '*' in popularity_markers:
        return 1  # やや知られている野菜

    return 0

def save_vegetables_json(vegetables: List[Dict], filename: str = "vegetables_database.json"):
    """JSONファイルとして保存"""

    output_data = {
        "metadata": {
            "total_vegetables": len(vegetables),
            "processing_strategy": "野菜リスト作成",
            "generated_at": "2025-01-01T00:00:00Z"
        },
        "vegetables": vegetables
    }

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"野菜データベース保存完了: {filename}")
    print(f"総数: {len(vegetables)}")

# メイン実行部分
if __name__ == "__main__":
    try:
        # Wikitextファイルを読み込み
        wikitext_filepath = WIKITEXT_DIR / f"{WIKITEXT_FILE_NAME}.txt"
        wikitext_sample = wikitext_filepath.read_text(encoding="utf-8")


        # Wikitextを解析
        vegetables = extract_vegetables_from_wikitext(wikitext_sample)

        # JSONファイルとして保存
        save_vegetables_json(vegetables, VEGETABLES_JSON_DIR / f"{WIKITEXT_FILE_NAME}.json")


    except Exception as e:
        print(f"処理エラー: {e}")