import sys

def parse_list(file_path: str) -> list:
    """
    リストファイルを読み込み、構造化された要素のリストを返します。
    # は大見出し
    ## は小見出し
    @ファイルパス はテキストファイル
    それ以外の行は構文エラーとして警告を出力し、無視します。
    """
    items = []
    with open(file_path, "r", encoding="utf-8-sig") as f:
        for line_num, line in enumerate(f, 1):
            line_str = line.strip()
            if not line_str:
                continue
            
            if line_str.startswith("### "):
                items.append({"type": "h3", "text": line_str[4:].strip()})
            elif line_str.startswith("###"):
                items.append({"type": "h3", "text": line_str[3:].strip()})
            elif line_str.startswith("## "):
                items.append({"type": "h2", "text": line_str[3:].strip()})
            elif line_str.startswith("##"):
                items.append({"type": "h2", "text": line_str[2:].strip()})
            elif line_str.startswith("# "):
                items.append({"type": "h1", "text": line_str[2:].strip()})
            elif line_str.startswith("#"):
                items.append({"type": "h1", "text": line_str[1:].strip()})
            elif line_str.startswith("@"):
                items.append({"type": "file", "path": line_str[1:].strip()})
            else:
                print(f"警告: リストファイル({file_path} の {line_num}行目)で構文エラーを検出しました。「# 見出し」や「@ファイルパス」の形式になっていません。無視されます: {line_str}", file=sys.stderr)
                
    return items
