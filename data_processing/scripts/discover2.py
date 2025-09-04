import os
import json
import time
from datetime import datetime, timezone
import config
import data
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold


# 結果を保存するためのベースディレクトリ
INPUT_DIR = config.PROJECT_ROOT / "output" / "raw_data" / "regional_cuisine_data"
OUTPUT_DIR = config.PROJECT_ROOT / "output" / "raw_data" / "cuisine_data"

def setup_api():
    """Gemini APIのセットアップとモデルの取得"""
    genai.configure(api_key=config.API_KEY)
    # 安全性設定を緩和し、より広範な応答を得やすくする
    safety_settings = {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }
    # ★★★ モデル名を、現在利用可能な最新モデルに修正 ★★★
    model = genai.GenerativeModel('gemini-2.5-pro', safety_settings=safety_settings)
    return model

def discover_concepts(model, area_id, n, area_meta, cuisine):
    """指定された地域の料理概念を発見し、ファイルに保存する"""
    id = f'{area_id}_{n:03}'
    specific_area = area_meta["specific_area"]
    consept_name_ja = cuisine["concept_name_ja"]
    consept_name_local = cuisine["concept_name_local"]
    consept_name_en = cuisine["concept_name_en"]
    language = cuisine["local_language"]

    print(f"\n--- {specific_area}の調査を開始 ---")

    # 出力先のディレクトリとファイルパスを決定
    filepath = os.path.join(OUTPUT_DIR, id + ".json")

    if os.path.exists(filepath):
        print(f"-> ファイルが既に存在するため、スキップします: {filepath}")
        return

    # プロンプトをフォーマット
    prompt = config.PROMPT_TEMPLATE.format(
        SPECIFIC_AREA = specific_area,
        CONCEPT_NAME_JA = consept_name_ja,
        CONCEPT_NAME_LOCAL = consept_name_local,
        CONCEPT_NAME_EN = consept_name_en,
        LANGUAGE = language
    )

    try:
        # Gemini APIへリクエスト
        response = model.generate_content(prompt)

        # レスポンスからJSONテキストを慎重に抽出
        json_text = response.text.strip()
        if "```json" in json_text:
            json_text = json_text.split("```json")[1]
        if "```" in json_text:
            json_text = json_text.split("```")[0]
        json_text = json_text.strip()

        # 取得したデータをパース
        data = json.loads(json_text)
        data["generated_at"] = datetime.now(timezone.utc).isoformat() + "Z"
        data["prompt_version"] = "1.0"

        # JSONファイルに美しく整形して保存
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"-> 成功: 調査結果を '{filepath}' に保存しました。")

    except Exception as e:
        print(f"-> エラーが発生しました ({specific_area}): {type(e).__name__} - {e}")
        # 失敗した場合、エラーログを残すことも可能
        pass


def main():
    """
    メインの処理を実行し、定義されたすべての地域の調査を行う
    """
    model = setup_api()
    print("--- 料理の自動発見プロセスを開始します ---")

    for area_info in data.SPECIFIC_AREA:
        area_id = area_info["id"]
        path = INPUT_DIR / f'{area_id}.json'
        with open(path, "r", encoding="utf-8") as f:
            area_all = json.load(f)
            area_meta = area_all["metadata"]
            area_data = area_all["data"]
            if len(area_data) == 0:
                continue
            n = 1
            for cuisine in area_data["culinary_concepts"]:
                discover_concepts(model, area_id, n, area_meta, cuisine)
                n += 1
                time.sleep(5)  # APIへの連続リクエストを避けるための丁寧な待機

    print("\n--- すべての調査が完了しました ---")


if __name__ == "__main__":
    main()
