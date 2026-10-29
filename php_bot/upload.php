<?php
// ==========================================
// TELEGRAM WEB-APP UPLOAD HANDLER
// ==========================================

header('Content-Type: application/json');
if (file_exists(__DIR__ . '/config.php')) { require_once __DIR__ . '/config.php'; }

$TELEGRAM_TOKEN = getenv("TELEGRAM_BOT_TOKEN");
$ADMIN_ID = 5701828462;

// Ruxsat etilgan fayl formatlari
$allowed_mimes = ['video/mp4', 'video/quicktime'];

// post_max_size oshib ketsa PHP $_POST va $_FILES ni jimgina bo'shatadi
if (empty($_FILES) && (int)($_SERVER['CONTENT_LENGTH'] ?? 0) > 0) {
    echo json_encode(['success' => false, 'error' => 'Fayl juda katta. Server limiti: post_max_size=' . ini_get('post_max_size') . ', upload_max_filesize=' . ini_get('upload_max_filesize')]);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    echo json_encode(['success' => false, 'error' => 'Not a POST request']);
    exit;
}

if (!isset($_FILES['video']) || $_FILES['video']['error'] !== UPLOAD_ERR_OK) {
    echo json_encode(['success' => false, 'error' => 'Fayl yuklashda xatolik yuz berdi. Error code: ' . ($_FILES['video']['error'] ?? 'Noma\'lum')]);
    exit;
}

// Uploads papkasini yaratish
$upload_dir = __DIR__ . '/uploads';
if (!is_dir($upload_dir)) {
    mkdir($upload_dir, 0755, true);
}

// 📦 BO'LAKLAB YUKLASH: video kichik bo'laklarda keladi va .part faylga yig'iladi
$upload_id = preg_replace('/[^a-zA-Z0-9_]/', '', $_POST['upload_id'] ?? '');
$chunk_index = (int)($_POST['chunk_index'] ?? 0);
$chunk_total = (int)($_POST['chunk_total'] ?? 0);
$chunk_offset = (int)($_POST['offset'] ?? 0);

// Eski (keshdagi) upload.html faylni bir butunda yuboradi — uni bitta bo'lak deb qabul qilamiz
if ($upload_id === '' || $chunk_total < 1) {
    $upload_id = 'single_' . time() . '_' . rand(1000, 9999);
    $chunk_index = 0;
    $chunk_total = 1;
    $chunk_offset = 0;
    $_POST['file_name'] = $_FILES['video']['name'];
    $_POST['file_type'] = $_FILES['video']['type'];
}

$part_path = $upload_dir . '/tmp_' . $upload_id . '.part';
$fp = fopen($part_path, 'c');
if (!$fp) {
    echo json_encode(['success' => false, 'error' => "Vaqtinchalik faylni ochib bo'lmadi. Jildga ruxsatlarni tekshiring."]);
    exit;
}
clearstatcache(true, $part_path);
$current_size = filesize($part_path);
if ($current_size < $chunk_offset) {
    fclose($fp);
    echo json_encode(['success' => false, 'error' => "Oldingi bo'lak yetib kelmagan, qaytadan yuklang"]);
    exit;
}
// Qayta yuborilgan bo'lak ikki marta yozilmasligi uchun offset'gacha qirqamiz
ftruncate($fp, $chunk_offset);
fseek($fp, $chunk_offset);
fwrite($fp, file_get_contents($_FILES['video']['tmp_name']));
fclose($fp);

if ($chunk_index < $chunk_total - 1) {
    echo json_encode(['success' => true, 'chunk' => $chunk_index]);
    exit;
}

// Oxirgi bo'lak keldi — to'liq fayl tayyor
clearstatcache(true, $part_path);
$file = [
    'name' => basename($_POST['file_name'] ?? 'video.mp4'),
    'size' => filesize($part_path),
    'tmp_name' => $part_path,
];
$file_mime = function_exists('mime_content_type') ? mime_content_type($file['tmp_name']) : ($_POST['file_type'] ?? '');

if (!in_array($file_mime, $allowed_mimes)) {
    unlink($part_path);
    echo json_encode(['success' => false, 'error' => "Faqat MP4 va MOV fayllar qabul qilinadi. Sizniki: $file_mime"]);
    exit;
}

// Uploads papkasi uchun .htaccess
if (!file_exists($upload_dir . '/.htaccess')) {
    // Xavfsizlik uchun .htaccess
    file_put_contents($upload_dir . '/.htaccess', "Options -Indexes\nAllow from all");
}

// 🧹 ESKI FAYLLARNI TOZALASH (Memory Leak oldini olish)
// 24 soatdan eskirgan videolarni o'chiramiz, LEKIN rejalashtirilganlarni (scheduled) himoya qilamiz
if (is_dir($upload_dir)) {
    $scheduled_file = __DIR__ . '/scheduled.json';
    $protected_urls = [];
    if (file_exists($scheduled_file)) {
        $scheduled_videos = json_decode(file_get_contents($scheduled_file), true) ?: [];
        foreach ($scheduled_videos as $sv) {
            $protected_urls[] = $sv['video_url'];
        }
    }

    $files = glob($upload_dir . '/*');
    $now = time();
    foreach ($files as $f) {
        if (is_file($f) && basename($f) != '.htaccess') {
            $is_protected = false;
            foreach ($protected_urls as $p_url) {
                if (strpos($p_url, basename($f)) !== false) {
                    $is_protected = true;
                    break;
                }
            }
            if (!$is_protected && ($now - filemtime($f) >= 86400)) { 
                unlink($f);
            }
        }
    }
}

// Unikal nom beramiz
$ext = pathinfo($file['name'], PATHINFO_EXTENSION);
if (!$ext) $ext = 'mp4';
$new_filename = 'webapp_' . time() . '_' . rand(1000, 9999) . '.' . $ext;
$dest_path = $upload_dir . '/' . $new_filename;

if (rename($file['tmp_name'], $dest_path)) {
    
    // Faylning public URL manzilini yaratamiz
    $protocol = ((isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] === 'on') || ($_SERVER['HTTP_X_FORWARDED_PROTO'] ?? '') === 'https') ? "https" : "http";
    $host = $_SERVER['HTTP_HOST'];
    $path = rtrim(dirname($_SERVER['REQUEST_URI']), '/');
    $video_url = $protocol . "://" . $host . $path . "/uploads/" . $new_filename;
    
    // bot.php logic ga ulaymiz (Xuddi Telegramdan kelgandek)
    file_put_contents("last_video.txt", $video_url);
    if (file_exists("last_caption.txt")) @unlink("last_caption.txt");
    if (file_exists("last_first_comment.txt")) @unlink("last_first_comment.txt");
    if (file_exists("last_thumbnail.txt")) @unlink("last_thumbnail.txt");
    $upload_type = isset($_POST['type']) ? $_POST['type'] : 'normal';
    
    if ($upload_type === 'trial') {
        file_put_contents("last_trial.txt", "true");
        file_put_contents("last_platform.txt", "ig");
    } else {
        file_put_contents("last_trial.txt", "false");
    }
    
    $thumb_keyboard = json_encode([
        "inline_keyboard" => [
            [
                ["text" => "📸 Ha, rasm yuboraman", "callback_data" => "thumb_manual"],
                ["text" => "⏭ Kerak emas (O'tkazish)", "callback_data" => "thumb_skip"]
            ]
        ]
    ]);
    
    $mode_title = ($upload_type === 'trial') ? "TRIAL VIDEO" : "VIDEO";
    $text = "☁️ <b>Web-App orqali {$mode_title} qabul qilindi!</b>\n\nFayl hajmi: " . number_format($file['size'] / 1048576, 2) . " MB\n\n🖼 <b>Reels uchun muqova (Thumbnail) rasm qo'ymoqchimisiz?</b>";
    $keyboard = $thumb_keyboard;
    
    $url = "https://api.telegram.org/bot" . $TELEGRAM_TOKEN . "/sendMessage";
    $data = array(
        'chat_id' => $ADMIN_ID,
        'text' => $text,
        'parse_mode' => 'HTML',
        'reply_markup' => $keyboard
    );
    
    $options = array(
        'http' => array(
            'header'  => "Content-type: application/x-www-form-urlencoded\r\n",
            'method'  => 'POST',
            'content' => http_build_query($data)
        )
    );
    $context  = stream_context_create($options);
    file_get_contents($url, false, $context);
    
    echo json_encode(['success' => true, 'url' => $video_url]);
} else {
    echo json_encode(['success' => false, 'error' => 'Faylni serverda saqlash imkoni bo\'lmadi. Jildga ruxsatlarni tekshiring.']);
}
?>
