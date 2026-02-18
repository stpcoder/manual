#!/usr/bin/env python3
"""
고문서 손상 영역 인식 시스템 -- Markdown to PDF 변환 스크립트

본 스크립트는 docs/manual/ 디렉토리 내의 모든 챕터 Markdown 파일을
단일 PDF 문서로 병합하여 출력한다.

의존성:
    pip install markdown weasyprint

사용법:
    python build_pdf.py
    python build_pdf.py --output custom_name.pdf
"""

import argparse
import os
import sys
from pathlib import Path


# 챕터 파일 순서 정의
CHAPTERS = [
    "01-개요.md",
    "02-시스템-구조.md",
    "03-설치-및-실행.md",
    "04-핵심-알고리즘.md",
    "05-GUI-사용법.md",
    "06-CLI-사용법.md",
    "07-레이아웃-엔진.md",
    "08-출력-형식.md",
    "09-API-레퍼런스.md",
    "10-데이터-구조.md",
]

# PDF 스타일시트
CSS_STYLE = """
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&family=Noto+Sans+Mono&display=swap');

@page {
    size: A4;
    margin: 25mm 20mm 25mm 20mm;

    @top-center {
        content: "고문서 손상 영역 인식 시스템 기술 문서";
        font-family: 'Noto Sans KR', sans-serif;
        font-size: 8pt;
        color: #888888;
    }

    @bottom-center {
        content: counter(page);
        font-family: 'Noto Sans KR', sans-serif;
        font-size: 9pt;
        color: #333333;
    }
}

@page :first {
    @top-center { content: none; }
    @bottom-center { content: none; }
}

body {
    font-family: 'Noto Sans KR', 'Malgun Gothic', sans-serif;
    font-size: 10.5pt;
    line-height: 1.8;
    color: #1a1a1a;
    text-align: justify;
}

h1 {
    font-size: 20pt;
    font-weight: 700;
    margin-top: 40pt;
    margin-bottom: 16pt;
    padding-bottom: 8pt;
    border-bottom: 2px solid #333333;
    page-break-before: always;
    color: #000000;
}

h1:first-of-type {
    page-break-before: avoid;
}

h2 {
    font-size: 14pt;
    font-weight: 700;
    margin-top: 28pt;
    margin-bottom: 12pt;
    color: #1a1a1a;
}

h3 {
    font-size: 12pt;
    font-weight: 700;
    margin-top: 20pt;
    margin-bottom: 8pt;
    color: #333333;
}

h4 {
    font-size: 11pt;
    font-weight: 700;
    margin-top: 16pt;
    margin-bottom: 6pt;
    color: #333333;
}

p {
    margin-bottom: 8pt;
    orphans: 3;
    widows: 3;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 12pt 0;
    font-size: 9.5pt;
    page-break-inside: avoid;
}

th {
    background-color: #f0f0f0;
    border: 1px solid #cccccc;
    padding: 6pt 8pt;
    text-align: left;
    font-weight: 700;
}

td {
    border: 1px solid #cccccc;
    padding: 5pt 8pt;
    vertical-align: top;
}

tr:nth-child(even) {
    background-color: #fafafa;
}

code {
    font-family: 'Noto Sans Mono', 'Consolas', monospace;
    font-size: 9pt;
    background-color: #f5f5f5;
    padding: 1pt 4pt;
    border-radius: 2pt;
    color: #c7254e;
}

pre {
    font-family: 'Noto Sans Mono', 'Consolas', monospace;
    font-size: 8.5pt;
    line-height: 1.5;
    background-color: #f8f8f8;
    border: 1px solid #e0e0e0;
    border-radius: 3pt;
    padding: 10pt 12pt;
    margin: 10pt 0;
    overflow-x: auto;
    page-break-inside: avoid;
    white-space: pre-wrap;
    word-wrap: break-word;
}

pre code {
    background-color: transparent;
    padding: 0;
    color: #333333;
    font-size: inherit;
}

ul, ol {
    margin-bottom: 8pt;
    padding-left: 24pt;
}

li {
    margin-bottom: 4pt;
}

hr {
    border: none;
    border-top: 1px solid #dddddd;
    margin: 20pt 0;
}

strong {
    font-weight: 700;
}

blockquote {
    border-left: 3px solid #cccccc;
    padding-left: 12pt;
    margin: 10pt 0;
    color: #555555;
}

/* 표지 페이지 */
.cover-page {
    text-align: center;
    padding-top: 200pt;
    page-break-after: always;
}

.cover-title {
    font-size: 28pt;
    font-weight: 700;
    margin-bottom: 20pt;
    color: #000000;
}

.cover-subtitle {
    font-size: 14pt;
    color: #555555;
    margin-bottom: 40pt;
}

.cover-info {
    font-size: 11pt;
    color: #666666;
    margin-top: 80pt;
    line-height: 2.0;
}

/* 목차 페이지 */
.toc-page {
    page-break-after: always;
}

.toc-page h1 {
    page-break-before: avoid;
    border-bottom: 2px solid #333333;
}

.toc-page ul {
    list-style: none;
    padding-left: 0;
}

.toc-page li {
    font-size: 11pt;
    margin-bottom: 8pt;
    padding: 4pt 0;
    border-bottom: 1px dotted #cccccc;
}
"""


def build_cover_page():
    """표지 페이지 HTML을 생성한다."""
    from datetime import date
    today = date.today().strftime("%Y년 %m월")

    return f"""
<div class="cover-page">
    <div class="cover-title">고문서 손상 영역 인식 시스템</div>
    <div class="cover-subtitle">Ancient Document Damage Detection System</div>
    <div class="cover-subtitle">기술 문서</div>
    <div class="cover-info">
        버전 1.0<br>
        {today}<br>
    </div>
</div>
"""


def build_toc_page():
    """목차 페이지 HTML을 생성한다."""
    toc_items = [
        ("제1장", "프로젝트 개요"),
        ("제2장", "시스템 구조"),
        ("제3장", "설치 및 실행"),
        ("제4장", "핵심 알고리즘"),
        ("제5장", "GUI 사용법"),
        ("제6장", "CLI 사용법"),
        ("제7장", "레이아웃 엔진"),
        ("제8장", "출력 형식"),
        ("제9장", "API 레퍼런스"),
        ("제10장", "데이터 구조"),
    ]

    items_html = "\n".join(
        f"        <li>{num} &mdash; {title}</li>"
        for num, title in toc_items
    )

    return f"""
<div class="toc-page">
    <h1>목차</h1>
    <ul>
{items_html}
    </ul>
</div>
"""


def merge_markdown_files(manual_dir):
    """모든 챕터 파일을 하나의 Markdown 문자열로 병합한다."""
    merged = []
    for chapter_file in CHAPTERS:
        filepath = manual_dir / chapter_file
        if not filepath.exists():
            print(f"경고: {chapter_file} 파일이 존재하지 않습니다. 건너뜁니다.")
            continue
        content = filepath.read_text(encoding="utf-8")
        merged.append(content)
    return "\n\n---\n\n".join(merged)


def markdown_to_html(md_text):
    """Markdown 텍스트를 HTML로 변환한다."""
    try:
        import markdown
    except ImportError:
        print("오류: markdown 패키지가 설치되지 않았습니다.")
        print("설치 명령: pip install markdown")
        sys.exit(1)

    extensions = [
        "markdown.extensions.tables",
        "markdown.extensions.fenced_code",
        "markdown.extensions.codehilite",
        "markdown.extensions.toc",
        "markdown.extensions.nl2br",
    ]
    extension_configs = {
        "markdown.extensions.codehilite": {
            "css_class": "highlight",
            "guess_lang": False,
        },
        "markdown.extensions.toc": {
            "permalink": False,
        },
    }
    html = markdown.markdown(
        md_text,
        extensions=extensions,
        extension_configs=extension_configs,
    )
    return html


def build_full_html(body_html):
    """완전한 HTML 문서를 구성한다."""
    cover = build_cover_page()
    toc = build_toc_page()

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>고문서 손상 영역 인식 시스템 기술 문서</title>
    <style>
{CSS_STYLE}
    </style>
</head>
<body>
{cover}
{toc}
{body_html}
</body>
</html>"""


def html_to_pdf(html_content, output_path):
    """HTML을 PDF로 변환한다."""
    try:
        from weasyprint import HTML
    except ImportError:
        print("오류: weasyprint 패키지가 설치되지 않았습니다.")
        print("설치 명령: pip install weasyprint")
        print("")
        print("macOS의 경우 추가로 다음 설치가 필요합니다:")
        print("  brew install pango")
        print("")
        print("대안으로 pandoc을 사용할 수 있습니다:")
        print("  pandoc -o output.pdf --pdf-engine=xelatex \\")
        print("    -V mainfont='Noto Sans KR' \\")
        print("    -V geometry:margin=25mm \\")
        print("    01-개요.md 02-시스템-구조.md ... 10-데이터-구조.md")
        sys.exit(1)

    html_obj = HTML(string=html_content)
    html_obj.write_pdf(output_path)


def main():
    parser = argparse.ArgumentParser(
        description="고문서 손상 영역 인식 시스템 기술 문서 PDF 생성"
    )
    parser.add_argument(
        "--output",
        default="고문서_손상영역_인식시스템_기술문서.pdf",
        help="출력 PDF 파일명 (기본값: 고문서_손상영역_인식시스템_기술문서.pdf)",
    )
    parser.add_argument(
        "--html-only",
        action="store_true",
        help="PDF 대신 중간 HTML 파일만 생성",
    )
    args = parser.parse_args()

    # 스크립트 위치 기준으로 manual 디렉토리 결정
    script_dir = Path(__file__).resolve().parent
    manual_dir = script_dir

    print("Markdown 파일 병합 중...")
    merged_md = merge_markdown_files(manual_dir)

    if not merged_md.strip():
        print("오류: 병합할 Markdown 파일이 없습니다.")
        sys.exit(1)

    print("Markdown -> HTML 변환 중...")
    body_html = markdown_to_html(merged_md)
    full_html = build_full_html(body_html)

    if args.html_only:
        html_output = args.output.replace(".pdf", ".html")
        Path(html_output).write_text(full_html, encoding="utf-8")
        print(f"HTML 파일 생성 완료: {html_output}")
        return

    output_path = manual_dir / args.output
    print(f"PDF 생성 중: {output_path}")
    html_to_pdf(full_html, str(output_path))
    print(f"PDF 생성 완료: {output_path}")


if __name__ == "__main__":
    main()
