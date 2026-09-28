#!/usr/bin/env python3
"""법률사무소 올본 — 업무사례 자동 생성기

_cases/*.md 파일 하나가 업무사례 하나입니다. 이 스크립트를 실행하면
  1) 사례별 상세 페이지 (case-<분야>-<번호>.html, 예: case-ip-001.html)
  2) 업무사례 목록 카드 (cases.html)
  3) 메인 화면 업무사례 슬라이더 (index.html, 최신 6건)
  4) sitemap.xml
  5) 업무분야 페이지의 관련 업무사례 카드 (practice-<분야>.html)
  6) llms.txt (AI용 사이트 요약)
  6-1) feed.xml (업무사례 RSS — 네이버 서치어드바이저 RSS 제출용)
  7) 모든 페이지의 공통 헤더·푸터 미리 넣기 (_tools/build_layout.py, node 필요)
을 한 번에 다시 만듭니다. GitHub Actions(.github/workflows/build-cases.yml)가
_cases 폴더가 바뀔 때마다 자동으로 실행합니다.

주소(번호) 규칙
  · 새 사례에는 분야별 다음 번호가 자동으로 붙고, 그 번호가 .md 머리말의 id 에 기록됩니다.
  · 한 번 발급된 번호는 _tools/issued_ids.txt 에 남아 다시 쓰이지 않습니다(사례를 지워도).
  · 나중에 분야(category)를 바꿔도 id(주소)는 그대로 유지됩니다.

사용법:  python _tools/build_cases.py
필요 패키지:  pip install markdown pyyaml
"""
import html
import json
import re
import sys
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
BLOG = "https://blog.naver.com/law_jhk"
KAKAO = "https://open.kakao.com/o/sblxZ3Ki"
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
LEDGER = ROOT / "_tools" / "issued_ids.txt"
ID_RE = re.compile(r"^(" + "|".join(CATEGORIES) + r")-(\d{3,})$")


def read_ledger():
    if not LEDGER.exists():
        return set()
    return {ln.strip() for ln in LEDGER.read_text(encoding="utf-8").splitlines()
            if ln.strip() and not ln.startswith("#")}


def write_ledger(ids):
    head = ("# 발급된 업무사례 번호 목록 — 자동 관리됩니다. 번호는 다시 쓰지 않으므로 지우지 마세요.\n")
    LEDGER.write_text(head + "\n".join(sorted(ids)) + "\n", encoding="utf-8")


def next_id(category, issued):
    nums = [int(ID_RE.match(i).group(2)) for i in issued
            if ID_RE.match(i) and ID_RE.match(i).group(1) == category]
    return f"{category}-{(max(nums) + 1 if nums else 1):03d}"


def stamp_id(path, new_id):
    """사례 .md 머리말 맨 위에 id 줄을 기록한다."""
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"^---\s*\n", f"---\nid: {new_id}\n", text, count=1)
    path.write_text(text, encoding="utf-8")


def load_cases():
    issued = read_ledger()
    loaded = []
    for path in sorted(SRC.glob("*.md")):
        if path.name.startswith("_"):
            continue  # _TEMPLATE.md 등 견본 파일은 건너뜀
        text = path.read_text(encoding="utf-8")
        m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.S)
        if not m:
            sys.exit(f"[오류] {path.name}: 맨 위 '---' 머리말(front matter)이 없습니다.")
        meta = yaml.safe_load(m.group(1)) or {}
        meta["body_md"] = m.group(2)
        meta["_file"] = path
        loaded.append(meta)

    # 이미 번호가 있는 사례 확인 (중복·형식)
    seen = {}
    for meta in loaded:
        if meta.get("id"):
            cid = str(meta["id"])
            if not ID_RE.match(cid):
                sys.exit(f"[오류] {meta['_file'].name}: id '{cid}' 형식이 잘못되었습니다 (예: ip-001).")
            if cid in seen:
                sys.exit(f"[오류] {meta['_file'].name}, {seen[cid]}: 같은 번호 {cid} 를 쓰고 있습니다.")
            seen[cid] = meta["_file"].name
            meta["id"] = cid
            issued.add(cid)

    cases = []
    for meta in loaded:
        name = meta["_file"].name
        if not meta.get("published", True):
            continue  # 임시 저장(비공개) 사례는 번호를 받지 않음
        for key in ("date", "category", "title", "card_title", "card_result", "summary"):
            if not meta.get(key):
                sys.exit(f"[오류] {name}: '{key}' 항목이 비어 있습니다.")
        if meta["category"] not in CATEGORIES:
            sys.exit(f"[오류] {name}: category는 {', '.join(CATEGORIES)} 중 하나여야 합니다.")
        also = meta.get("also_in") or []
        if isinstance(also, str):
            also = [also]
        for a in also:
            if a not in CATEGORIES:
                sys.exit(f"[오류] {name}: also_in은 {', '.join(CATEGORIES)} 중에서 골라야 합니다.")
        meta["also_in"] = [a for a in also if a != meta["category"]]
        blog = meta.get("blog") or []
        for b in blog:
            if not isinstance(b, dict) or not b.get("title") or not str(b.get("url", "")).startswith("https://"):
                sys.exit(f"[오류] {name}: blog 항목은 '- title: 글 제목' / '  url: https://...' 형식이어야 합니다.")
        meta["blog"] = blog
        meta["date"] = str(meta["date"])
        meta["updated"] = str(meta.get("updated") or meta["date"])
        if isinstance(meta["card_title"], str):
            meta["card_title"] = [meta["card_title"]]
        cases.append(meta)

    # 번호가 없는 새 사례: 게시일 → 파일 이름 순으로 분야별 다음 번호 발급
    for meta in sorted((c for c in cases if not c.get("id")), key=lambda c: (c["date"], c["_file"].name)):
        meta["id"] = next_id(meta["category"], issued)
        issued.add(meta["id"])
        stamp_id(meta["_file"], meta["id"])
        print(f"새 번호 발급: {meta['_file'].name} → {meta['id']}")
    write_ledger(issued)

    for meta in cases:
        meta["url_path"] = f"case-{meta['id']}.html"
    cases.sort(key=lambda c: (c["date"], c["id"]), reverse=True)
    return cases


# --------------------------------------------------------------------------
# 2. 카드 (목록·메인 공용)
# --------------------------------------------------------------------------
def card_html(c, extra_class="case-card"):
    title = "<br>".join(esc(line) for line in c["card_title"])
    cat = c["category"]
    cats = " ".join([cat] + c.get("also_in", []))
    return (
        f'<a class="{extra_class} ob-card" href="{c["url_path"]}" data-cat="{cat}" data-cats="{cats}">\n'
        f'  <span class="ob-card__band" aria-hidden="true"></span>\n'
        f'  <span class="ob-card__body">\n'
        f'    <span class="ob-card__cat">{CATEGORIES[cat]}</span>\n'
        f'    <span class="ob-card__type">{esc(c.get("case_type", ""))}</span>\n'
        f'    <strong class="ob-card__title">{title}</strong>\n'
        f'    <span class="ob-card__rule" aria-hidden="true"></span>\n'
        f'    <span class="ob-card__result">{CHECK_SVG}{esc(c["card_result"])}</span>\n'
        f'  </span>\n'
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
            "author": {"@type": "Person", "@id": SITE + "/#kimjaehoon", "name": AUTHOR["name"],
                       "jobTitle": AUTHOR["title"], "url": AUTHOR["url"], "sameAs": [BLOG]},
            "publisher": {
                "@type": "LegalService",
                "@id": SITE + "/#office",
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
    if c.get("blog"):
        graph[0]["relatedLink"] = [b["url"] for b in c["blog"]]
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
    blog_html = ""
    if c.get("blog"):
        items = "".join(
            f'<li><a href="{esc(b["url"])}" target="_blank" rel="noopener">{esc(b["title"])}</a></li>'
            for b in c["blog"]
        )
        blog_html = (f'<aside class="case-view__blog" aria-label="관련 해설 글">'
                     f'<strong>이 사례를 쟁점별로 풀어 쓴 글 (네이버 블로그)</strong><ul>{items}</ul></aside>')
    note = f'<p class="case-view__note">{esc(c["note"])}</p>' if c.get("note") else ""
    note += (f'\n        <p class="case-view__area">관련 업무분야 · '
             f'<a href="practice-{c["category"]}.html">{CATEGORIES[c["category"]]}</a></p>')
    cta_title = esc(c.get("cta_title") or "비슷한 상황이신가요?")
    cta_desc = esc(c.get("cta_desc") or "자료를 보내주시면 검토 후 대응 방향을 말씀드립니다.")

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<!-- 이 파일은 _cases/{c['_file'].name} 에서 자동 생성됩니다. 직접 고치지 말고 원본 .md 를 수정하세요. -->
<title>{esc(c['title'])} | 업무사례 | 법률사무소 올본</title>
<meta name="description" content="{esc(desc)}">
<meta name="keywords" content="{esc(keywords)}">
<meta name="author" content="변호사·변리사 김재훈">
<link rel="canonical" href="{canonical}">
<link rel="alternate" type="application/rss+xml" title="법률사무소 올본 업무사례" href="{SITE}/feed.xml">
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

        {blog_html}

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
    new = pat.sub(lambda m: m.group(1) + "\n" + content + "\n" + m.group(3).lstrip("\n"), text)
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

    # 업무분야 페이지마다 해당 분야 사례 카드 (<!-- RELATED:START --> … <!-- RELATED:END -->)
    for cat in CATEGORIES:
        page = ROOT / f"practice-{cat}.html"
        if page.exists():
            related = "\n\n".join(card_html(c) for c in cases
                                    if c["category"] == cat or cat in c.get("also_in", []))
            replace_block(page, "RELATED", indent(related, 12))

    write_llms(cases)
    write_feed(cases)

    print(f"업무사례 {len(cases)}건 반영 완료: " + ", ".join(c["url_path"] for c in cases))

    # 공통 헤더·푸터를 모든 페이지 원본 HTML에 미리 넣기 (검색엔진·AI 크롤러용)
    import build_layout
    build_layout.build()


# --------------------------------------------------------------------------
# 5. llms.txt — AI가 사이트를 요약해 읽을 수 있도록 주요 페이지와 사례 목록 제공
# --------------------------------------------------------------------------
def write_llms(cases):
    lines = [
        "# 법률사무소 올본 (OLBON LAW OFFICE)",
        "",
        "> 서울 강남구 테헤란로 138 성홍타워 4층(2호선 역삼역 3번 출구 도보 1분)에 있는 법률사무소입니다. "
        "대표 변호사 김재훈(변호사·변리사)이 형사·지식재산권·민사·행정·가사 사건을 상담부터 종결까지 직접 수행합니다.",
        "",
        "- 대표 변호사: 김재훈 (변호사 시험 제9회, 변리사 시험 제49회, 연세대 전기전자공학과, 서강대 법학전문대학원)",
        "- 이전 소속: 리앤목 특허법인, 리인터내셔널 특허법률사무소, 법무법인 테헤란, 법무법인(유한) 동인 형사팀, 법무법인(유) 지평 IPIT그룹",
        "- 상담: 카카오톡 오픈채팅, 이메일 jhkim@olbonlaw.com (방문 상담 사전 예약제)",
        f"- 네이버 블로그: {BLOG} (업무사례의 쟁점별 해설 글)",
        "",
        "## 주요 페이지",
        f"- [사무소 소개]({SITE}/about.html): 인사말과 사무소 운영 원칙",
        f"- [대표 변호사 소개]({SITE}/attorney.html): 학력, 자격, 경력, 대외활동",
        f"- [업무사례 목록]({SITE}/cases.html): 실제 수행 사건을 분야별로 정리",
        f"- [상담 안내]({SITE}/consult.html): 상담 절차, 방법, 자주 묻는 질문",
        f"- [오시는 길]({SITE}/location.html): 위치와 교통",
        "",
        "## 업무분야",
    ]
    for cat, name in CATEGORIES.items():
        lines.append(f"- [{name}]({SITE}/practice-{cat}.html)")
    lines += ["", "## 업무사례"]
    for c in cases:
        desc = (c.get("description") or c.get("lead", "")).strip()
        lines.append(f"- [{c['title']}]({SITE}/{c['url_path']}): {desc}")
    lines.append("")
    out = ROOT / "llms.txt"
    text = "\n".join(lines)
    if not out.exists() or out.read_text(encoding="utf-8") != text:
        out.write_text(text, encoding="utf-8")


# --------------------------------------------------------------------------
# 6. feed.xml — 업무사례 RSS (네이버 서치어드바이저 'RSS 제출'에 등록)
# --------------------------------------------------------------------------
def write_feed(cases):
    from email.utils import format_datetime
    from datetime import datetime, timezone, timedelta
    kst = timezone(timedelta(hours=9))

    def rfc822(d):
        return format_datetime(datetime.fromisoformat(d).replace(hour=9, tzinfo=kst))

    items = []
    for c in cases:
        url = f"{SITE}/{c['url_path']}"
        desc = (c.get("description") or c.get("lead", "")).strip()
        cats = "".join(f"<category>{esc(CATEGORIES[x])}</category>" for x in [c["category"]] + c.get("also_in", []))
        items.append(
            f"    <item>\n      <title>{esc(c['title'])}</title>\n      <link>{url}</link>\n"
            f"      <guid isPermaLink=\"true\">{url}</guid>\n      <pubDate>{rfc822(c['date'])}</pubDate>\n"
            f"      {cats}\n      <description>{esc(desc)}</description>\n    </item>"
        )
    last = max((c["updated"] for c in cases), default="2026-01-01")
    text = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n  <channel>\n'
        "    <title>법률사무소 올본 업무사례</title>\n"
        f"    <link>{SITE}/cases.html</link>\n"
        f'    <atom:link href="{SITE}/feed.xml" rel="self" type="application/rss+xml"/>\n'
        "    <description>변호사·변리사 김재훈이 수행한 형사·지식재산권·민사·행정·가사 사건을 쟁점별로 정리한 업무사례</description>\n"
        "    <language>ko</language>\n"
        f"    <lastBuildDate>{rfc822(last)}</lastBuildDate>\n"
        + "\n".join(items) + "\n  </channel>\n</rss>\n"
    )
    out = ROOT / "feed.xml"
    if not out.exists() or out.read_text(encoding="utf-8") != text:
        out.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    build()
