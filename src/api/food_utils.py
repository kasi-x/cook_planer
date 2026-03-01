"""食品名マッチングユーティリティ

substring matching による誤検出（「乳」→「乳化剤」、「米」→「米ぬか」等）を
防ぐための共通マッチング関数。
"""

# 短いキーワード（1-2文字）で誤検出しやすいもの
_SHORT_KEYWORD_DELIMITERS = ("\u3000", "（", "）", "　", " ", "、")


def match_food_keyword(food_name: str, keyword: str) -> bool:
    """食品名がキーワードにマッチするか判定する。

    - 完全一致を最優先
    - 短いキーワード（1-2文字）は厳密マッチのみ（完全一致 or 区切り文字で囲まれている）
    - 3文字以上は部分一致を許容
    """
    if not food_name or not keyword:
        return False

    # 完全一致
    if food_name == keyword:
        return True

    if len(keyword) <= 2:
        # 短いキーワードは厳密にマッチ
        # キーワードが先頭にあり、直後が区切り文字
        if food_name.startswith(keyword):
            if len(food_name) == len(keyword):
                return True
            if food_name[len(keyword)] in _SHORT_KEYWORD_DELIMITERS:
                return True
        # キーワードが末尾にあり、直前が区切り文字
        if food_name.endswith(keyword):
            pos = len(food_name) - len(keyword)
            if pos > 0 and food_name[pos - 1] in _SHORT_KEYWORD_DELIMITERS:
                return True
        # キーワードが中間にあり、前後が区切り文字
        idx = food_name.find(keyword)
        while idx > 0:
            before_ok = food_name[idx - 1] in _SHORT_KEYWORD_DELIMITERS
            after_pos = idx + len(keyword)
            after_ok = after_pos >= len(food_name) or food_name[after_pos] in _SHORT_KEYWORD_DELIMITERS
            if before_ok and after_ok:
                return True
            idx = food_name.find(keyword, idx + 1)
        return False

    # 3文字以上は部分一致でOK
    return keyword in food_name
