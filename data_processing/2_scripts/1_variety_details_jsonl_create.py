import json

import config

# ディレクトリ
IN_JSON = config.INPUT_LISTS / "varieties_list_ja_0.json"
IN_WITH_REC_JSON = config.INPUT_LISTS / "varieties_list_ja_with_rec_0.json"
PROMPT_DIR = config.PROMPTS_DIR / "2_varieties_details"
OUTPUT_FILE = config.INPUT_LISTS / "varieties_detail_ja_0.jsonl"

START_NUM = 1

PROMPT_SYSTEM_FILE = PROMPT_DIR / "1_system.txt"
PROMPT_SYSTEM = PROMPT_SYSTEM_FILE.read_text(encoding="utf-8")
PROMPT_SCHEME_FILE = PROMPT_DIR / "2_schema.json"
PROMPT_SCHEME = PROMPT_SCHEME_FILE.read_text(encoding="utf-8")
PROMPT_SPECIAL_FILE = PROMPT_DIR / "3_special.md"
PROMPT_SPECIAL = PROMPT_SPECIAL_FILE.read_text(encoding="utf-8")


def main():
    rec_num = START_NUM
    with open(IN_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # 各項目にIDを追加
    data_with_rec = []
    for item in data:
        new_item = {"rec": f"rec_{rec_num}"}
        rec_num += 1
        new_item.update(item)
        data_with_rec.append(new_item)
    with open(IN_WITH_REC_JSON, 'w', encoding='utf-8') as f:
        json.dump(data_with_rec, f, ensure_ascii=False, indent=2)


    request_list = []
    for item in data_with_rec:
        prompt = PROMPT_SYSTEM.format(
            VARIETY_NAME=item.get("variety_name"),
            COUNTRY_REGION=item.get("country_region"),
            PRIMARY_RESEARCH_AREA=item.get("primary_research_area"),
            PARENT_SPECIES_NAME=item.get("parent_species_name"),
            SCIENTIFIC_NAME="-",
        )
        prompt += f"'''\n{PROMPT_SCHEME}\n'''\n\n{PROMPT_SPECIAL}"
        request_list.append({
            "key": item.get("rec"),
            "request": {
                'contents': [{'parts': [{'text': prompt}]}]
            },
        })

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for request in request_list:
            f.write(json.dumps(request, ensure_ascii=False) + "\n")

    print("--------------------------------------")
    print(f"{len(request_list)}件処理しました")
    print("\n--- 処理終了 ---")

if __name__ == "__main__":
    main()