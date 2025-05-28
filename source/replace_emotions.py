import re


EMOTICONS = {
    ":)": "☺",
    ":(": "☹",
    ";)": "😉",
    ":D": "😃",
    ":P": "😛",
    ":'(": "😢",
    ":o": "😮",
    ":-)": "🙂",
    ":-(": "🙁"
}

EMOTICON_PATTERN = re.compile(
    r'(^|\s)(' + '|'.join(map(re.escape, EMOTICONS.keys())) + r')(?=\s|$)'
)


def replace_emotions(text):
    """
    Заменяет смайлики на юникод-смайлы в тексте.
    Заменяет только разделенные пробелами символы.
    """
    def replacer(match):
        prefix = match.group(1)
        emoticon = match.group(2)
        return prefix + EMOTICONS[emoticon]
    return EMOTICON_PATTERN.sub(replacer, text)
