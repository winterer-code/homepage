<?php
/* ==========================================================================
   법률사무소 올본 — 온라인 상담 신청 접수 (PHP)
   --------------------------------------------------------------------------
   홈페이지의 상담 폼에서 보낸 내용을 아래 RECEIVER 주소로 메일 발송합니다.
   PHP를 지원하는 웹호스팅(카페24·가비아·닷홈 등)이면 이 파일을 index.html 과
   같은 위치에 올리기만 하면 바로 동작합니다.

   ※ 별도 회원가입이나 외부 서비스가 필요 없고, 상담 내용이 제3자 서버를
     거치지 않습니다. 변호사 비밀유지 측면에서 이 방식을 권장합니다.
   ========================================================================== */

/* ── 1. 설정 ────────────────────────────────────────────────────────────── */

// 상담 신청을 받을 메일 주소 (쉼표로 여러 개 지정 가능)
$RECEIVER   = 'jhkim@olbonlaw.com';

// 보내는 사람 주소 — 반드시 '내 도메인' 주소를 쓰세요.
// 네이버·지메일 주소를 넣으면 스팸으로 분류되거나 발송이 거부됩니다.
$FROM_EMAIL = 'noreply@olbonlaw.com';
$FROM_NAME  = '올본 홈페이지';

// 접수 내역을 서버에 파일로도 남기려면 true (개인정보이므로 기본은 false)
$SAVE_LOG   = false;
$LOG_FILE   = __DIR__ . '/consult-log.txt';   // 반드시 웹에서 접근 못 하게 보호할 것

/* ── 2. 요청 처리 ───────────────────────────────────────────────────────── */

header('Content-Type: application/json; charset=UTF-8');
header('X-Content-Type-Options: nosniff');

function out($ok, $msg = '', $code = 200) {
    http_response_code($code);
    echo json_encode(['ok' => $ok, 'error' => $msg], JSON_UNESCAPED_UNICODE);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    out(false, '잘못된 접근입니다.', 405);
}

// JSON / 일반 폼 전송 모두 지원
$raw  = file_get_contents('php://input');
$data = json_decode($raw, true);
if (!is_array($data)) { $data = $_POST; }

$get = function ($k) use ($data) {
    return isset($data[$k]) ? trim((string)$data[$k]) : '';
};

// 스팸 봇 차단 (사람에게는 보이지 않는 필드)
if ($get('website') !== '') { out(true); }

$name    = $get('name');
$phone   = $get('phone');
$email   = $get('email');
$field   = $get('field');
$message = $get('message');
$agree   = $get('agree');

/* ── 3. 서버측 검증 (브라우저 검증을 우회한 요청 대비) ──────────────────── */

$FIELDS = [
    'ip' => '지식재산권', 'civil' => '민사', 'criminal' => '형사',
    'family' => '가사', 'admin' => '행정', 'etc' => '기타',
];

if ($name === '' || mb_strlen($name) > 40)                       out(false, '이름을 확인해 주세요.', 400);
if (!preg_match('/^0\d{1,2}-?\d{3,4}-?\d{4}$/', $phone))         out(false, '연락처 형식을 확인해 주세요.', 400);
if ($email !== '' && !filter_var($email, FILTER_VALIDATE_EMAIL)) out(false, '이메일 형식을 확인해 주세요.', 400);
if (!isset($FIELDS[$field]))                                     out(false, '상담 분야를 선택해 주세요.', 400);
if (mb_strlen($message) < 10 || mb_strlen($message) > 5000)      out(false, '상담 내용을 10자 이상 입력해 주세요.', 400);
if ($agree !== '1' && $agree !== 'true' && $agree !== 'on')       out(false, '개인정보 수집·이용 동의가 필요합니다.', 400);

// 헤더 인젝션 방지
foreach ([$name, $phone, $email] as $v) {
    if (preg_match('/[\r\n]/', $v)) out(false, '허용되지 않는 문자가 포함되어 있습니다.', 400);
}

/* ── 4. 메일 작성 ───────────────────────────────────────────────────────── */

$fieldName = $FIELDS[$field];
$when      = date('Y-m-d H:i:s');
$ip        = isset($_SERVER['REMOTE_ADDR']) ? $_SERVER['REMOTE_ADDR'] : '-';

$subject = "[홈페이지 상담신청] {$fieldName} · {$name}";

$body  = "법률사무소 올본 홈페이지에서 상담 신청이 접수되었습니다.\n";
$body .= str_repeat('─', 40) . "\n";
$body .= "성함       : {$name}\n";
$body .= "연락처     : {$phone}\n";
$body .= "이메일     : " . ($email !== '' ? $email : '(미입력)') . "\n";
$body .= "상담 분야  : {$fieldName}\n";
$body .= "접수 일시  : {$when}\n";
$body .= "접속 IP    : {$ip}\n";
$body .= str_repeat('─', 40) . "\n\n";
$body .= "[상담 내용]\n{$message}\n\n";
$body .= str_repeat('─', 40) . "\n";
$body .= "· 신청자는 개인정보 수집·이용에 동의하였습니다.\n";
$body .= "· 상담 종료 후 3개월 이내 파기 대상입니다.\n";

$headers  = "From: " . mb_encode_mimeheader($FROM_NAME, 'UTF-8') . " <{$FROM_EMAIL}>\r\n";
$headers .= "Reply-To: " . ($email !== '' ? $email : $FROM_EMAIL) . "\r\n";
$headers .= "MIME-Version: 1.0\r\n";
$headers .= "Content-Type: text/plain; charset=UTF-8\r\n";
$headers .= "Content-Transfer-Encoding: 8bit\r\n";

$sent = @mail($RECEIVER,
              mb_encode_mimeheader($subject, 'UTF-8'),
              $body,
              $headers,
              "-f{$FROM_EMAIL}");

/* ── 5. 기록 및 응답 ────────────────────────────────────────────────────── */

if ($SAVE_LOG) {
    @file_put_contents($LOG_FILE,
        "[{$when}] {$name} / {$phone} / {$email} / {$fieldName}\n{$message}\n\n",
        FILE_APPEND | LOCK_EX);
}

if (!$sent) {
    // 호스팅이 mail() 을 막아둔 경우입니다. README 4번의 SMTP 방식을 참고하세요.
    out(false, '메일 발송에 실패했습니다. 전화나 이메일로 연락해 주세요.', 500);
}

out(true);
