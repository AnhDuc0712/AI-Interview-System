import re


class TextNormalizationService:
    def normalize(self, raw_text: str) -> str:
        text = raw_text.replace('\r\n', '\n').replace('\r', '\n')
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()
