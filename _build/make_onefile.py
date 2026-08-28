# -*- coding: utf-8 -*-
"""
단일 파일(올인원) 미리보기 빌드 스크립트
────────────────────────────────────────────────────────────────
13개 페이지 + CSS + JS + 이미지를 HTML 한 장에 모두 담습니다.
휴대폰·태블릿에서 파일 하나만 열어도 전체 사이트가 그대로 동작합니다.

실행:  python3 _build/make_onefile.py
결과:  올본-미리보기.html  (실서버 업로드용이 아니라 확인용입니다)
"""
import os, re, io, base64, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

PAGES = [
    ("index",             "index.html"),
    ("about",             "about.html"),
    ("location",          "location.html"),
    ("attorney",          "attorney.html"),
    ("practice-civil",    "practice-civil.html"),
    ("practice-criminal", "practice-criminal.html"),
    ("practice-family",   "practice-family.html"),
    ("practice-admin",    "practice-admin.html"),
    ("practice-ip",       "practice-ip.html"),
    ("cases",             "cases.html"),
    ("case-view",         "case-view.html"),
    ("consult",           "consult.html"),
    ("privacy",           "privacy.html"),
]
ROUTES = {r for r, _ in PAGES}

read = lambda p: io.open(p, encoding="utf-8").read()

# ── 이미지 → data URI ────────────────────────────────────────────
MIME = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
        ".svg": "image/svg+xml", ".webp": "image/webp", ".gif": "image/gif"}

_cache = {}
def data_uri(path):
    if path in _cache:
        return _cache[path]
    if not os.path.exists(path):
        return path
    ext = os.path.splitext(path)[1].lower()
    b64 = base64.b64encode(open(path, "rb").read()).decode()
    uri = "data:%s;base64,%s" % (MIME.get(ext, "application/octet-stream"), b64)
    _cache[path] = uri
    return uri

def embed_images(html):
    html = re.sub(r'src="(assets/images/[^"]+)"',
                  lambda m: 'src="%s"' % data_uri(m.group(1)), html)
    html = re.sub(r"url\('(assets/images/[^']+)'\)",
                  lambda m: "url('%s')" % data_uri(m.group(1)), html)
    html = re.sub(r'href="(assets/images/[^"]+)"',
                  lambda m: 'href="%s"' % data_uri(m.group(1)), html)
    return html

# ── 링크 재작성 : xxx.html[#anchor] → #/xxx[~anchor] ──────────────
def rewrite_links(text):
    def rep(m):
        page, anchor = m.group(1), m.group(3)
        if page not in ROUTES:
            return m.group(0)
        return '#/%s%s' % (page, ("~" + anchor) if anchor else "")
    return re.sub(r'([a-z0-9\-]+)\.html(#([A-Za-z0-9_\-]+))?', rep, text)

# ── 페이지별 id 접두어 부여 (중복 id 방지) ─────────────────────────
ATTRS = ("aria-labelledby", "aria-controls", "aria-describedby", "for")

def prefix_ids(frag, route):
    ids = set(re.findall(r'\sid="([^"]+)"', frag))
    if not ids:
        return frag
    new = lambda x: "%s__%s" % (route, x)

    frag = re.sub(r'(\sid=")([^"]+)(")',
                  lambda m: m.group(1) + new(m.group(2)) + m.group(3), frag)

    def fix_ref(m):
        vals = [new(v) if v in ids else v for v in m.group(2).split()]
        return m.group(1) + " ".join(vals) + m.group(3)
    for a in ATTRS:
        frag = re.sub(r'(%s=")([^"]+)(")' % a, fix_ref, frag)

    frag = re.sub(r'href="#([A-Za-z0-9_\-]+)"',
                  lambda m: 'href="#%s"' % (new(m.group(1)) if m.group(1) in ids else m.group(1)),
                  frag)
    return frag

# ── 페이지 수집 ──────────────────────────────────────────────────
pages_html, titles = [], {}
for route, fname in PAGES:
    src = read(fname)
    titles[route] = re.search(r"<title>(.*?)</title>", src, re.S).group(1).strip()
    body_tag = re.search(r"<body([^>]*)>", src).group(1)
    is_sub = 'is-sub' in body_tag
    nav_key = re.search(r'data-page="([^"]*)"', body_tag)
    nav_key = nav_key.group(1) if nav_key else ""

    frag = re.search(r"<main id=\"main\">(.*?)</main>", src, re.S).group(1)
    frag = prefix_ids(frag, route)
    frag = rewrite_links(frag)

    pages_html.append(
        '<div class="page" data-route="%s" data-sub="%s" data-nav="%s" hidden>\n'
        '<main>%s</main>\n</div>' % (route, "1" if is_sub else "", nav_key, frag))

# ── CSS ─────────────────────────────────────────────────────────
css = "\n".join(read("assets/css/%s.css" % n) for n in ("common", "main", "sub"))
css = css.replace('@charset "utf-8";', "")

STANDALONE_CSS = """
/* ══════════════════════════════════════════════════════════════
   단일 파일 미리보기 전용 스타일
   (Swiper CDN 없이도 히어로/성공사례가 정상 표시되도록 처리)
   ══════════════════════════════════════════════════════════════ */
.page[hidden] { display: none !important; }
.hero .hero__slide { display: none; }
.hero .hero__slide.swiper-slide-active { display: flex; animation: heroFade .7s ease both; }
@keyframes heroFade { from { opacity: .3 } to { opacity: 1 } }
.cases .swiper { overflow: hidden; }
.cases .swiper-wrapper { display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; }
@media (max-width: 1024px) { .cases .swiper-wrapper { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 767px)  { .cases .swiper-wrapper { grid-template-columns: 1fr; } }
.cases__nav { display: none; }
.preview-note {
  position: fixed; left: 50%; bottom: 76px; z-index: 400; transform: translateX(-50%);
  display: flex; align-items: center; gap: 10px;
  max-width: calc(100% - 32px); padding: 10px 14px;
  background: rgba(15, 37, 64, .94); color: #fff; border-radius: 100px;
  font-size: 12.5px; line-height: 1.4; box-shadow: 0 8px 24px rgba(0,0,0,.25);
}
.preview-note b { color: #D9C08F; font-weight: 700; }
.preview-note button {
  flex: none; width: 22px; height: 22px; border-radius: 50%;
  background: rgba(255,255,255,.16); color: #fff; font-size: 14px; line-height: 1;
}
@media (min-width: 1025px) { .preview-note { bottom: 20px; } }
"""

# ── JS ──────────────────────────────────────────────────────────
layout_js = read("assets/js/layout.js")
layout_js = rewrite_links(layout_js)
layout_js = layout_js.replace(
    "'<li class=\"gnb__item' + cur + '\">'",
    "'<li class=\"gnb__item' + cur + '\" data-navkey=\"' + item.key + '\">'")

common_js = read("assets/js/common.js")
common_js = rewrite_links(common_js)
# 단일 파일 모드에서는 body.is-sub 를 라우터가 실시간으로 토글합니다.
common_js = common_js.replace(
    'var isSub = body.classList.contains("is-sub");',
    'var isSub = false; /* 단일 파일 모드: 라우터가 body.is-sub 를 토글 */')
common_js = common_js.replace(
    """      var onScroll = function () {
        if (window.scrollY > 40) header.classList.add("is-solid");
        else header.classList.remove("is-solid");
      };""",
    """      var onScroll = function () {
        if (body.classList.contains("is-sub")) { header.classList.add("is-solid"); return; }
        if (window.scrollY > 40) header.classList.add("is-solid");
        else header.classList.remove("is-solid");
      };
      window.__olbonSyncHeader = onScroll;""")
common_js = common_js.replace(
    'if (!isSub && window.scrollY <= 40) header.classList.remove("is-solid");',
    'if (!body.classList.contains("is-sub") && window.scrollY <= 40) header.classList.remove("is-solid");')
# 라우터용 해시(#/xxx)는 앵커 스크롤 처리에서 제외
common_js = common_js.replace(
    """    var a = e.target.closest('a[href^="#"]:not([href="#"])');
    if (!a) return;""",
    """    var a = e.target.closest('a[href^="#"]:not([href="#"])');
    if (!a) return;
    if (a.getAttribute("href").indexOf("#/") === 0) return;   /* 라우터가 처리 */""")
common_js = common_js.replace(
    """  window.addEventListener("load", function () {
    if (!location.hash) return;""",
    """  window.addEventListener("load", function () {
    if (!location.hash || location.hash.indexOf("#/") === 0) return;""")

ROUTER_JS = """
/* ══════════════════════════════════════════════════════════════
   단일 파일 미리보기 — 해시 라우터
   #/<페이지>            예) #/attorney
   #/<페이지>~<앵커>     예) #/consult~consult-form , #/cases~ip
   ══════════════════════════════════════════════════════════════ */
(function () {
  "use strict";
  var pages  = [].slice.call(document.querySelectorAll(".page"));
  var titles = %s;
  var NAVMAP = { location: "about", "practice-civil": "practice", "practice-criminal": "practice",
                 "practice-family": "practice", "practice-admin": "practice", "practice-ip": "practice",
                 "case-view": "cases" };

  function byRoute(r) {
    for (var i = 0; i < pages.length; i++) if (pages[i].dataset.route === r) return pages[i];
    return null;
  }

  function go(hash, initial) {
    var raw = (hash || "").replace(/^#\\//, "");
    var parts = raw.split("~");
    var route = parts[0] || "index";
    var anchor = parts[1] || "";
    var page = byRoute(route) || byRoute("index");
    route = page.dataset.route;

    pages.forEach(function (p) { p.hidden = p !== page; });

    document.body.classList.toggle("is-sub", page.dataset.sub === "1");
    document.body.setAttribute("data-page", page.dataset.nav || "");
    if (titles[route]) document.title = titles[route];

    var key = NAVMAP[route] || route;
    [].forEach.call(document.querySelectorAll(".gnb__item"), function (li) {
      var on = li.dataset.navkey === key;
      li.classList.toggle("is-current", on);
      var a = li.querySelector(".gnb__link");
      if (a) { if (on) a.setAttribute("aria-current", "page"); else a.removeAttribute("aria-current"); }
    });
    if (window.__olbonSyncHeader) window.__olbonSyncHeader();

    if (anchor) {
      var filter = page.querySelector('[data-case-filter="' + anchor + '"]');
      if (filter) { filter.click(); window.scrollTo(0, 0); return; }
      var el = document.getElementById(route + "__" + anchor);
      if (el) {
        var hd = document.getElementById("siteHeader");
        var off = (hd ? hd.offsetHeight : 70) + 12;
        setTimeout(function () {
          window.scrollTo({ top: el.getBoundingClientRect().top + window.scrollY - off,
                            behavior: initial ? "auto" : "smooth" });
        }, 60);
        return;
      }
    }
    window.scrollTo(0, 0);
  }

  window.addEventListener("hashchange", function () { go(location.hash, false); });
  go(location.hash, true);

  /* 안내 배너 */
  var note = document.createElement("div");
  note.className = "preview-note";
  note.innerHTML = '<span><b>미리보기 파일</b> · 모든 페이지가 이 파일 하나에 들어 있습니다.</span>' +
                   '<button type="button" aria-label="안내 닫기">&times;</button>';
  document.body.appendChild(note);
  note.querySelector("button").addEventListener("click", function () { note.remove(); });
  setTimeout(function () { if (note.parentNode) note.remove(); }, 9000);
})();
""" % json.dumps(titles, ensure_ascii=False)

HERO_JS = """
/* 히어로 슬라이더 (Swiper 없이 동작하는 경량 버전) */
(function () {
  "use strict";
  var slides = [].slice.call(document.querySelectorAll(".hero__slide"));
  if (!slides.length) return;
  var cur = 0, timer = null;
  var curEl = document.querySelector("[data-hero-current]");
  var totEl = document.querySelector("[data-hero-total]");
  var barEl = document.querySelector("[data-hero-bar]");
  var pad = function (n) { return (n < 10 ? "0" : "") + n; };

  function show(i) {
    cur = (i + slides.length) % slides.length;
    slides.forEach(function (s, idx) { s.classList.toggle("swiper-slide-active", idx === cur); });
    if (curEl) curEl.textContent = pad(cur + 1);
    if (totEl) totEl.textContent = pad(slides.length);
    if (barEl) barEl.style.width = ((cur + 1) / slides.length * 100) + "%";
  }
  function play()  { stop(); timer = setInterval(function () { show(cur + 1); }, 5500); }
  function stop()  { if (timer) clearInterval(timer); timer = null; }

  var prev = document.querySelector(".hero__prev"), next = document.querySelector(".hero__next");
  if (prev) prev.addEventListener("click", function () { show(cur - 1); play(); });
  if (next) next.addEventListener("click", function () { show(cur + 1); play(); });

  var hero = document.querySelector(".hero");
  if (hero) {
    hero.addEventListener("mouseenter", stop);
    hero.addEventListener("mouseleave", play);
    /* 모바일 스와이프 */
    var x0 = null;
    hero.addEventListener("touchstart", function (e) { x0 = e.touches[0].clientX; stop(); }, { passive: true });
    hero.addEventListener("touchend", function (e) {
      if (x0 === null) return;
      var dx = e.changedTouches[0].clientX - x0;
      if (Math.abs(dx) > 45) show(cur + (dx < 0 ? 1 : -1));
      x0 = null; play();
    }, { passive: true });
  }
  show(0); play();
})();
"""

# ── 조립 ────────────────────────────────────────────────────────
favicon = data_uri("assets/images/favicon.svg")
og = data_uri("assets/images/og-image.jpg")

doc = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>법률사무소 올본 | 지식재산권·특허소송 중심 법률사무소</title>
<meta name="description" content="법률사무소 올본 — 변리사·변호사 이중 자격의 김재훈 대표변호사가 지식재산권 및 민사·형사·가사·행정 사건을 직접 수행합니다.">
<meta property="og:title" content="법률사무소 올본">
<meta property="og:description" content="기술을 아는 변호사가 권리를 지킵니다.">
<meta property="og:image" content="%(og)s">
<link rel="icon" href="%(favicon)s" type="image/svg+xml">
<link rel="apple-touch-icon" href="%(favicon)s">
<!-- ══════════════════════════════════════════════════════════════
     법률사무소 올본 — 단일 파일 미리보기
     CSS·JS·이미지를 모두 포함하고 있어 인터넷 연결이나
     별도 폴더 없이 이 파일 하나만으로 전체 사이트가 동작합니다.
     휴대폰·태블릿에서 확인하실 때 사용하세요.
     ※ 실제 서버에는 원본 폴더(index.html + assets/)를 올리시면 됩니다.
     ══════════════════════════════════════════════════════════════ -->
<style>
%(css)s
%(standalone_css)s
</style>
</head>
<body data-page="home">
<div id="header"></div>
%(pages)s
<div id="footer"></div>
<script>
%(layout_js)s
</script>
<script>
%(common_js)s
</script>
<script>
%(router_js)s
</script>
<script>
%(hero_js)s
</script>
</body>
</html>
""" % dict(css=css, standalone_css=STANDALONE_CSS, pages="\n".join(pages_html),
           layout_js=layout_js, common_js=common_js, router_js=ROUTER_JS,
           hero_js=HERO_JS, favicon=favicon, og=og)

doc = embed_images(doc)

out = "olbon-preview.html"
io.open(out, "w", encoding="utf-8").write(doc)
print("생성 완료:", out, "|", round(len(doc.encode("utf-8")) / 1024), "KB")
