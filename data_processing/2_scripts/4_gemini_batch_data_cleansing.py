import config
import json
import os

OUTPUT_DIR = config.RAW_DATA / "species_detail"
ERROR_DIR = config.RAW_DATA / "species_detail_error"


def main():
    files = list(ERROR_DIR.glob("*.json"))
    if not files:
        print("エラーデータがありません。")
        return

    print(f"{len(files)}個のファイルをチェックします...\n")

    num = 0
    for filepath in sorted(files):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                output_path = OUTPUT_DIR / filepath.name
            with open(output_path, "w") as f_out:
                json.dump(data, f_out, ensure_ascii=False, indent=2)
            os.remove(filepath)
            num += 1
        except json.JSONDecodeError as e:
            print(f"{filepath.name}: {e}")
        except Exception as e:
            print(f"ファイルの読み込み中にエラーが発生しました: {e}")

    print(f"{num}個の正常なファイルを移動しました\n")

if __name__ == "__main__":
    main()


