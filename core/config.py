import json

def load_config(file_path: str) -> dict:
    """
    JSONフォーマット設定ファイルを読み込みます。
    BOM付きUTF-8に対応します。
    """
    with open(file_path, "r", encoding="utf-8-sig") as f:
        return json.load(f)
