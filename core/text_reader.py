def read_text_file(file_path: str) -> str:
    """
    プレーンテキストファイルを読み込みます。
    BOM付きUTF-8に対応し、改行コードの違いを吸収します。
    """
    with open(file_path, "r", encoding="utf-8-sig") as f:
        return f.read()
