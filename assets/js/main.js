/* ==========================================================================
   법률사무소 올본 — main.js (메인 페이지 전용)
   히어로 슬라이더 / 성공사례 슬라이더 (Swiper.js)
   ※ Swiper CDN 로드 실패 시에도 첫 슬라이드가 정상 노출되도록 폴백 처리
   ========================================================================== */
(function () {
  "use strict";

  if (typeof Swiper === "undefined") {
    // CDN 차단·오프라인 환경 폴백: 슬라이드를 세로로 펼쳐 표시
    var hero = document.querySelector(".hero .swiper");
    if (hero) {
      var first = hero.querySelector(".swiper-slide");
      if (first) first.classList.add("swiper-slide-active");
      Array.prototype.slice.call(hero.querySelectorAll(".swiper-slide")).slice(1).forEach(function (s) {
        s.style.display = "none";
      });
      hero.querySelector(".swiper-wrapper").style.display = "block";
    }
    var caseWrap = document.querySelector(".cases .swiper-wrapper");
    if (caseWrap) {
      caseWrap.style.display = "grid";
      caseWrap.style.gridTemplateColumns = "repeat(auto-fit, minmax(280px, 1fr))";
      caseWrap.style.gap = "24px";
    }
    return;
  }

  /* ----------------------------- 히어로 ----------------------------- */
  var totalEl = document.querySelector("[data-hero-total]");
  var curEl = document.querySelector("[data-hero-current]");
  var barEl = document.querySelector("[data-hero-bar]");

  var heroSwiper = new Swiper(".hero .swiper", {
    loop: true,
    speed: 900,
    effect: "fade",
    fadeEffect: { crossFade: true },
    autoplay: { delay: 5500, disableOnInteraction: false },
    a11y: {
      prevSlideMessage: "이전 슬라이드",
      nextSlideMessage: "다음 슬라이드",
      containerMessage: "메인 비주얼 슬라이드"
    },
    navigation: { prevEl: ".hero__prev", nextEl: ".hero__next" },
    on: {
      init: updatePaging,
      slideChange: updatePaging
    }
  });

  function updatePaging(sw) {
    var s = sw || heroSwiper;
    if (!s) return;
    var total = s.slides.length - (s.loopedSlides ? s.loopedSlides * 2 : 0);
    total = s.params.loop ? document.querySelectorAll(".hero__slide").length : s.slides.length;
    var cur = (s.realIndex || 0) + 1;
    if (curEl) curEl.textContent = String(cur).padStart(2, "0");
    if (totalEl) totalEl.textContent = String(total).padStart(2, "0");
    if (barEl) barEl.style.width = (cur / total) * 100 + "%";
  }

  // 자동재생 일시정지 (접근성: 마우스 오버 / 포커스 시)
  var heroEl = document.querySelector(".hero");
  if (heroEl && heroSwiper.autoplay) {
    heroEl.addEventListener("mouseenter", function () { heroSwiper.autoplay.stop(); });
    heroEl.addEventListener("mouseleave", function () { heroSwiper.autoplay.start(); });
    heroEl.addEventListener("focusin", function () { heroSwiper.autoplay.stop(); });
  }

  /* --------------------------- 성공사례 ---------------------------- */
  if (document.querySelector(".cases .swiper")) {
    new Swiper(".cases .swiper", {
      slidesPerView: 1,
      spaceBetween: 20,
      speed: 600,
      a11y: { containerMessage: "성공사례 슬라이드" },
      navigation: { prevEl: ".cases__prev", nextEl: ".cases__next" },
      breakpoints: {
        768: { slidesPerView: 2, spaceBetween: 22 },
        1025: { slidesPerView: 3, spaceBetween: 24 }
      }
    });
  }
})();
