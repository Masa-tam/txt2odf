from odf.opendocument import OpenDocumentText
from odf.style import Style, TextProperties, ParagraphProperties, PageLayout, PageLayoutProperties, MasterPage, RubyProperties
from odf.text import P, H, Span, Ruby, RubyBase, RubyText
from core.markup import parse_paragraph

def build_document(document_data: list, config: dict) -> OpenDocumentText:
    doc = OpenDocumentText()
    
    style_config = config.get("style", {})
    font_family = style_config.get("font_family", "Noto Serif JP")
    font_sizes = style_config.get("font_size", {"body": 10.5, "h1": 16, "h2": 14})
    
    # 行送りの設定 (デフォルト 1.5)
    line_height = style_config.get("line_height", 1.5)
    body_font_size = font_sizes.get("body", 10.5)
    
    if isinstance(line_height, (int, float)):
        # ルビ等で行の幅（高さ）がブレるのを防ぐため、固定値（pt）として計算する
        fixed_line_height = body_font_size * line_height
        line_height_str = f"{fixed_line_height}pt"
    else:
        line_height_str = str(line_height)
    
    writing_mode = style_config.get("writing_mode", "vertical")
    # lr-tb は横書き、tb-rl は縦書き (ODF仕様)
    writing_mode_odf = "tb-rl" if writing_mode == "vertical" else "lr-tb"
    
    def get_text_properties(family: str, size: float, **kwargs) -> TextProperties:
        size_str = f"{size}pt"
        return TextProperties(
            fontfamily=family, fontfamilyasian=family, fontfamilycomplex=family,
            fontsize=size_str, fontsizeasian=size_str, fontsizecomplex=size_str,
            **kwargs
        )
    
    # ページレイアウト (縦書き/横書きの設定)
    page_layout = PageLayout(name="StandardLayout")
    page_layout.addElement(PageLayoutProperties(writingmode=writing_mode_odf))
    doc.automaticstyles.addElement(page_layout)
    
    master_page = MasterPage(name="Standard", pagelayoutname=page_layout)
    doc.masterstyles.addElement(master_page)
    
    # 段落スタイル
    p_style = Style(name="BodyText", family="paragraph")
    # 行の高さを完全固定し、文字を底辺（縦書きの場合は左端）に揃えることで、
    # ルビによる中央揃えのズレと、はみ出しによる欠けを同時に防ぐ
    p_style.addElement(ParagraphProperties(
        writingmode=writing_mode_odf, 
        lineheight=line_height_str,
        verticalalign="bottom",
        margintop="0pt",
        marginbottom="0pt",
        marginleft="0pt",
        marginright="0pt"
    ))
    p_style.addElement(get_text_properties(font_family, font_sizes.get('body', 10.5)))
    doc.styles.addElement(p_style)
    
    # 見出しスタイル
    h1_style = Style(name="Heading1", family="paragraph")
    h1_style.addElement(get_text_properties(font_family, font_sizes.get('h1', 16), fontweight="bold", fontweightasian="bold"))
    doc.styles.addElement(h1_style)
    
    h2_style = Style(name="Heading2", family="paragraph")
    h2_style.addElement(get_text_properties(font_family, font_sizes.get('h2', 14), fontweight="bold", fontweightasian="bold"))
    doc.styles.addElement(h2_style)
    
    h3_style = Style(name="Heading3", family="paragraph")
    h3_style.addElement(get_text_properties(font_family, font_sizes.get('h3', 12), fontweight="bold", fontweightasian="bold"))
    doc.styles.addElement(h3_style)
    
    # 傍点スタイル設定
    emphasis_marks = style_config.get("emphasis", ["text-emphasize"])
    if "ruby" in emphasis_marks and "text-emphasize" in emphasis_marks:
        raise ValueError("Cannot specify both 'ruby' and 'text-emphasize' for emphasis styles.")
        
    use_ruby_emphasis = "ruby" in emphasis_marks
    if not use_ruby_emphasis:
        emp_style = Style(name="Emphasis", family="text")
        emp_text_props = {}
        if "bold" in emphasis_marks:
            emp_text_props["fontweight"] = "bold"
            emp_text_props["fontweightasian"] = "bold"
        if "italic" in emphasis_marks:
            emp_text_props["fontstyle"] = "italic"
            emp_text_props["fontstyleasian"] = "italic"
        if "text-emphasize" in emphasis_marks:
            emp_text_props["textemphasize"] = "dot above"
        
        if emp_text_props:
            emp_style.addElement(TextProperties(**emp_text_props))
        doc.automaticstyles.addElement(emp_style)
    
    # ルビのスタイル（センタリング配置指定）
    ruby_style = Style(name="RubyStyle", family="ruby")
    ruby_style.addElement(RubyProperties(rubyalign="center"))
    doc.automaticstyles.addElement(ruby_style)

    # ルビ文字（ふりがな）のスタイル
    # ルビがはみ出して欠けるのを防ぐため、textpositionで少し本文側に寄せる（下付き/左寄せ）
    rt_style = Style(name="RubyText", family="text")
    rt_style.addElement(TextProperties(fontsize="45%", fontsizeasian="45%"))
    doc.automaticstyles.addElement(rt_style)

    # ドキュメント要素の構築
    for item in document_data:
        if item["type"] == "h1":
            doc.text.addElement(H(outlinelevel=1, stylename=h1_style, text=item["text"]))
        elif item["type"] == "h2":
            doc.text.addElement(H(outlinelevel=2, stylename=h2_style, text=item["text"]))
        elif item["type"] == "h3":
            doc.text.addElement(H(outlinelevel=3, stylename=h3_style, text=item["text"]))
        elif item["type"] == "content":
            text_blocks = item["text"].split("\n")
            for block in text_blocks:
                p = P(stylename=p_style)
                if block == "":
                    # 空行の場合はそのまま空の段落を追加
                    doc.text.addElement(p)
                    continue
                
                chunks = parse_paragraph(block)
                for chunk in chunks:
                    if chunk["type"] == "text":
                        p.addElement(Span(text=chunk["content"]))
                    elif chunk["type"] == "emphasis":
                        if use_ruby_emphasis:
                            for char in chunk["content"]:
                                ruby_node = Ruby(stylename=ruby_style)
                                ruby_node.addElement(RubyBase(text=char))
                                ruby_node.addElement(RubyText(stylename=rt_style, text="・"))
                                p.addElement(ruby_node)
                        else:
                            p.addElement(Span(stylename=emp_style, text=chunk["content"]))
                    elif chunk["type"] == "ruby":
                        ruby_node = Ruby(stylename=ruby_style)
                        ruby_node.addElement(RubyBase(text=chunk["rb"]))
                        ruby_node.addElement(RubyText(stylename=rt_style, text=chunk["rt"]))
                        p.addElement(ruby_node)
                        
                doc.text.addElement(p)
                
    return doc
