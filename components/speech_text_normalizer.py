from emoji import replace_emoji
from markdown_it import MarkdownIt
from markdown_it.token import Token


class SpeechTextNormalizer:
    """Converts model output into text suitable for speech synthesis."""

    def __init__(self) -> None:
        self._markdown = MarkdownIt("commonmark", {"html": False})

    def normalize(self, text: str) -> str:
        text = replace_emoji(text, replace="")
        blocks = [self._text(token) for token in self._markdown.parse(text)]
        return "\n".join(block for block in blocks if block).strip()

    @staticmethod
    def _text(token: Token) -> str:
        if token.type in {"fence", "code_block"}:
            return token.content.rstrip("\n")
        if token.type != "inline":
            return ""
        parts = []
        for child in token.children or []:
            if child.type in {"text", "code_inline"}:
                parts.append(child.content)
            elif child.type in {"softbreak", "hardbreak"}:
                parts.append("\n")
        return "".join(parts)
