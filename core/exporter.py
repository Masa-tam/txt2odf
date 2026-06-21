import os
import subprocess
from odf.opendocument import OpenDocumentText

def export_document(doc: OpenDocumentText, output_path: str, config: dict):
    """
    ODTドキュメントを保存します。
    PDFの場合はLibreOfficeを呼び出して変換します。
    """
    if output_path.lower().endswith('.pdf'):
        # PDF変換用に一時ODTファイルを作成
        temp_odt = output_path + ".temp.odt"
        doc.save(temp_odt)
        
        try:
            outdir = os.path.dirname(os.path.abspath(output_path))
            print("LibreOfficeを使用してPDFに変換しています...")
            
            # Windows/Linux共通: sofficeコマンドを使用
            subprocess.run(
                ["soffice", "--headless", "--convert-to", "pdf", temp_odt, "--outdir", outdir],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # 出力されたPDFのパスを特定
            generated_pdf = os.path.join(outdir, os.path.basename(temp_odt).replace(".odt", ".pdf"))
            
            if os.path.exists(generated_pdf):
                if os.path.exists(output_path):
                    os.remove(output_path)
                os.rename(generated_pdf, output_path)
            else:
                print("エラー: PDFファイルが生成されませんでした。")
                
        except FileNotFoundError:
            print("エラー: 'soffice' コマンドが見つかりません。LibreOfficeがインストールされ、PATHが通っているか確認してください。")
        except subprocess.CalledProcessError as e:
            print(f"PDF変換プロセスがエラーを返しました: {e.stderr.decode('utf-8', errors='ignore')}")
        except Exception as e:
            print(f"PDF変換中に予期せぬエラーが発生しました: {e}")
        finally:
            if os.path.exists(temp_odt):
                os.remove(temp_odt)
    else:
        # 通常のODT保存
        doc.save(output_path)
