import json

import config

# ディレクトリ
IN_DIR = config.RAW_DATA / "varieties_detail"
PROMPT_DIR = config.PROMPTS_DIR / "5_varieties_summary"
SPECIES_DIR = config.PROCESSING_DATA / "species_detail"
OUTPUT_FILE = config.INPUT_LISTS / "varieties_summary_0.jsonl"

PROMPT_SYSTEM_FILE = PROMPT_DIR / "1_system.txt"
PROMPT_SYSTEM = PROMPT_SYSTEM_FILE.read_text(encoding="utf-8")
PROMPT_SCHEME_FILE = PROMPT_DIR / "2_schema.json"
PROMPT_SCHEME = PROMPT_SCHEME_FILE.read_text(encoding="utf-8")


def main():
    response_files = list(IN_DIR.glob("*.json"))
    print(f'{len(response_files)}件の処理を開始')
    request_list = []
    for file_path in response_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                variety_detail_data = f.read()
                data = json.loads(variety_detail_data)
                variety_profile = data.get("variety_profile", {})
                parent_species_url = variety_profile.get("parent_species_url")
            with open(SPECIES_DIR / f"{parent_species_url}.json", 'r', encoding='utf-8') as f:
                species_detail_data = f.read()

            prompt = PROMPT_SYSTEM.format(
                VARIETY_DETAIL_DATA=variety_detail_data,
                SPECIES_DETAIL_DATA=species_detail_data,
            )
            prompt += f"\n'''\n{PROMPT_SCHEME}\n'''\n"
            request_list.append({
                "key": file_path.name,
                "request": {
                    'contents': [{'parts': [{'text': prompt}]}]
                },
            })
        except Exception as e:
            print(f"{file_path.name}: {e}")
            continue

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for request in request_list:
            f.write(json.dumps(request, ensure_ascii=False) + "\n")

    print("--------------------------------------")
    print(f"{len(request_list)}件処理しました")
    print("\n--- 処理終了 ---")

if __name__ == "__main__":
    main()