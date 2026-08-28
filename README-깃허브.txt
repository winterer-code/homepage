법률사무소 올본 — GitHub Pages 업로드용
=====================================================

[올리는 법]
이 폴더 안의 '내용물 전부'를 저장소(homepage) 루트에 올리세요.
이 폴더 자체를 올리면 주소에 폴더 한 겹이 더 생깁니다.

[꼭 남겨두어야 할 기존 파일 2개]
  CNAME                        ← 도메인 연결 정보 (olbonlaw.com). 절대 지우지 마세요
  naver8...html                ← 네이버 소유확인 파일. 지우면 인증이 풀립니다

[기준 주소]
  https://olbonlaw.com   (www 없음)
  canonical / og:url / sitemap.xml 이 모두 이 주소로 맞춰져 있습니다.

[아파치(가비아) 버전과 다른 점]
  .htaccess     → GitHub Pages 는 Apache 가 아니라 동작하지 않습니다. 제외했습니다.
                  https 강제는 저장소 Settings > Pages > "Enforce HTTPS" 체크로 대신합니다.
  send.php      → PHP 가 실행되지 않으므로 제외했습니다.
                  (상담은 전화·카카오톡·이메일 버튼으로 받습니다)
  .nojekyll     → 새로 추가. GitHub 이 Jekyll 로 파일을 건드리지 않게 합니다.
                  빈 파일이지만 반드시 함께 올려주세요.
  404.html      → 새로 추가. 없는 주소로 들어왔을 때 보이는 안내 페이지입니다.

[올린 뒤 확인]
  1) Settings > Pages > Custom domain 에 olbonlaw.com 이 들어가 있고 초록 체크가 뜨는지
  2) "Enforce HTTPS" 체크
  3) https://olbonlaw.com 접속 후 Ctrl+F5 (맥은 Cmd+Shift+R)
