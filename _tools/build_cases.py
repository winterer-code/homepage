#!/usr/bin/env python3
"""법률사무소 올본 — 업무사례 자동 생성기

_cases/*.md 파일 하나가 업무사례 하나입니다. 이 스크립트를 실행하면
  1) 사례별 상세 페이지 (case-<slug>.html)
  2) 업무사례 목록 카드 (cases.html)
  3) 메인 화면 업무사례 슬라이더 (index.html, 최신 6건)
  4) sitemap.xml
을 한 번에 다시 만듭니다. GitHub Actions(.github/workflows/build-cases.yml)가
_cases 폴더가 바뀔 때마다 자동으로 실행합니다.

사용법:  python _tools/build_cases.py
필요 패키지:  pip install markdown pyyaml
"""
import html
import json
import re
import sys
from datetime import date
from pathlib import Path

import markdown
import yaml

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "_cases"
SITE = "https://www.olbonlaw.com"

CATEGORIES = {
    "criminal": "형사",
    "ip": "지식재산권",
    "civil": "민사",
    "admin": "행정",
    "family": "가사",
}
HOME_SLIDES = 6

AUTHOR = {"name": "김재훈", "title": "대표 변호사 · 변리사", "url": SITE + "/attorney.html"}
KAKAO = "https://open.kakao.com/o/syCkuapi"
MAIL = ("mailto:jhkim@olbonlaw.com?subject=%5B%EC%83%81%EB%8B%B4%20%EB%AC%B8%EC%9D%98%5D&body="
        "%EC%84%B1%ED%95%A8%20%3A%20%0A%EC%97%B0%EB%9D%BD%EC%B2%98%20%3A%20%0A%EC%83%81%EB%8B%B4%20"
        "%EB%B6%84%EC%95%BC%20%3A%20%0A%0A%5B%EC%82%AC%EA%B1%B4%20%EA%B2%BD%EC%9C%84%5D%0A%0A%0A%E2"
        "%80%BB%20%EA%B4%80%EB%A0%A8%20%EC%9E%90%EB%A3%8C%28%EA%B3%84%EC%95%BD%EC%84%9C%C2%B7%EB%82"
        "%B4%EC%9A%A9%EC%A6%9D%EB%AA%85%C2%B7%EA%B3%A0%EC%86%8C%EC%9E%A5%C2%B7%ED%8A%B9%ED%97%88%EA"
        "%B3%B5%EB%B3%B4%20%EB%93%B1%29%EA%B0%80%20%EC%9E%88%EC%9C%BC%EC%8B%9C%EB%A9%B4%20%ED%95%A8"
        "%EA%BB%98%20%EC%B2%A8%EB%B6%80%ED%95%B4%20%EC%A3%BC%EC%84%B8%EC%9A%94.")

CHECK_SVG = ('<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" '
             'aria-hidden="true"><path d="M3 8.5l3.2 3L13 4.5"/></svg>')
HOME_SVG = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3 2.5 11h2.7v9h5.1v-5.4h3.4V20h5.1v-9'
            'h2.7L12 3Z"/></svg>')

esc = html.escape


# --------------------------------------------------------------------------
# 1. 사례 파일 읽기
# --------------------------------------------------------------------------
def load_cases():
    cases = []
    for path in sorted(SRC.glob("*.md")):
        if path.name.startswith("_"):
            continue  # _TEMPLATE.md 등 견본 파일은 건너뜀
        text = path.read_text(encoding="utf-8")
        m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.S)
        if not m:
            sys.exit(f"[오류] {path.name}: 맨 위 '---' 머리말(front matter)이 없습니다.")
        meta = yaml.safe_load(m.group(1)) or {}
        meta["body_md"] = m.group(2)
        meta.setdefault("slug", path.stem)
        if not meta.get("published", True):
            continue
        for key in ("date", "category", "title", "card_title", "card_result", "summary"):
            if not meta.get(key):
                sys.exit(f"[오류] {path.name}: '{key}' 항목이 비어 있습니다.")
        if meta["category"] not in CATEGORIES:
            sys.exit(f"[오류] {path.name}: category는 {', '.join(CATEGORIES)} 중 하나여야 합니다.")
        meta["date"] = str(meta["date"])
        meta["updated"] = str(meta.get("updated") or meta["date"])
        if isinstance(meta["card_title"], str):
            meta["card_title"] = [meta["card_title"]]
        meta["url_path"] = f"case-{meta['slug']}.html"
        cases.append(meta)
    cases.sort(key=lambda c: (c["date"], c["slug"]), reverse=True)
    return cases


# --------------------------------------------------------------------------
# 2. 카드 (목록·메인 공용)
# --------------------------------------------------------------------------
def card_html(c, extra_class="case-card"):
    title = "<br>".join(esc(line) for line in c["card_title"])
    cat = c["category"]
    return (
        f'<a class="{extra_class} ob-card" href="{c["url_path"]}" data-cat="{cat}">\n'
        f'  <span class="ob-card__band" aria-hidden="true"></span>\n'
        f'  <span class="ob-card__body">\n'
        f'    <span class="ob-card__cat">{CATEGORIES[cat]}</span>\n'
        f'    <span class="ob-card__type">{esc(c.get("case_type", ""))}</span>\n'
        f'    <strong class="ob-card__title">{title}</strong>\n'
        f'    <span class="ob-card__rule" aria-hidden="true"></span>\n'
        f'    <span class="ob-card__result">{CHECK_SVG}{esc(c["card_result"])}</span>\n'
        f'  </span>\n'
        f'  <span class="ob-card__foot"><img src="assets/images/logo-full.png" alt="법률사무소 올본" '
        f'width="141" height="32" loading="lazy"></span>\n'
        f'</a>'
    )


# --------------------------------------------------------------------------
# 3. 상세 페이지
# --------------------------------------------------------------------------
def render_body(md_text):
    body = markdown.markdown(md_text, extensions=["tables", "sane_lists"])
    # 사이트 제목 구조에 맞춰 한 단계씩 내림: ## → h3, ### → h4
    body = re.sub(r"<(/?)h3>", r"<\1h4>", body)
    body = re.sub(r"<(/?)h2>", r"<\1h3>", body)
    toc = []

    def add_id(m):
        n = len(toc) + 1
        toc.append((f"s{n}", re.sub("<[^>]+>", "", m.group(1))))
        return f'<h3 id="s{n}">{m.group(1)}</h3>'

    body = re.sub(r"<h3>(.*?)</h3>", add_id, body)
    body = body.replace("<blockquote>", '<blockquote class="case-view__result">')
    body = body.replace("<table>", '<div class="case-view__tbl"><table>').replace("</table>", "</table></div>")
    return body, toc


def jsonld(c, canonical):
    graph = [
        {
            "@type": "Article",
            "headline": c["title"],
            "description": c.get("description", c.get("lead", "")),
            "datePublished": c["date"],
            "dateModified": c["updated"],
            "inLanguage": "ko",
            "image": SITE + "/assets/images/og-image.jpg",
            "keywords": ", ".join(c.get("keywords", [])),
            "author": {"@type": "Person", "name": AUTHOR["name"], "jobTitle": AUTHOR["title"], "url": AUTHOR["url"]},
            "publisher": {
                "@type": "LegalService",
                "name": "법률사무소 올본",
                "url": SITE + "/",
                "logo": {"@type": "ImageObject", "url": SITE + "/assets/images/logo-full.png"},
            },
            "mainEntityOfPage": canonical,
        },
        {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "홈", "item": SITE + "/"},
                {"@type": "ListItem", "position": 2, "name": "업무사례", "item": SITE + "/cases.html"},
                {"@type": "ListItem", "position": 3, "name": c["title"]},
            ],
        },
    ]
    if c.get("faq"):
        graph.append({
            "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": f["a"]}}
                for f in c["faq"]
            ],
        })
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=2)


def nav_btn(target, label):
    if target:
        return f'<a href="{target["url_path"]}" class="btn btn--line btn--sm">{label}</a>'
    return f'<span class="btn btn--line btn--sm is-disabled" aria-disabled="true">{label}</span>'


def detail_html(c, older, newer):
    canonical = f"{SITE}/{c['url_path']}"
    body, toc = render_body(c["body_md"])
    faq = c.get("faq") or []
    if faq:
        toc.append(("faq", "자주 묻는 질문"))
    y, m, d = c["date"].split("-")
    date_ko = f"{int(y)}. {int(m)}. {int(d)}."
    desc = c.get("description") or c.get("lead", "")
    keywords = ", ".join(c.get("keywords", []))
    tags = "".join(f"<li>{esc(t)}</li>" for t in c.get("tags", []))
    summary_rows = "\n".join(
        f'            <tr><th scope="row">{esc(str(k))}</th><td>{v}</td></tr>' for k, v in c["summary"].items()
    )
    toc_html = "".join(f'<li><a href="#{i}">{esc(t)}</a></li>' for i, t in toc)
    faq_html = ""
    if faq:
        items = "".join(
            f"<dt>Q. {esc(f['q'])}</dt><dd>{esc(f['a'])}</dd>" for f in faq
        )
        faq_html = f'<h3 id="faq">자주 묻는 질문</h3>\n<dl class="case-view__faq">{items}</dl>'
    note = f'<p class="case-view__note">{esc(c["note"])}</p>' if c.get("note") else ""
    cta_title = esc(c.get("cta_title") or "비슷한 상황이신가요?")
    cta_desc = esc(c.get("cta_desc") or "자료를 보내주시면 검토 후 대응 방향을 말씀드립니다.")

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<!-- 이 파일은 _cases/{c['slug']}.md 에서 자동 생성됩니다. 직접 고치지 말고 원본 .md 를 수정하세요. -->
<title>{esc(c['title'])} | 업무사례 | 법률사무소 올본</title>
<meta name="description" content="{esc(desc)}">
<meta name="keywords" content="{esc(keywords)}">
<meta name="author" content="변호사·변리사 김재훈">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="법률사무소 올본">
<meta property="og:title" content="{esc(c['title'])}">
<meta property="og:description" content="{esc(c.get('lead') or desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE}/assets/images/og-image.jpg">
<meta property="og:locale" content="ko_KR">
<meta property="article:published_time" content="{c['date']}">
<meta property="article:modified_time" content="{c['updated']}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="assets/images/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="https://unpkg.com/aos@2.3.4/dist/aos.css">
<link rel="stylesheet" href="assets/css/common.css">
<link rel="stylesheet" href="assets/css/sub.css">
<link rel="stylesheet" href="assets/css/cases.css">
<script type="application/ld+json">
{jsonld(c, canonical)}
</script>
</head>

<body data-page="cases" class="is-sub">
<div id="header"></div>

<main id="main">

  <section class="subvisual">
    <div class="subvisual__inner">
      <p class="subvisual__en">Case Studies</p>
      <h2 class="subvisual__title">업무사례</h2>
    </div>
  </section>

  <nav class="breadcrumb" aria-label="현재 위치">
    <div class="container">
      <ol>
        <li><a href="index.html">{HOME_SVG}<span class="blind">홈</span></a></li>
        <li><a href="cases.html">업무사례</a></li>
        <li aria-current="page">{CATEGORIES[c['category']]}</li>
      </ol>
    </div>
  </nav>

  <div class="sub-body">
    <div class="container case-view">

      <article>
        <header class="case-view__head">
          <span class="tag{' tag--ip' if c['category'] == 'ip' else ''}">{CATEGORIES[c['category']]}</span>
          <h1 class="case-view__title">{esc(c['title'])}</h1>
          <p class="case-view__meta">
            <span>작성 <a href="attorney.html">김재훈 변호사·변리사</a></span>
            <span>게시일 <time datetime="{c['date']}">{date_ko}</time></span>
          </p>
          <ul class="case-view__tags">{tags}</ul>
        </header>

        <p class="case-view__lead">{esc(c.get('lead', ''))}</p>

        <table class="case-view__table">
          <caption class="blind">사건 요약</caption>
          <tbody>
{summary_rows}
          </tbody>
        </table>

        <nav class="case-view__toc" aria-label="목차">
          <strong>목차</strong>
          <ol>{toc_html}</ol>
        </nav>

        <div class="case-view__body">
{body}
{faq_html}
        </div>

        {note}

        <nav class="case-view__nav" aria-label="사례 이동">
          {nav_btn(older, "이전 사례")}
          <a href="cases.html" class="btn btn--navy btn--sm">목록으로</a>
          {nav_btn(newer, "다음 사례")}
        </nav>
      </article>

      <div class="cta-banner">
        <div>
          <h2 class="cta-banner__title">{cta_title}</h2>
          <p class="cta-banner__desc">{cta_desc}</p>
        </div>
        <div class="cta-banner__btns">
          <a href="{KAKAO}" class="btn btn--gold btn--lg" target="_blank" rel="noopener">카카오톡 상담</a>
          <a href="{MAIL}" class="btn btn--line-white btn--lg">이메일 상담</a>
        </div>
      </div>

    </div>
  </div>
</main>

<div id="footer"></div>

<script src="https://unpkg.com/aos@2.3.4/dist/aos.js"></script>
<script src="assets/js/layout.js"></script>
<script src="assets/js/common.js"></script>
</body>
</html>
"""


# --------------------------------------------------------------------------
# 4. 표시 구간 교체 (<!-- CASES:START --> … <!-- CASES:END -->)
# --------------------------------------------------------------------------
def replace_block(path, marker, content):
    text = path.read_text(encoding="utf-8")
    pat = re.compile(rf"(<!-- {marker}:START[^>]*-->)(.*?)(\s*<!-- {marker}:END -->)", re.S)
    if not pat.search(text):
        sys.exit(f"[오류] {path.name}: <!-- {marker}:START --> 표시를 찾지 못했습니다.")
    new = pat.sub(lambda m: m.group(1) + "\n" + content + m.group(3), text)
    if new != text:
        path.write_text(new, encoding="utf-8")


def indent(block, n):
    pad = " " * n
    return "\n".join(pad + line if line else line for line in block.splitlines())


def build():
    cases = load_cases()

    # 이전 빌드에서 만들어졌지만 지금은 없는(삭제·비공개) 상세 페이지 정리
    live = {c["url_path"] for c in cases}
    for old in ROOT.glob("case-*.html"):
        if old.name not in live and "자동 생성됩니다" in old.read_text(encoding="utf-8")[:600]:
            old.unlink()

    for i, c in enumerate(cases):
        newer = cases[i - 1] if i > 0 else None
        older = cases[i + 1] if i + 1 < len(cases) else None
        out = ROOT / c["url_path"]
        page = detail_html(c, older, newer)
        if not out.exists() or out.read_text(encoding="utf-8") != page:
            out.write_text(page, encoding="utf-8")

    cards = "\n\n".join(card_html(c) for c in cases)
    replace_block(ROOT / "cases.html", "CASES", indent(cards, 8))

    slides = "\n\n".join(
        '<div class="swiper-slide">\n' + indent(card_html(c, "case-slide-card"), 2) + "\n</div>"
        for c in cases[:HOME_SLIDES]
    )
    replace_block(ROOT / "index.html", "CASES", indent(slides, 10))

    latest = cases[0]["updated"] if cases else None
    urls = "\n".join(
        f"  <url>\n    <loc>{SITE}/{c['url_path']}</loc>\n    <lastmod>{c['updated']}</lastmod>\n"
        f"    <changefreq>yearly</changefreq>\n    <priority>0.7</priority>\n  </url>"
        for c in cases
    )
    sm = ROOT / "sitemap.xml"
    replace_block(sm, "CASES", urls)
    if latest:  # 목록 페이지의 수정일도 최신 사례 날짜로 맞춤
        text = sm.read_text(encoding="utf-8")
        text2 = re.sub(r"(<loc>https://www\.olbonlaw\.com/cases\.html</loc>\s*<lastmod>)[^<]*(</lastmod>)",
                       lambda m: m.group(1) + max(latest, re.search(
                           r"cases\.html</loc>\s*<lastmod>([^<]*)", text).group(1)) + m.group(2), text)
        if text2 != text:
            sm.write_text(text2, encoding="utf-8")

    print(f"업무사례 {len(cases)}건 반영 완료: " + ", ".join(c["url_path"] for c in cases))


if __name__ == "__main__":
    build()
