# -*- coding: utf-8 -*-
"""업무분야 서브페이지(민사/형사/가사/행정) 생성 스크립트.
   내용 수정 후 `python3 _build/gen_practice.py` 로 다시 생성할 수 있습니다."""
import os, io

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ICONS = [
    'M12 3 3 6v1.6h1.9l-2.7 6.3c0 1.6 1.5 2.9 3.3 2.9s3.3-1.3 3.3-2.9l-2.7-6.3H11V19H7v2h10v-2h-4V7.6h4.9l-2.7 6.3c0 1.6 1.5 2.9 3.3 2.9s3.3-1.3 3.3-2.9l-2.7-6.3H21V6l-9-3Z',
    'M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6Zm-1 7V3.5L18.5 9H13ZM8 12h8v2H8v-2Zm0 4h8v2H8v-2Z',
    'M12 2 4 5v6c0 5 3.4 9.7 8 11 4.6-1.3 8-6 8-11V5l-8-3Zm0 2.1 6 2.3V11c0 4-2.5 7.8-6 9-3.5-1.2-6-5-6-9V6.4l6-2.3Z',
    'M12 3 2 11h3v10h6v-6h2v6h6V11h3L12 3Zm0 2.7 6 4.8V19h-2v-6H8v6H6v-8.5l6-4.8Z',
    'M12 2 2 7v2h20V7L12 2ZM5 11v8H3v2h18v-2h-2v-8h-2v8h-3v-8h-2v8H9v-8H5Z',
    'M20 4H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2Zm0 4-8 5-8-5V6l8 5 8-5v2Z',
    'M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20Zm1 15h-2v-2h2v2Zm1.8-7.3-.9.9c-.7.7-1.1 1.3-1.1 2.4h-2v-.5c0-1.1.4-2.1 1.1-2.8l1.2-1.3c.4-.3.6-.8.6-1.4a2 2 0 0 0-4 0H8a4 4 0 0 1 8 0c0 .8-.3 1.5-.8 2.1l-.4.6Z',
    'M17 3H7a2 2 0 0 0-2 2v16l7-3 7 3V5a2 2 0 0 0-2-2Zm-2 9H9v-2h6v2Zm0-4H9V6h6v2Z',
    'M3 3h18v2H3V3Zm2 4h14v14H5V7Zm3 3v2h8v-2H8Zm0 4v2h8v-2H8Z',
    'M19 3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V5a2 2 0 0 0-2-2Zm-8 14-4-4 1.4-1.4L11 14.2l5.6-5.6L18 10l-7 7Z',
    'M21 6h-3V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v2H3v14h18V6Zm-13-2h8v2H8V4Z',
    'M12 2 1 21h22L12 2Zm1 15h-2v-2h2v2Zm0-4h-2V9h2v4Z',
]


def icon(i):
    return ('<span class="type-item__icon" aria-hidden="true"><svg viewBox="0 0 24 24">'
            '<path d="%s"/></svg></span>' % ICONS[i % len(ICONS)])


NAV = [
    ("civil", "민사", "practice-civil.html"),
    ("criminal", "형사", "practice-criminal.html"),
    ("family", "가사", "practice-family.html"),
    ("admin", "행정", "practice-admin.html"),
    ("ip", "지식재산권", "practice-ip.html"),
]

PAGES = {
"civil": dict(
    file="practice-civil.html",
    label="민사", en="Civil",
    title="민사 | 업무분야 | 법률사무소 올본",
    desc="손해배상·대여금·부동산·건설·계약분쟁·채권추심·보전처분 등 민사 사건. 법률사무소 올본이 증거 구조부터 정리해 대응합니다.",
    kw="민사소송 변호사, 손해배상 변호사, 부동산 소송, 공사대금 소송, 가압류 가처분, 강남 변호사",
    subdesc="다툼의 구조를 먼저 그리고, 자료로 증명합니다.",
    overview=[
        "민사 사건의 승패는 대부분 <b>주장</b>이 아니라 <b>증거</b>에서 갈립니다. 같은 사실관계라도 어떤 자료를 어떤 순서로 제출하느냐에 따라 결론이 달라집니다.",
        "올본은 사건을 맡으면 먼저 계약서·이체내역·문자·현장자료를 시계열로 재구성하고, 상대방이 다툴 지점을 미리 정리합니다. 그다음에 서면을 씁니다.",
        "청구 가능성과 회수 가능성은 다른 문제입니다. 소송에서 이기더라도 집행할 재산이 없으면 의미가 줄어들기 때문에, 착수 전에 <b>보전처분(가압류·가처분)</b>의 필요성부터 함께 검토합니다.",
    ],
    types=[
        ("손해배상", "불법행위·채무불이행"),
        ("대여금 · 약정금", "차용증 없는 사안 포함"),
        ("부동산", "매매·임대차·명도·경계"),
        ("건설 · 공사대금", "기성고·추가공사 분쟁"),
        ("계약 분쟁", "해제·해지·위약금"),
        ("채권추심", "지급명령·강제집행"),
        ("가압류 · 가처분", "보전처분 신청·이의"),
        ("기타 재산분쟁", "부당이득·구상금 등"),
    ],
    points=[
        ("자료부터 구조화합니다", "산더미 같은 자료를 시계열 표와 쟁점별 대비표로 정리합니다. 재판부가 한 번에 이해할 수 있는 형태로 만드는 것이 첫 단계입니다."),
        ("회수까지 함께 봅니다", "판결을 받는 것과 돈을 받는 것은 다릅니다. 상대방 자산 상황을 고려해 보전처분과 집행 방법을 미리 설계합니다."),
        ("조정·화해도 선택지입니다", "끝까지 다투는 것이 늘 최선은 아닙니다. 기간과 비용, 회수 가능성을 계산해 합의가 유리한 지점을 함께 판단합니다."),
    ],
    related="civil",
),

"criminal": dict(
    file="practice-criminal.html",
    label="형사", en="Criminal",
    title="형사 | 업무분야 | 법률사무소 올본",
    desc="수사 초기 대응부터 재판까지. 재산범죄·성범죄·명예훼손은 물론 기술유출·영업비밀 침해, 저작권법·상표법 위반 등 IP 형사사건에 강점이 있습니다.",
    kw="형사 변호사, 영업비밀 유출, 기술유출 변호사, 저작권법 위반 형사, 상표법 위반, 수사 초기대응",
    subdesc="첫 조사 전에 만나야 선택지가 넓습니다.",
    overview=[
        "형사사건에서 가장 중요한 시점은 판결 직전이 아니라 <b>첫 조사</b>입니다. 초기에 남긴 진술이 이후 전체 절차의 틀을 정하기 때문입니다.",
        "올본은 출석 요구를 받은 단계에서부터 사실관계를 정리하고, 진술 범위와 제출 자료를 함께 준비합니다. 필요하면 조사에 동석합니다.",
        "특히 <b>기술유출·영업비밀 침해, 저작권법·상표법 위반</b> 형사사건은 기술과 권리 내용을 정확히 이해해야 다툴 수 있습니다. 변리사 실무와 IP 소송 경험을 형사 대응에 그대로 연결합니다.",
    ],
    types=[
        ("수사 초기 대응", "출석 요구·조사 동석"),
        ("사기 · 횡령 · 배임", "재산범죄 전반"),
        ("성범죄", "수사·재판 대응"),
        ("폭력 · 상해", "합의·양형 자료"),
        ("명예훼손 · 모욕", "온라인 게시물 포함"),
        ("기술유출 · 영업비밀", "부정경쟁방지법 위반"),
        ("저작권법 위반", "소프트웨어·콘텐츠"),
        ("상표법 · 특허법 위반", "위조품·침해 형사"),
    ],
    points=[
        ("IP 형사사건이 강점입니다", "영업비밀의 비공지성·비밀관리성, 저작물의 창작성, 상표의 동일·유사 판단처럼 기술과 권리에 대한 이해가 필요한 쟁점을 직접 분석합니다."),
        ("진술 전략을 먼저 세웁니다", "무엇을 말할지보다 어떤 순서로 어디까지 말할지가 중요합니다. 예상 질문과 자료를 미리 정리해 조사에 들어갑니다."),
        ("민사·형사를 함께 봅니다", "기술유출 사건은 형사 고소와 민사 손해배상, 가처분이 동시에 진행되는 경우가 많습니다. 절차 간 영향을 계산해 순서를 정합니다."),
    ],
    related="criminal",
),

"family": dict(
    file="practice-family.html",
    label="가사", en="Family",
    title="가사 | 업무분야 | 법률사무소 올본",
    desc="이혼(협의·재판), 재산분할, 위자료, 양육권·양육비, 상속, 유류분 등 가사 사건을 자료 중심으로 정리해 대응합니다.",
    kw="이혼 변호사, 재산분할, 양육권 소송, 상속 변호사, 유류분 청구, 강남 이혼 변호사",
    subdesc="감정이 아니라 자료로 정리해 드립니다.",
    overview=[
        "가사 사건은 감정이 앞서기 쉽지만, 법원이 판단하는 것은 결국 <b>구체적인 자료</b>입니다. 기여도, 양육 환경, 재산의 형성 경위가 숫자와 기록으로 설명되어야 합니다.",
        "올본은 혼인 기간의 금융거래·부동산 등기·소득 자료를 정리해 재산 형성 과정을 재구성하고, 주장할 수 있는 범위를 먼저 확인합니다.",
        "자녀가 있는 사건에서는 결과만큼 <b>과정</b>이 중요합니다. 분쟁이 길어질 때의 부담까지 고려해 협의·조정 가능성을 함께 검토합니다.",
    ],
    types=[
        ("협의이혼", "절차 안내·합의서 작성"),
        ("재판상 이혼", "소장·조정·변론"),
        ("재산분할", "기여도 산정·재산 조회"),
        ("위자료", "청구 및 방어"),
        ("양육권 · 친권", "양육환경 소명"),
        ("양육비", "산정·이행 청구"),
        ("상속", "분할협의·상속포기"),
        ("유류분", "반환청구 소송"),
    ],
    points=[
        ("재산을 먼저 특정합니다", "재산명시·금융거래정보 제출명령 등 절차를 활용해 분할 대상을 확정합니다. 대상이 정해져야 기여도 주장이 의미를 갖습니다."),
        ("생활의 기록이 증거입니다", "양육 사건에서는 일상의 기록이 중요한 자료가 됩니다. 어떤 자료를 어떻게 남겨야 하는지 초기에 안내드립니다."),
        ("합의 가능성도 열어둡니다", "조정으로 마무리하는 것이 시간과 비용, 관계 측면에서 나은 경우가 있습니다. 유불리를 계산해 솔직히 말씀드립니다."),
    ],
    related="family",
),

"admin": dict(
    file="practice-admin.html",
    label="행정", en="Administrative",
    title="행정 | 업무분야 | 법률사무소 올본",
    desc="인허가 취소·정지 처분 대응, 영업정지, 행정심판·행정소송, 정보공개청구, 그리고 특허심판원·특허법원 심결취소소송까지 연계 대응합니다.",
    kw="행정소송 변호사, 영업정지 처분, 행정심판, 특허법원 심결취소소송, 정보공개청구",
    subdesc="처분에는 기한이 있습니다. 먼저 날짜부터 확인하세요.",
    overview=[
        "행정 사건에는 <b>제소기간</b>이 있습니다. 처분을 안 날부터 90일, 처분이 있은 날부터 1년이 원칙이므로, 대응 여부를 고민하는 사이에 다툴 기회 자체가 사라질 수 있습니다.",
        "올본은 처분서를 받은 즉시 기한과 불복 경로(행정심판 / 행정소송 / 집행정지)를 확인하고, 영업 지속이 필요한 사안에서는 <b>집행정지 신청</b>을 우선 검토합니다.",
        "특히 특허·상표·디자인 사건에서 특허심판원 심결에 불복하는 <b>심결취소소송</b>은 특허법원 관할의 행정소송입니다. 올본은 IP 실무와 행정소송을 하나의 흐름으로 대응합니다.",
    ],
    types=[
        ("인허가 취소 · 정지", "처분 사전통지 대응"),
        ("영업정지 처분", "집행정지 신청"),
        ("과징금 · 과태료", "감경·취소 주장"),
        ("행정심판", "심판청구 대리"),
        ("행정소송", "취소·무효확인의 소"),
        ("정보공개청구", "청구 및 불복"),
        ("심결취소소송", "특허법원 관할 사건"),
        ("특허심판원 심판", "무효·권리범위확인 등"),
    ],
    points=[
        ("기한 관리가 첫 업무입니다", "처분서 수령일을 기준으로 남은 기간을 계산하고, 집행정지가 필요한지 즉시 판단합니다. 늦으면 되돌릴 수 없는 영역입니다."),
        ("절차 위법도 다툽니다", "처분 사유의 사실오인·재량권 일탈뿐 아니라, 사전통지·의견제출 기회 부여 등 절차적 하자도 함께 검토합니다."),
        ("IP 행정소송과 연결됩니다", "심결취소소송은 기술 이해와 행정소송 절차를 동시에 요구합니다. 변리사 실무 경험이 그대로 활용되는 영역입니다."),
    ],
    related="admin",
),
}


def side_nav(active):
    lis = []
    for key, label, href in NAV:
        cls = ' class="is-active"' if key == active else ""
        lis.append('          <li%s><a href="%s"%s>%s</a></li>' % (
            cls, href, ' aria-current="page"' if key == active else "", label))
    return "\n".join(lis)


TPL = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="keywords" content="{kw}">
<link rel="canonical" href="https://www.olbonlaw.com/{file}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="법률사무소 올본">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="https://www.olbonlaw.com/{file}">
<meta property="og:image" content="https://www.olbonlaw.com/assets/images/og-image.jpg">
<meta property="og:locale" content="ko_KR">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="assets/images/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="https://unpkg.com/aos@2.3.4/dist/aos.css">
<link rel="stylesheet" href="assets/css/common.css">
<link rel="stylesheet" href="assets/css/sub.css">
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "LegalService",
  "name": "법률사무소 올본",
  "url": "https://www.olbonlaw.com/{file}",
  "telephone": "+82-10-7612-3038",
  "email": "jhkim@olbonlaw.com",
  "address": {{
    "@type": "PostalAddress",
    "streetAddress": "테헤란로 138 성홍타워 4층",
    "addressLocality": "강남구",
    "addressRegion": "서울특별시",
    "addressCountry": "KR"
  }},
  "hasOfferCatalog": {{
    "@type": "OfferCatalog",
    "name": "{label} 업무",
    "itemListElement": [{offer_items}]
  }}
}}
</script>
</head>

<body data-page="practice" class="is-sub">
<div id="header"></div>

<main id="main">

  <section class="subvisual">
    <div class="subvisual__inner">
      <p class="subvisual__en">{en}</p>
      <h2 class="subvisual__title">{label}</h2>
      <p class="subvisual__desc">{subdesc}</p>
    </div>
  </section>

  <nav class="breadcrumb" aria-label="현재 위치">
    <div class="container">
      <ol>
        <li><a href="index.html"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3 2.5 11h2.7v9h5.1v-5.4h3.4V20h5.1v-9h2.7L12 3Z"/></svg><span class="blind">홈</span></a></li>
        <li>업무분야</li>
        <li aria-current="page">{label}</li>
      </ol>
    </div>
  </nav>

  <div class="sub-body">
    <div class="container">
      <div class="pract-layout">

        <!-- 좌측 사이드 메뉴 -->
        <aside class="pract-side">
          <h2 class="pract-side__title"><span>PRACTICE AREAS</span>업무분야</h2>
          <ul class="pract-side__list">
{side}
          </ul>
          <div class="pract-side__cta">
            <p>{label} 사건 상담</p>
            <a href="tel:010-7612-3038" class="tel">010-7612-3038</a>
            <a href="consult.html#consult-form" class="btn btn--navy btn--block btn--sm">온라인 상담 신청</a>
          </div>
        </aside>

        <!-- 본문 -->
        <div>

          <!-- 1. 분야 개요 -->
          <section class="blk" style="margin-top:0" aria-labelledby="ovTitle">
            <div class="blk__head" data-aos="fade-up">
              <p class="blk__num">01. OVERVIEW</p>
              <h2 class="blk__title" id="ovTitle">분야 개요</h2>
            </div>
            <div class="field-intro" data-aos="fade-up">
              <div>
{overview}
              </div>
              <div class="field-intro__visual">
                <!-- ★ 이미지 교체 위치: <img src="assets/images/practice-{key}.jpg" alt="{label} 업무 이미지" loading="lazy"> -->
                <div class="ph" aria-hidden="true">이미지 영역<br>(practice-{key}.jpg)</div>
              </div>
            </div>
          </section>

          <!-- 2. 주요 취급 사건 유형 -->
          <section class="blk" aria-labelledby="typeTitle">
            <div class="blk__head" data-aos="fade-up">
              <p class="blk__num">02. CASE TYPES</p>
              <h2 class="blk__title" id="typeTitle">주요 취급 사건 유형</h2>
            </div>
            <ul class="type-grid" data-aos="fade-up">
{types}
            </ul>
          </section>

          <!-- 3. 올본의 접근 방식 -->
          <section class="blk" aria-labelledby="pointTitle">
            <div class="blk__head" data-aos="fade-up">
              <p class="blk__num">03. APPROACH</p>
              <h2 class="blk__title" id="pointTitle">올본의 접근 방식</h2>
            </div>
            <div class="point-grid">
{points}
            </div>
          </section>

          <!-- 4. 관련 성공사례 + CTA -->
          <section class="blk" aria-labelledby="caseTitle">
            <div class="blk__head" data-aos="fade-up">
              <p class="blk__num">04. CASE STUDIES</p>
              <h2 class="blk__title" id="caseTitle">관련 성공사례</h2>
            </div>
            <p class="blk__lead" data-aos="fade-up">{label} 분야에서 진행한 사례를 비실명으로 정리해 두었습니다.</p>
            <p style="margin-top:20px" data-aos="fade-up">
              <a href="cases.html#{related}" class="btn btn--line">{label} 성공사례 보기</a>
            </p>

            <div class="cta-banner" data-aos="fade-up">
              <div>
                <h2 class="cta-banner__title">{label} 사건, 혼자 판단하지 마세요.</h2>
                <p class="cta-banner__desc">가능성과 위험을 있는 그대로 말씀드립니다. 상담은 사전 예약제로 운영됩니다.</p>
              </div>
              <div class="cta-banner__btns">
                <a href="tel:010-7612-3038" class="btn btn--gold btn--lg">010-7612-3038</a>
                <a href="consult.html#consult-form" class="btn btn--line-white btn--lg">온라인 상담 신청</a>
              </div>
            </div>
          </section>

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

for key, d in PAGES.items():
    overview = "\n".join('                <p class="blk__lead">%s</p>' % t for t in d["overview"])
    types = "\n".join(
        '              <li class="type-item">%s<span>%s<br><small style="font-weight:400;color:var(--gray-text);font-size:13px">%s</small></span></li>'
        % (icon(i), t[0], t[1]) for i, t in enumerate(d["types"]))
    points = "\n".join(
        '              <div class="point-item" data-aos="fade-up"%s><span class="point-item__no">%02d</span><h4>%s</h4><p>%s</p></div>'
        % ((' data-aos-delay="%d"' % (i * 80)) if i else "", i + 1, p[0], p[1])
        for i, p in enumerate(d["points"]))
    offers = ",".join(
        '{ "@type": "Offer", "itemOffered": { "@type": "Service", "name": "%s" } }' % t[0]
        for t in d["types"])

    html = TPL.format(
        title=d["title"], desc=d["desc"], kw=d["kw"], file=d["file"], label=d["label"],
        en=d["en"], subdesc=d["subdesc"], side=side_nav(key), overview=overview,
        types=types, points=points, key=key, related=d["related"], offer_items=offers)

    out = os.path.join(ROOT, d["file"])
    with io.open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print("created:", d["file"])
