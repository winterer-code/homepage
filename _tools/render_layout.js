/* layout.js 를 브라우저 없이 실행해 페이지별 헤더·푸터 HTML을 만들어 JSON으로 출력합니다.
   사용: node _tools/render_layout.js home about cases ...  (data-page 값 목록)
   _tools/build_layout.py 가 호출합니다. */
const fs = require("fs");
const path = require("path");
const vm = require("vm");
const src = fs.readFileSync(path.join(__dirname, "..", "assets", "js", "layout.js"), "utf8");
const out = {};
for (const key of process.argv.slice(2)) {
  const pageKey = key === "_" ? "" : key;
  const captured = {};
  const stub = (id) => ({ set outerHTML(v) { captured[id] = v; } });
  const document = {
    body: { getAttribute: () => pageKey },
    getElementById: (id) => (id === "header" || id === "footer" ? stub(id) : null),
    querySelector: () => null
  };
  vm.runInNewContext(src, { document, window: {}, Date, encodeURIComponent });
  out[key] = captured;
}
process.stdout.write(JSON.stringify(out));
