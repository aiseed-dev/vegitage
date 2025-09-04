import os
import json
import time
from datetime import datetime
import google.generativeai as genai
import config
import data


# 結果を保存するためのベースディレクトリ
OUTPUT_DIR = config.PROJECT_ROOT / "output" / "raw_data" / "regional_cuisine_data"

def setup_api():
    """Gemini APIのセットアップとモデルの取得"""
    genai.configure(api_key=config.API_KEY)
    # 安全性設定を緩和し、より広範な応答を得やすくする
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]
    model = genai.GenerativeModel('gemini-2.5-pro', safety_settings=safety_settings)
    return model

def discover_concepts_for_region(model, region_info):
    """指定された地域の料理概念を発見し、ファイルに保存する"""
    id = region_info["id"]
    region = region_info["region"]
    specific_area = region_info["specific_area"]
    language = region_info["lang_code"]

    print(f"\n--- {specific_area}の調査を開始 ---")

    # 出力先のディレクトリとファイルパスを決定
    filepath = os.path.join(OUTPUT_DIR, id + ".json")

    if os.path.exists(filepath):
        print(f"-> ファイルが既に存在するため、スキップします: {filepath}")
        return

    # プロンプトをフォーマット
    prompt = config.PROMPT_TEMPLATE.format(
        REGION=region,
        SPECIFIC_AREA=specific_area,
        LANGUAGE=language
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

        # メタデータを追加
        final_output = {
            "metadata": {
                "region": region,
                "specific_area": specific_area,
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "prompt_version": "1.0"
            },
            "data": data
        }

        # JSONファイルに美しく整形して保存
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(final_output, f, ensure_ascii=False, indent=2)

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

    for region_info in data.SPECIFIC_AREA:
        discover_concepts_for_region(model, region_info)
        time.sleep(5)  # APIへの連続リクエストを避けるための丁寧な待機

    print("\n--- すべての調査が完了しました ---")


if __name__ == "__main__":
    main()
