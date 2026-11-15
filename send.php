<?php
// Latine Mayfair: emails website form submissions (events / Christmas enquiries, newsletter, LACAV list).
// Change TO_EMAIL if enquiries should go elsewhere. Add more addresses comma-separated.
const TO_EMAIL   = 'contact@latinemayfair.com';
const FROM_EMAIL = 'website@latinemayfair.com';   // must be on the latinemayfair.com domain for delivery

header('Content-Type: application/json');
if ($_SERVER['REQUEST_METHOD'] !== 'POST') { http_response_code(405); echo '{"ok":false}'; exit; }
if (!empty($_POST['website'])) { echo '{"ok":true}'; exit; }          // spam honeypot

function clean($v) { return trim(str_replace(["\r", "\n"], ' ', strip_tags((string)$v))); }
$form  = clean($_POST['form'] ?? 'Website form');
$email = filter_var(trim($_POST['email'] ?? ''), FILTER_VALIDATE_EMAIL);
if (!$email) { http_response_code(400); echo '{"ok":false,"error":"email"}'; exit; }

$labels = ['occasion'=>'Occasion','name'=>'Name','company'=>'Company','email'=>'Email','phone'=>'Phone',
           'date'=>'Preferred date','guests'=>'Guests','time'=>'Time','space'=>'Space','message'=>'Message'];
$lines = [];
foreach ($labels as $k => $label) {
  if (isset($_POST[$k]) && $_POST[$k] !== '') {
    $val = $k === 'message' ? trim(strip_tags((string)$_POST[$k])) : clean($_POST[$k]);
    $lines[] = $label . ': ' . $val;
  }
}
$who = clean($_POST['name'] ?? '') ?: $email;
$subject = $form . ' – ' . $who . (isset($_POST['date']) && $_POST['date'] !== '' ? ' – ' . clean($_POST['date']) : '');
$body = $form . " from latinemayfair.com\n\n" . implode("\n", $lines) . "\n\nSent " . date('j M Y, H:i') . "\n";
$headers = "From: Latine Mayfair website <" . FROM_EMAIL . ">\r\nReply-To: " . $email . "\r\nContent-Type: text/plain; charset=UTF-8\r\n";

$ok = mail(TO_EMAIL, '=?UTF-8?B?' . base64_encode($subject) . '?=', $body, $headers, '-f' . FROM_EMAIL);
echo json_encode(['ok' => (bool)$ok]);
