/* ==========================================================================
   법률사무소 올본 — common.js
   sticky 헤더 / 모바일 메뉴 / TOP / AOS / 상담폼 검증 / 아코디언 / 탭 / 필터
   ※ layout.js 다음에 로드하세요.
   ========================================================================== */
(function () {
  "use strict";

  var body = document.body;
  var isSub = body.classList.contains("is-sub");

  /* ------------------------------------------------------------------
     1. Sticky header — 메인은 투명→흰색, 서브는 항상 흰색
     ------------------------------------------------------------------ */
  var header = document.getElementById("siteHeader");
  if (header) {
    if (isSub) {
      header.classList.add("is-solid");
    } else {
      var onScroll = function () {
        if (window.scrollY > 40) header.classList.add("is-solid");
        else header.classList.remove("is-solid");
      };
      onScroll();
      window.addEventListener("scroll", onScroll, { passive: true });
    }
    // 데스크톱 드롭다운이 열리면 헤더 배경 유지
    header.addEventListener("mouseover", function (e) {
      if (e.target.closest(".gnb__item")) header.classList.add("is-solid");
    });
    header.addEventListener("mouseleave", function () {
      if (!isSub && window.scrollY <= 40) header.classList.remove("is-solid");
    });
  }

  /* ------------------------------------------------------------------
     2. 모바일 전체화면 내비게이션
     ------------------------------------------------------------------ */
  var toggle = document.getElementById("navToggle");
  var mnav = document.getElementById("mobileNav");
  var navClose = document.getElementById("navClose");

  function openNav() {
    if (!mnav) return;
    mnav.classList.add("is-active");
    body.classList.add("is-locked");
    if (toggle) { toggle.setAttribute("aria-expanded", "true"); toggle.setAttribute("aria-label", "전체 메뉴 닫기"); }
    var first = mnav.querySelector("a, button");
    if (first) first.focus();
  }
  function closeNav() {
    if (!mnav) return;
    mnav.classList.remove("is-active");
    body.classList.remove("is-locked");
    if (toggle) {
      toggle.setAttribute("aria-expanded", "false");
      toggle.setAttribute("aria-label", "전체 메뉴 열기");
      toggle.focus();
    }
  }
  if (toggle) toggle.addEventListener("click", openNav);
  if (navClose) navClose.addEventListener("click", closeNav);
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && mnav && mnav.classList.contains("is-active")) closeNav();
  });

  // 모바일 2depth 토글 (아코디언)
  if (mnav) {
    mnav.addEventListener("click", function (e) {
      var btn = e.target.closest("button.mnav__link");
      if (!btn) return;
      var item = btn.parentElement;
      var open = item.classList.toggle("is-open");
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  // 데스크톱 폭으로 돌아가면 메뉴 자동 닫기
  var mq = window.matchMedia("(min-width: 1025px)");
  (mq.addEventListener ? mq.addEventListener.bind(mq, "change") : mq.addListener.bind(mq))(function (ev) {
    if ((ev.matches !== undefined ? ev.matches : mq.matches) && mnav && mnav.classList.contains("is-active")) closeNav();
  });

  /* ------------------------------------------------------------------
     3. TOP 버튼
     ------------------------------------------------------------------ */
  document.addEventListener("click", function (e) {
    var btn = e.target.closest("[data-scroll-top]");
    if (!btn) return;
    window.scrollTo({ top: 0, behavior: "smooth" });
  });

  /* ------------------------------------------------------------------
     4. AOS (스크롤 페이드업) — CDN 로드 실패 시에도 콘텐츠가 보이도록 처리
     ------------------------------------------------------------------ */
  if (window.AOS) {
    AOS.init({ duration: 600, easing: "ease-out", once: true, offset: 60, disable: "phone" });
  } else {
    Array.prototype.forEach.call(document.querySelectorAll("[data-aos]"), function (el) {
      el.removeAttribute("data-aos");
    });
  }

  /* ------------------------------------------------------------------
     5. 아코디언 (FAQ 등)  —  [data-accordion] > .acc__item > button.acc__q
     ------------------------------------------------------------------ */
  Array.prototype.forEach.call(document.querySelectorAll("[data-accordion]"), function (root) {
    root.addEventListener("click", function (e) {
      var q = e.target.closest(".acc__q");
      if (!q || !root.contains(q)) return;
      var item = q.closest(".acc__item");
      var isOpen = item.classList.contains("is-open");
      if (root.hasAttribute("data-accordion-single")) {
        Array.prototype.forEach.call(root.querySelectorAll(".acc__item"), function (it) {
          it.classList.remove("is-open");
          var b = it.querySelector(".acc__q");
          if (b) b.setAttribute("aria-expanded", "false");
        });
      }
      if (!isOpen) { item.classList.add("is-open"); q.setAttribute("aria-expanded", "true"); }
      else { item.classList.remove("is-open"); q.setAttribute("aria-expanded", "false"); }
    });
  });

  /* ------------------------------------------------------------------
     6. 탭 (지식재산권 특허/상표/디자인/저작권 등)
        [data-tabs] 안의 button[data-tab-target] ↔ [data-tab-panel]
     ------------------------------------------------------------------ */
  Array.prototype.forEach.call(document.querySelectorAll("[data-tabs]"), function (root) {
    var btns = root.querySelectorAll("[data-tab-target]");
    var panels = root.querySelectorAll("[data-tab-panel]");
    function activate(name, focus) {
      Array.prototype.forEach.call(btns, function (b) {
        var on = b.getAttribute("data-tab-target") === name;
        b.classList.toggle("is-active", on);
        b.setAttribute("aria-selected", on ? "true" : "false");
        b.setAttribute("tabindex", on ? "0" : "-1");
        if (on && focus) b.focus();
      });
      Array.prototype.forEach.call(panels, function (p) {
        p.hidden = p.getAttribute("data-tab-panel") !== name;
      });
    }
    Array.prototype.forEach.call(btns, function (b, i) {
      b.addEventListener("click", function () { activate(b.getAttribute("data-tab-target")); });
      b.addEventListener("keydown", function (e) {
        var idx = null;
        if (e.key === "ArrowRight") idx = (i + 1) % btns.length;
        if (e.key === "ArrowLeft") idx = (i - 1 + btns.length) % btns.length;
        if (idx !== null) { e.preventDefault(); activate(btns[idx].getAttribute("data-tab-target"), true); }
      });
    });
    // 해시로 진입 시 해당 탭 활성화
    var hash = location.hash.replace("#", "");
    var match = hash && root.querySelector('[data-tab-target="' + hash + '"]');
    activate(match ? hash : btns[0] && btns[0].getAttribute("data-tab-target"));
  });

  /* ------------------------------------------------------------------
     7. 성공사례 분야 필터 + 페이지네이션
     ------------------------------------------------------------------ */
  var caseRoot = document.querySelector("[data-case-list]");
  if (caseRoot) {
    var PER_PAGE = 6;
    var filterBtns = document.querySelectorAll("[data-case-filter]");
    var pager = document.querySelector("[data-case-pager]");
    var emptyMsg = document.querySelector("[data-case-empty]");
    var state = { cat: "all", page: 1 };

    function items() { return Array.prototype.slice.call(caseRoot.querySelectorAll(".case-card")); }
    function filtered() {
      return items().filter(function (el) {
        return state.cat === "all" || el.getAttribute("data-cat") === state.cat;
      });
    }
    function render() {
      var list = filtered();
      var total = Math.max(1, Math.ceil(list.length / PER_PAGE));
      if (state.page > total) state.page = total;
      items().forEach(function (el) { el.hidden = true; });
      list.slice((state.page - 1) * PER_PAGE, state.page * PER_PAGE).forEach(function (el) { el.hidden = false; });
      if (emptyMsg) emptyMsg.hidden = list.length !== 0;

      if (pager) {
        var html = "";
        html += '<button type="button" class="pager__nav" data-go="prev"' + (state.page === 1 ? " disabled" : "") + ' aria-label="이전 페이지">‹</button>';
        for (var i = 1; i <= total; i++) {
          html += '<button type="button" class="pager__num' + (i === state.page ? " is-active" : "") + '" data-go="' + i + '"' +
            (i === state.page ? ' aria-current="page"' : "") + ">" + i + "</button>";
        }
        html += '<button type="button" class="pager__nav" data-go="next"' + (state.page === total ? " disabled" : "") + ' aria-label="다음 페이지">›</button>';
        pager.innerHTML = html;
        pager.hidden = list.length <= PER_PAGE;
      }
    }
    Array.prototype.forEach.call(filterBtns, function (b) {
      b.addEventListener("click", function () {
        Array.prototype.forEach.call(filterBtns, function (x) { x.classList.remove("is-active"); x.setAttribute("aria-pressed", "false"); });
        b.classList.add("is-active"); b.setAttribute("aria-pressed", "true");
        state.cat = b.getAttribute("data-case-filter");
        state.page = 1;
        render();
      });
    });
    if (pager) {
      pager.addEventListener("click", function (e) {
        var b = e.target.closest("[data-go]");
        if (!b || b.disabled) return;
        var go = b.getAttribute("data-go");
        var total = Math.max(1, Math.ceil(filtered().length / PER_PAGE));
        if (go === "prev") state.page = Math.max(1, state.page - 1);
        else if (go === "next") state.page = Math.min(total, state.page + 1);
        else state.page = parseInt(go, 10);
        render();
        caseRoot.scrollIntoView({ behavior: "smooth", block: "start" });
      });
    }
    // 해시로 분야 진입 (예: cases.html#ip)
    var h = location.hash.replace("#", "");
    var fb = h && document.querySelector('[data-case-filter="' + h + '"]');
    if (fb) fb.click(); else render();
  }

  /* ------------------------------------------------------------------
     8. 온라인 상담 폼 — 유효성 검사 + 실제 전송
        · 기본 전송 경로 : 같은 폴더의 send.php  (PHP 지원 호스팅이면 그대로 동작)
        · 다른 방식으로 바꾸려면 아래 CONSULT.endpoint 한 줄만 고치면 됩니다.
            예) 외부 폼 서비스 : "https://formspree.io/f/XXXXXXX"
                자체 API      : "/api/consult"
        · 전송에 실패하거나 endpoint 가 없으면, 입력하신 내용을 그대로 담은
          메일 작성 창을 띄워 드립니다. 어떤 경우에도 내용이 사라지지 않습니다.
     ------------------------------------------------------------------ */
  var CONSULT = {
    endpoint: "send.php",
    email: (window.OLBON_SITE && window.OLBON_SITE.email) || "jhkim@olbonlaw.com",
    tel: (window.OLBON_SITE && window.OLBON_SITE.tel) || "010-7612-3038"
  };

  var FIELD_LABEL = {
    ip: "지식재산권", civil: "민사", criminal: "형사",
    family: "가사", admin: "행정", etc: "기타"
  };

  Array.prototype.forEach.call(document.querySelectorAll("form[data-consult-form]"), function (form) {
    var submitBtn = form.querySelector('button[type="submit"]');
    var doneBox = form.querySelector("[data-form-done]");
    var failBox = form.querySelector("[data-form-fail]");
    var mailLink = form.querySelector("[data-mail-link]");

    function setError(field, msg) {
      var box = field.closest(".form-row");
      if (!box) return;
      var err = box.querySelector(".form-error");
      if (msg) {
        field.classList.add("is-error");
        field.setAttribute("aria-invalid", "true");
        if (err) { err.textContent = msg; err.classList.add("is-visible"); }
      } else {
        field.classList.remove("is-error");
        field.removeAttribute("aria-invalid");
        if (err) { err.textContent = ""; err.classList.remove("is-visible"); }
      }
    }

    var telPattern = /^0\d{1,2}-?\d{3,4}-?\d{4}$/;
    var mailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

    // 연락처 자동 하이픈
    var telField = form.querySelector('input[name="phone"]');
    if (telField) {
      telField.addEventListener("input", function () {
        var v = telField.value.replace(/[^0-9]/g, "").slice(0, 11);
        if (v.length > 7) telField.value = v.replace(/(\d{2,3})(\d{3,4})(\d{4})/, "$1-$2-$3");
        else if (v.length > 3) telField.value = v.replace(/(\d{2,3})(\d+)/, "$1-$2");
        else telField.value = v;
      });
    }

    function collect() {
      var g = function (n) {
        var el = form.querySelector('[name="' + n + '"]');
        return el ? el.value.trim() : "";
      };
      var agreeEl = form.querySelector('input[name="agree"]');
      return {
        name: g("name"), phone: g("phone"), email: g("email"),
        field: g("field"), message: g("message"),
        website: g("website"),                       /* 허니팟 */
        agree: agreeEl && agreeEl.checked ? "1" : ""
      };
    }

    function mailtoUrl(d) {
      var label = FIELD_LABEL[d.field] || d.field;
      var subject = "[상담신청] " + label + " · " + d.name;
      var body =
        "성함 : " + d.name + "\n" +
        "연락처 : " + d.phone + "\n" +
        "이메일 : " + (d.email || "(미입력)") + "\n" +
        "상담 분야 : " + label + "\n" +
        "----------------------------------------\n" +
        d.message + "\n" +
        "----------------------------------------\n" +
        "(홈페이지 상담 신청 양식에서 작성)";
      return "mailto:" + CONSULT.email +
             "?subject=" + encodeURIComponent(subject) +
             "&body=" + encodeURIComponent(body);
    }

    function showDone() {
      if (failBox) failBox.hidden = true;
      form.reset();
      if (doneBox) {
        doneBox.hidden = false;
        doneBox.setAttribute("tabindex", "-1");
        doneBox.scrollIntoView({ behavior: "smooth", block: "center" });
        doneBox.focus();
      } else {
        alert("상담 신청이 접수되었습니다. 순차적으로 연락드리겠습니다.");
      }
    }

    function showFail(d, reason) {
      if (doneBox) doneBox.hidden = true;
      if (!failBox) { window.location.href = mailtoUrl(d); return; }
      if (mailLink) mailLink.setAttribute("href", mailtoUrl(d));
      var p = failBox.querySelector("p");
      if (p && reason) {
        p.innerHTML = "<b>" + reason + "</b><br>아래 방법으로 보내주시면 동일하게 접수됩니다. " +
                      "입력하신 내용은 그대로 담겨 있습니다.";
      }
      failBox.hidden = false;
      failBox.setAttribute("tabindex", "-1");
      failBox.scrollIntoView({ behavior: "smooth", block: "center" });
      failBox.focus();
    }

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var ok = true, firstBad = null;

      var name = form.querySelector('input[name="name"]');
      var phone = form.querySelector('input[name="phone"]');
      var email = form.querySelector('input[name="email"]');
      var field = form.querySelector('select[name="field"]');
      var message = form.querySelector('textarea[name="message"]');
      var agree = form.querySelector('input[name="agree"]');

      if (name) {
        if (!name.value.trim()) { setError(name, "이름을 입력해 주세요."); ok = false; firstBad = firstBad || name; }
        else setError(name, "");
      }
      if (phone) {
        var pv = phone.value.trim();
        if (!pv) { setError(phone, "연락처를 입력해 주세요."); ok = false; firstBad = firstBad || phone; }
        else if (!telPattern.test(pv)) { setError(phone, "연락처 형식을 확인해 주세요. (예: 010-1234-5678)"); ok = false; firstBad = firstBad || phone; }
        else setError(phone, "");
      }
      if (email) {
        var ev = email.value.trim();
        if (ev && !mailPattern.test(ev)) { setError(email, "이메일 형식을 확인해 주세요."); ok = false; firstBad = firstBad || email; }
        else setError(email, "");
      }
      if (field) {
        if (!field.value) { setError(field, "상담 분야를 선택해 주세요."); ok = false; firstBad = firstBad || field; }
        else setError(field, "");
      }
      if (message) {
        if (message.value.trim().length < 10) { setError(message, "상담 내용을 10자 이상 입력해 주세요."); ok = false; firstBad = firstBad || message; }
        else setError(message, "");
      }
      if (agree) {
        if (!agree.checked) { setError(agree, "개인정보 수집·이용에 동의해 주세요."); ok = false; firstBad = firstBad || agree; }
        else setError(agree, "");
      }

      if (!ok) { if (firstBad) firstBad.focus(); return; }

      var data = collect();

      /* 파일(file://)로 직접 열어 본 경우에는 서버가 없어 전송할 수 없습니다. */
      if (location.protocol === "file:") {
        showFail(data, "미리보기 파일에서는 자동 전송이 되지 않습니다.");
        return;
      }
      if (!CONSULT.endpoint) {
        showFail(data, "전송 경로가 설정되어 있지 않습니다.");
        return;
      }

      var label = submitBtn ? submitBtn.textContent : "";
      if (submitBtn) { submitBtn.disabled = true; submitBtn.textContent = "전송 중…"; }

      var done = function () {
        if (submitBtn) { submitBtn.disabled = false; submitBtn.textContent = label; }
      };

      fetch(CONSULT.endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
      })
        .then(function (r) {
          return r.json().catch(function () { return { ok: r.ok }; })
            .then(function (json) { return { status: r.status, json: json }; });
        })
        .then(function (res) {
          if (res.json && res.json.ok) { done(); showDone(); return; }
          done();
          showFail(data, (res.json && res.json.error) || "전송에 실패했습니다.");
        })
        .catch(function () {
          done();
          showFail(data, "서버와 연결하지 못했습니다.");
        });
    });
  });

  /* ------------------------------------------------------------------
     9. 헤더 높이만큼 앵커 이동 보정
     ------------------------------------------------------------------ */
  document.addEventListener("click", function (e) {
    var a = e.target.closest('a[href^="#"]:not([href="#"])');
    if (!a) return;
    var target = document.querySelector(a.getAttribute("href"));
    if (!target) return;
    e.preventDefault();
    var offset = (header ? header.offsetHeight : 70) + 12;
    var top = target.getBoundingClientRect().top + window.scrollY - offset;
    window.scrollTo({ top: top, behavior: "smooth" });
    if (mnav && mnav.classList.contains("is-active")) closeNav();
  });

  // 다른 페이지에서 해시로 진입한 경우 보정
  window.addEventListener("load", function () {
    if (!location.hash) return;
    var t = document.querySelector(location.hash);
    if (!t) return;
    setTimeout(function () {
      var offset = (header ? header.offsetHeight : 70) + 12;
      window.scrollTo({ top: t.getBoundingClientRect().top + window.scrollY - offset });
    }, 120);
  });

  /* ------------------------------------------------------------------
     10. 전화 걸기 / 주소 복사 / 지도 로드 실패 대응
     ------------------------------------------------------------------ */
  var toastEl = null, toastTimer = null;
  function showToast(html, ms) {
    if (!toastEl) {
      toastEl = document.createElement("div");
      toastEl.className = "toast";
      toastEl.setAttribute("role", "status");
      document.body.appendChild(toastEl);
    }
    toastEl.innerHTML = html;
    toastEl.classList.add("is-on");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toastEl.classList.remove("is-on"); }, ms || 5000);
  }

  function copyText(text) {
    var ok = false;
    try {
      var ta = document.createElement("textarea");
      ta.value = text;
      ta.setAttribute("readonly", "");
      ta.style.position = "fixed";
      ta.style.top = "-1000px";
      document.body.appendChild(ta);
      ta.select();
      ta.setSelectionRange(0, text.length);
      ok = document.execCommand("copy");
      document.body.removeChild(ta);
    } catch (e) { ok = false; }
    if (!ok && navigator.clipboard) {
      try { navigator.clipboard.writeText(text); ok = true; } catch (e2) {}
    }
    return ok;
  }

  /* 주소·번호 복사 버튼 */
  document.addEventListener("click", function (e) {
    var b = e.target.closest("[data-copy]");
    if (!b) return;
    var t = b.getAttribute("data-copy");
    showToast(copyText(t) ? "복사했습니다 · <b>" + t + "</b>" : "<b>" + t + "</b>", 3500);
  });

  /* 전화 링크
     통화 앱이 열리지 않는 환경(PC 브라우저, 휴대폰의 파일 미리보기 등)에서는
     번호를 띄워 직접 걸거나 복사할 수 있게 안내합니다. */
  document.addEventListener("click", function (e) {
    var a = e.target.closest("a[data-tel]");
    if (!a) return;
    var num = a.getAttribute("data-tel");
    var left = false;
    var mark = function () { left = true; };
    window.addEventListener("pagehide", mark);
    window.addEventListener("blur", mark);
    document.addEventListener("visibilitychange", mark);
    setTimeout(function () {
      window.removeEventListener("pagehide", mark);
      window.removeEventListener("blur", mark);
      document.removeEventListener("visibilitychange", mark);
      if (left || document.hidden) return;   /* 통화 앱으로 잘 넘어감 */
      showToast('<span>통화 앱이 열리지 않으면 직접 걸어 주세요</span><b>' + num +
                '</b><button type="button" data-copy="' + num + '">번호 복사</button>', 8000);
    }, 900);
  });

  /* 지도 iframe 이 차단되거나 실패하면 대체 화면 표시 */
  Array.prototype.forEach.call(document.querySelectorAll("[data-map]"), function (box) {
    var frame = box.querySelector("iframe");
    var fb = box.querySelector(".map__fallback");
    if (!frame || !fb) return;
    var loaded = false;
    frame.addEventListener("load", function () { loaded = true; });
    setTimeout(function () { if (!loaded) fb.hidden = false; }, 6000);
  });

})();
