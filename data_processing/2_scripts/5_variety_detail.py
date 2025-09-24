import json
import config

INL_DIR = config.RAW_DATA / "varieties_detail"
OUT_DIR = config.PROCESSING_DATA / "varieties_detail"

def main():
    response_files = sorted(INL_DIR.glob("*.json"))
    print(f"{len(response_files)}件の処理を開始します")
    num = 0
    error_count = 0
    for file_path in response_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                variety_detail = json.load(f)
                variety_profile = variety_detail.get("variety_profile", {})
                url = variety_profile.get("url")
                output_path = OUT_DIR / f"{url}.json"
                with open(output_path, "w") as f_out:
                    json.dump(variety_detail, f_out, ensure_ascii=False, indent=2)
                num += 1
        except Exception as e:
            print(f"{file_path.name}: {e}")
            error_count += 1

    print(f"{num}件の処理が完了")

if __name__ == "__main__":
    main()

