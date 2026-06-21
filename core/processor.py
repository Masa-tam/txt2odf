import re

def process_text(text: str, config: dict) -> str:
    """
    設定に基づいてテキストの空白行を除去・圧縮します。
    """
    proc_config = config.get("processing", {}).get("blank_lines", {})
    mode = proc_config.get("mode", "none")
    
    if mode == "none":
        return text
        
    if mode == "remove_all":
        lines = text.splitlines()
        return "\n".join(line for line in lines if line.strip())
        
    if mode == "compress":
        # 単一の空行は削除(\n)、複数行の空行は1行の空行(\n\n)に圧縮する
        def replacer(m):
            n_count = m.group(0).count('\n')
            return '\n' if n_count == 2 else '\n\n'
        text = re.sub(r'\n([ \t\r\f\v]*\n)+', replacer, text)
        return text
        
    if mode == "dialogue_narrative":
        # 会話文（「」）の前後の単一空行を削除して詰める
        text = re.sub(r'\n[ \t\r\f\v]*\n(?=[ \t]*「)', '\n', text)
        text = re.sub(r'(」[ \t]*)\n[ \t\r\f\v]*\n', r'\1\n', text)
        return text
        
    if mode == "dialogue_narrative_compress":
        # 3行以上の空行は1行(\n\n)に圧縮
        def replacer_multi(m):
            return '\n\n'
        text = re.sub(r'\n([ \t\r\f\v]*\n){2,}', replacer_multi, text)
        # 会話文（「」）の前後の単一空行を削除して詰める
        text = re.sub(r'\n[ \t\r\f\v]*\n(?=[ \t]*「)', '\n', text)
        text = re.sub(r'(」[ \t]*)\n[ \t\r\f\v]*\n', r'\1\n', text)
        return text
        
    if mode == "custom":
        rules = proc_config.get("custom_rules", [])
        for rule in rules:
            pattern = rule.get("pattern")
            replace = rule.get("replace", "")
            if pattern:
                text = re.sub(pattern, replace, text, flags=re.MULTILINE)
        return text
        
    return text
