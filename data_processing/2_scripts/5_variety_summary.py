import json
import config

IN_DIR = config.RAW_DATA / "varieties_summary"
IN_DETAIL_DIR = config.RAW_DATA / "varieties_detail"
SPECIES_SUMMARY_DIR = config.PROCESSING_DATA / "species_summary"
OUT_DIR = config.PROCESSING_DATA / "varieties_summary"

def generate_global_info(profile, species_global_info):
    """
    Geminiが生成した詳細データから、ファーストビュー用の global_info を生成する。

    Args:
        profile: Geminiが生成した詳細な分析データ（JSONを辞書に変換したもの）。
        species_global_info: 属する品目の global_info
    Returns:
        計算・抽出された global_info の辞書。
    """
    try:

        url_id = profile.get("url")
        kana_name = profile.get("kana_name")

        # --- scientificName の抽出 ---
        # full_notation があればそれを優先、なければ species_level を使う
        sci_name_data = profile.get("scientific_name", {})
        scientific_name = sci_name_data.get("variety_level") or sci_name_data.get("species_level")
        classification = species_global_info.get("classification", {})
        food_classification = species_global_info.get("foodClassification", {}) or {}

        # --- names の抽出 ---
        names_data = profile.get("names", {})

        # names.japanese.common の生成
        # display_name の括弧を除いた部分と、url(ID)を基本とする
        display_name = profile.get("display_name", "")
        if "(" in display_name:
            jp_common_name = display_name.split("(", 1)[0].strip()
        else:
            jp_common_name = display_name.strip()

        # 重複を避けてリスト化
        jp_common_list = sorted(list(set(filter(None, [jp_common_name, url_id]))))

        # names.international.en の抽出
        en_names_list = names_data.get("international", {}).get("en", [])

        # --- 最終的な global_info 構造の組み立て ---
        global_info = {
            "url": url_id,
            "kana_name": kana_name,
            "scientificName": scientific_name,
            "classification": classification,
            "foodClassification": food_classification,
            "names": {
                "japanese": {
                    "common": jp_common_list
                },
                "international": {
                    "en": en_names_list
                }
            }
        }

        return global_info

    except Exception as e:
        print(f"global_info の生成中にエラーが発生しました: {e}")
        # エラーが発生した場合は、構造が分かるように空のデータを返す
        return {
            "url": "error",
            "kana_name": "エラー",
            "scientificName": "N/A",
            "classification": {},
            "foodClassification": {},
            "names": {}
        }

def main():
    response_files = sorted(IN_DIR.glob("*.json"))
    print(f"{len(response_files)}件の処理を開始します")
    num = 0
    error_count = 0
    for file_path in response_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                gemini_variety_summary = json.load(f)
            with open(IN_DETAIL_DIR / file_path.name, 'r', encoding='utf-8') as f:
                varieties_detail = json.load(f)
                variety_profile = varieties_detail.get("variety_profile", {})
                parent_species_url = variety_profile.get("parent_species_url")
            with open(SPECIES_SUMMARY_DIR / f"{parent_species_url}.json", 'r', encoding='utf-8') as f:
                species_summary = json.load(f)
                species_global_info = species_summary.get("global_info", {})
            global_info = generate_global_info(variety_profile, species_global_info)
            content = gemini_variety_summary.get("content", {})
            relationships = varieties_detail.get("relationships", {})
            ja = content["ja"]
            ja["relationships"] = relationships
            variety_summary = {
                "global_info": global_info,
                "content": content,
            }
            url = global_info.get("url")
            output_path = OUT_DIR / f"{url}.json"
            with open(output_path, "w") as f_out:
                json.dump(variety_summary, f_out, ensure_ascii=False, indent=2)
            num += 1
        except json.JSONDecodeError as e:
            print(f"{file_path.name}: {e}")
            error_count += 1
            continue
    print(f"{num}件の処理が完了")

if __name__ == "__main__":
    main()

