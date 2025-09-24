import json

import config

RAW_SPECIES_SUMMARY_DIR = config.RAW_DATA / "species_summary"
RAW_SPECIES_DETAIL_DIR = config.RAW_DATA / "species_detail"
PROCESSING_SPECIES_SUMMARY_DIR = config.PROCESSING_DATA / "species_summary"
PROCESSING_SPECIES_DETAIL_DIR = config.PROCESSING_DATA / "species_detail"

def main():
    # ... あなたのファイル読み込みロジック ...
    response_files = list(RAW_SPECIES_SUMMARY_DIR.glob("*.json"))
    total_count = len(response_files)
    print(f"{total_count}件の処理を開始します")
    num = 0
    error_count = 0
    for file_path in response_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                veg_summary = json.load(f)
                if veg_summary:
                    global_info = veg_summary.get("global_info", {})
                    url = global_info.get("url")

                    proc_summary_path = PROCESSING_SPECIES_SUMMARY_DIR / f"{url}.json"
                    with open(proc_summary_path, 'w', encoding='utf-8') as f:
                        json.dump(veg_summary, f, ensure_ascii=False, indent=2)

                    raw_detail_path = RAW_SPECIES_DETAIL_DIR / file_path.name
                    with open(raw_detail_path, 'r', encoding='utf-8') as f:
                        veg_detail = json.load(f)
                    proc_detail_path = PROCESSING_SPECIES_DETAIL_DIR /  f"{url}.json"
                    with open(proc_detail_path, 'w', encoding='utf-8') as f:
                        json.dump(veg_detail, f, ensure_ascii=False, indent=2)
                    num += 1
                else:
                    print(f"{file_path.name}: データが空")
                    error_count += 1

        except Exception as e:
            print(f"{file_path.name}: {e}")
            error_count += 1

    print(f" {num}件の処理が成功、 {error_count}件の失敗")

if __name__ == "__main__":
    main()


