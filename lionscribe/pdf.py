"""마크다운 → HTML → PDF 변환."""
import markdown as md
from weasyprint import HTML

_CSS = """
@page { size: A4; margin: 2cm; }
body { font-family: 'Noto Sans KR', sans-serif; line-height: 1.6; color: #2C3E50; }
h1 { color: #F5A623; border-bottom: 2px solid #F5A623; padding-bottom: 0.3em; }
h2 { color: #2C3E50; margin-top: 1.5em; }
h3 { color: #555; }
code { background: #f5f5f5; padding: 0.1em 0.3em; border-radius: 3px; }
pre { background: #f5f5f5; padding: 1em; border-radius: 4px; overflow-x: auto; }
blockquote { border-left: 4px solid #F5A623; padding-left: 1em; color: #666; }
table { border-collapse: collapse; width: 100%; }
th, td { border: 1px solid #ddd; padding: 0.5em; }
th { background: #f9f9f9; }
"""


def render_markdown_to_pdf(markdown_text: str, title: str = '') -> bytes:
    """마크다운 문자열을 받아 PDF bytes 반환."""
    html_body = md.markdown(
        markdown_text,
        extensions=['extra', 'fenced_code', 'tables', 'codehilite'],
    )
    html_doc = f"""
    <html><head><meta charset="utf-8"><title>{title}</title>
    <style>{_CSS}</style></head>
    <body>{html_body}</body></html>
    """
    return HTML(string=html_doc).write_pdf()
