"""공통 헤더·푸터를 각 HTML 파일에 미리 넣습니다.

assets/js/layout.js 가 브라우저에서 그리던 메뉴·하단 정보를 원본 HTML에 그대로 넣어,
스크립트를 실행하지 않는 검색엔진·AI 크롤러도 메뉴와 사무소 정보를 읽을 수 있게 합니다.
- 처음: <div id="header"></div>, <div id="footer"></div> 자리를 채웁니다.
- 이후: <!-- LAYOUT:HEADER --> ... <!-- /LAYOUT:HEADER --> 사이를 다시 만듭니다.
layout.js 를 고친 뒤 이 스크립트(또는 build_cases.py)를 실행하면 모든 페이지에 반영됩니다.
node 가 없으면 건너뜁니다(이 경우 브라우저에서 layout.js 가 대신 그립니다).
"""
import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

BLOCKS = {
    "header": (re.compile(r'<div id="header"></div>|<!-- LAYOUT:HEADER -->.*?<!-- /LAYOUT:HEADER -->', re.S),
               "<!-- LAYOUT:HEADER -->", "<!-- /LAYOUT:HEADER -->"),
    "footer": (re.compile(r'<div id="footer"></div>|<!-- LAYOUT:FOOTER -->.*?<!-- /LAYOUT:FOOTER -->', re.S),
               "<!-- LAYOUT:FOOTER -->", "<!-- /LAYOUT:FOOTER -->"),
}
PAGE_RE = re.compile(r'<body[^>]*\bdata-page="([^"]*)"')


def build():
    node = shutil.which("node")
    if not node:
        print("node 가 없어 헤더·푸터 미리 넣기를 건너뜁니다.")
        return
    pages = {}
    for f in sorted(ROOT.glob("*.html")):
        m = PAGE_RE.search(f.read_text(encoding="utf-8"))
        if m:
            pages[f] = m.group(1) or "_"
    keys = sorted(set(pages.values()))
    res = subprocess.run([node, str(ROOT / "_tools" / "render_layout.js"), *keys],
                         capture_output=True, text=True, check=True)
    rendered = json.loads(res.stdout)
    changed = 0
    for f, key in pages.items():
        text = f.read_text(encoding="utf-8")
        new = text
        for part, (pat, start, end) in BLOCKS.items():
            html = rendered[key].get(part)
            if html:
                new = pat.sub(lambda _m: f"{start}{html}{end}", new, count=1)
        if new != text:
            f.write_text(new, encoding="utf-8")
            changed += 1
    print(f"헤더·푸터 미리 넣기: {changed}개 파일 갱신")


if __name__ == "__main__":
    build()
