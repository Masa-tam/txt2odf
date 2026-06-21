import re

def parse_paragraph(text: str) -> list:
    """
    1段落の文字列をカクヨム記法として解析し、テキストチャンクのリストを返します。
    """
    chunks = []
    
    # 1. 傍点: 《《...》》
    # 2. ルビ (|あり): |親文字《ルビ》
    # 3. ルビ (|なし): 漢字《ルビ》
    pattern = re.compile(
        r'(?P<emphasis>《《(?P<emp_text>[^》]+)》》)'
        r'|(?P<ruby_bar>\|(?P<rb_bar>[^《]+)《(?P<rt_bar>[^》]+)》)'
        r'|(?P<ruby_kanji>(?P<rb_kanji>[一-龠々]+)《(?P<rt_kanji>[^》]+)》)'
    )
    
    last_end = 0
    for match in pattern.finditer(text):
        start, end = match.span()
        
        if start > last_end:
            chunks.append({"type": "text", "content": text[last_end:start]})
            
        if match.group("emphasis"):
            chunks.append({"type": "emphasis", "content": match.group("emp_text")})
        elif match.group("ruby_bar"):
            chunks.append({
                "type": "ruby", 
                "rb": match.group("rb_bar"), 
                "rt": match.group("rt_bar")
            })
        elif match.group("ruby_kanji"):
            chunks.append({
                "type": "ruby", 
                "rb": match.group("rb_kanji"), 
                "rt": match.group("rt_kanji")
            })
            
        last_end = end
        
    if last_end < len(text):
        chunks.append({"type": "text", "content": text[last_end:]})
        
    return chunks
