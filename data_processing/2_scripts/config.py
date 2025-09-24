# scripts/config.py
import os
from pathlib import Path
from dotenv import load_dotenv

# -----------------------------
# パス設定
# -----------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
INPUT_LISTS = DATA_DIR / "1_input_lists"
RAW_RESPONSES = DATA_DIR / "2_raw_responses"
RAW_DATA = DATA_DIR / "3_raw_data"
PROCESSING_DATA = DATA_DIR / "4_processing_data"
APP_DATA = DATA_DIR / "5_app_data"
PROMPTS_DIR = PROJECT_ROOT / "1_prompts"

# -----------------------------
# 環境変数のロードとAPI設定
# -----------------------------
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise ValueError("エラー: .envファイルに GOOGLE_API_KEY を設定してください。")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("エラー: .envファイルに OPENAI_API_KEY を設定してください。")

# -----------------------------
# プロンプトテンプレートの読み込み
# -----------------------------
def load_template() :
    template_path = TEMPLATES_DIR / TEMPLATE_NAME
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()
