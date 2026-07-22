<?php
// ==========================================
// TELEGRAM WEB-APP UPLOAD HANDLER
// ==========================================

header('Content-Type: application/json');

$TELEGRAM_TOKEN = "8674470670:AAER3Y3EfZ44eFUhxKTpsGX_X_Vg6LvKYOQ";
$ADMIN_ID = 5701828462;

// Ruxsat etilgan fayl formatlari
$allowed_mimes = ['video/mp4', 'video/quicktime'];

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    echo json_encode(['success' => false, 'error' => 'Not a POST request']);
    exit;
}

if (!isset($_FILES['video']) || $_FILES['video']['error'] !== UPLOAD_ERR_OK) {
    echo json_encode(['success' => false, 'error' => 'Fayl yuklashda xatolik yuz berdi. Error code: ' . ($_FILES['video']['error'] ?? 'Noma\'lum')]);
    exit;
}

$file = $_FILES['video'];
$file_mime = mime_content_type($file['tmp_name']);

if (!in_array($file_mime, $allowed_mimes)) {
    echo json_encode(['success' => false, 'error' => "Faqat MP4 va MOV fayllar qabul qilinadi. Sizniki: $file_mime"]);
    exit;
}

// Uploads papkasini yaratish
$upload_dir = __DIR__ . '/uploads';
if (!is_dir($upload_dir)) {
    mkdir($upload_dir, 0755, true);
    // Xavfsizlik uchun .htaccess
    file_put_contents($upload_dir . '/.htaccess', "Options -Indexes\nAllow from all");
}

// Unikal nom beramiz
$ext = pathinfo($file['name'], PATHINFO_EXTENSION);
if (!$ext) $ext = 'mp4';
$new_filename = 'webapp_' . time() . '_' . rand(1000, 9999) . '.' . $ext;
$dest_path = $upload_dir . '/' . $new_filename;

if (move_uploaded_file($file['tmp_name'], $dest_path)) {
    
    // Faylning public URL manzilini yaratamiz
    $protocol = isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] === 'on' ? "https" : "http";
    $host = $_SERVER['HTTP_HOST'];
    $path = rtrim(dirname($_SERVER['REQUEST_URI']), '/');
    $video_url = $protocol . "://" . $host . $path . "/uploads/" . $new_filename;
    
    // bot.php logic ga ulaymiz (Xuddi Telegramdan kelgandek)
    file_put_contents("last_video.txt", $video_url);
    
    // Telegramga xabar jo'natamiz
    $keyboard = json_encode([
        "inline_keyboard" => [
            [
                ["text" => "🤖 AI O'zi yozsin", "callback_data" => "video_ai"],
                ["text" => "✍️ O'zim yozaman", "callback_data" => "video_manual"]
            ]
        ]
    ]);
    
    $text = "☁️ <b>Web-App orqali KATTA VIDEO qabul qilindi!</b>\n\nFayl hajmi: " . number_format($file['size'] / 1048576, 2) . " MB\n\nIzohni kim yozadi?";
    
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
