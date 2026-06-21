import argparse
import os
import sys
from core.config import load_config
from core.list_parser import parse_list
from core.text_reader import read_text_file
from core.processor import process_text
from core.builder import build_document
from core.exporter import export_document

def main():
    parser = argparse.ArgumentParser(description="Web小説プレーンテキストからODT/PDFへの変換プログラム")
    parser.add_argument("-i", "--Input", required=True, help="入力リストファイル (.txt)")
    parser.add_argument("-f", "--Format", required=True, help="変換フォーマット設定ファイル (.json)")
    parser.add_argument("-o", "--Output", required=True, help="出力ファイルパス (.odt または .pdf)")
    
    args = parser.parse_args()

    print(f"[{args.Input}] を読み込んでいます...")
    
    # 設定の読み込み
    try:
        config = load_config(args.Format)
    except Exception as e:
        print(f"設定ファイルの読み込みに失敗しました: {e}", file=sys.stderr)
        sys.exit(1)
        
    # リストファイルのパース
    try:
        list_items = parse_list(args.Input)
    except Exception as e:
        print(f"リストファイルの読み込みに失敗しました: {e}", file=sys.stderr)
        sys.exit(1)

    # 構造化データの構築
    document_data = []
    base_dir = os.path.dirname(os.path.abspath(args.Input))
    
    for item in list_items:
        if item["type"] in ("h1", "h2", "h3"):
            document_data.append(item)
        elif item["type"] == "file":
            # ファイルパスの解決 (相対パスの場合、リストファイル基準)
            file_path = item["path"]
            if not os.path.isabs(file_path):
                file_path = os.path.join(base_dir, file_path)
            
            try:
                raw_text = read_text_file(file_path)
                processed_text = process_text(raw_text, config)
                document_data.append({
                    "type": "content",
                    "text": processed_text
                })
            except Exception as e:
                print(f"警告: ファイル {file_path} の読み込み・処理に失敗しました: {e}", file=sys.stderr)

    print("ドキュメントを構築しています...")
    # ODTの構築
    odt_doc = build_document(document_data, config)
    
    print(f"[{args.Output}] を出力しています...")
    # 保存とエクスポート
    export_document(odt_doc, args.Output, config)
    print("変換が完了しました。")

if __name__ == "__main__":
    main()
