<?php
// ==========================================
// TELEGRAM "PULT" BOTI - CUSTOM CRON SCHEDULER
// ==========================================

$CONFIG_FILE = 'config.json';
$GITHUB_PAT = "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"; // O'zgartirish shart emas (hozircha)
$GITHUB_REPO = "temurbek1306/InstagaramAvtoReels";

// 🧹 ESKI FAYLLARNI TOZALASH (Server xotirasini asrash)
// Har safar cron ishlaganda uploads papkasini tekshirib 24 soatdan oshganlarini o'chiradi
$upload_dir = __DIR__ . '/uploads';
if (is_dir($upload_dir)) {
    $files = glob($upload_dir . '/*');
    $now = time();
    foreach ($files as $f) {
        if (is_file($f) && basename($f) != '.htaccess') {
            if ($now - filemtime($f) >= 86400) { 
                unlink($f);
            }
        }
    }
}

// Default settings

$config = [
    "interval_hours" => 2,
    "last_run" => 0
];

if (file_exists($CONFIG_FILE)) {
    $config = json_decode(file_get_contents($CONFIG_FILE), true);
} else {
    file_put_contents($CONFIG_FILE, json_encode($config));
}

$current_time = time();
$interval_seconds = $config['interval_hours'] * 3600;

if ($current_time >= ($config['last_run'] + $interval_seconds)) {
    // Vaqti keldi! GitHub'ni ishga tushiramiz
    $url = "https://api.github.com/repos/" . $GITHUB_REPO . "/dispatches";
    $data = array(
        "event_type" => "telegram_post",
        "client_payload" => array("video_url" => "")
    );
    
    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_HTTPHEADER, array(
        'Accept: application/vnd.github.v3+json',
        'Authorization: Bearer ' . $GITHUB_PAT,
        'User-Agent: Telegram-PHP-Cron',
        'Content-Type: application/json'
    ));
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
    $response = curl_exec($ch);
    $httpcode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    
    if ($httpcode >= 200 && $httpcode < 300) {
        // Muvaffaqiyatli ishga tushdi, vaqtni yangilaymiz
        $config['last_run'] = $current_time;
        file_put_contents($CONFIG_FILE, json_encode($config));
        echo "✅ GitHub Action ishga tushirildi! Keyingi post " . $config['interval_hours'] . " soatdan keyin bo'ladi.";
    } else {
        echo "❌ Xatolik yuz berdi: HTTP " . $httpcode . " " . $response;
    }
} else {
    $remaining = ($config['last_run'] + $interval_seconds) - $current_time;
    echo "⏳ Hali erta. Keyingi postgacha " . round($remaining/60) . " daqiqa qoldi. (Interval: " . $config['interval_hours'] . " soat)";
}
?>
