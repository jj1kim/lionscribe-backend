"""마크다운 → HTML → PDF 변환."""
import markdown as md
from weasyprint import HTML

_CSS = """
@page { size: A4; margin: 2cm; }
body {
    font-family: 'Noto Sans KR', 'Noto Sans', sans-serif;
    line-height: 1.65;
    color: #2C3E50;
    font-size: 11pt;
}
h1 {
    color: #5E35B1;
    border-bottom: 2px solid #5E35B1;
    padding-bottom: 0.3em;
    margin-top: 0.5em;
}
h2 {
    color: #2C3E50;
    margin-top: 1.5em;
    border-left: 4px solid #7E57C2;
    padding-left: 0.5em;
}
h3 { color: #555; margin-top: 1.2em; }
p { margin: 0.6em 0; }
ul, ol { margin: 0.6em 0; padding-left: 1.8em; }
ul ul, ol ol, ul ol, ol ul {
    margin: 0.2em 0;
    padding-left: 1.5em;
}
li { margin: 0.25em 0; }
li > p { margin: 0.2em 0; }
code {
    background: #f3f0fa;
    padding: 0.1em 0.35em;
    border-radius: 3px;
    font-family: 'Courier New', monospace;
    font-size: 0.92em;
}
pre {
    background: #f3f0fa;
    padding: 1em;
    border-radius: 6px;
    overflow-x: auto;
    border-left: 3px solid #7E57C2;
}
pre code { background: transparent; padding: 0; }
blockquote {
    border-left: 4px solid #7E57C2;
    padding: 0.3em 1em;
    color: #555;
    margin: 0.8em 0;
    background: #faf9fd;
}
table { border-collapse: collapse; width: 100%; margin: 1em 0; }
th, td { border: 1px solid #ddd; padding: 0.5em 0.8em; }
th { background: #f3f0fa; color: #5E35B1; }
hr { border: none; border-top: 1px solid #ddd; margin: 1.2em 0; }
a { color: #5E35B1; }
strong { color: #2C3E50; }
"""


def render_markdown_to_pdf(markdown_text: str, title: str = '') -> bytes:
    """마크다운 문자열을 받아 PDF bytes 반환.

    Tab 문자를 4 space로 normalize한 다음 markdown 처리. 중첩 리스트 명확.
    """
    # Tab → 4 spaces (standard markdown 들여쓰기 단위)
    normalized = markdown_text.replace('\t', '    ')

    html_body = md.markdown(
        normalized,
        extensions=['extra', 'fenced_code', 'tables', 'sane_lists', 'nl2br'],
    )
    html_doc = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>{title}</title>
<style>{_CSS}</style></head>
<body>
<h1>{title}</h1>
{html_body}
</body></html>"""
    return HTML(string=html_doc).write_pdf()
