import json
import os

import config


JSONL_FILENAME = config.RAW_RESPONSES / "varieties_summary_0.jsonl"
OUTPUT_DIR = config.RAW_DATA / "varieties_summary"
ERROR_DIR = config.RAW_DATA / "varieties_summary_error"


def main():
    """JSONLファイルを個別のJSONファイルに分割"""
    with (open(JSONL_FILENAME, 'r', encoding='utf-8') as f):
        for line_num, line in enumerate(f):
            if line.strip():  # 空行をスキップ
                try:
                    data = json.loads(line)
                    text = data.get("response").get("candidates")[0].get("content").get("parts")[0].get("text").strip().replace("```json", "").replace("```", "").strip()
                    output_data = json.loads(text)

                    # custom_idからファイル名を作成
                    key = data.get('key')
                    filename = key # f"{key}.json"
                    filepath = os.path.join(OUTPUT_DIR, filename)
                    # 個別ファイルに保存
                    with open(filepath, 'w', encoding='utf-8') as out_f:
                        json.dump(output_data, out_f, ensure_ascii=False, indent=2)

                    print(f"作成: {filepath}")
                except json.JSONDecodeError as e:
                    key = data.get('key')
                    filepath = ERROR_DIR / f"{key}.json"
                    with open(filepath, 'w', encoding='utf-8') as out_f:
                        out_f.write(text)
                except Exception as e:
                    print(f"エラーが発生しました:{line_num} {e}")


if __name__ == "__main__":
    main()