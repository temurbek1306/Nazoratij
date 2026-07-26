<?php
// ==========================================
// TELEGRAM "PULT" BOTI - CUSTOM CRON SCHEDULER
// ==========================================

$CONFIG_FILE = 'config.json';
$GITHUB_PAT = "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"; // O'zgartirish shart emas (hozircha)
$GITHUB_REPO = "temurbek1306/InstagaramAvtoReels";

// 1️⃣ ANIQ VAQTGA BELGILANGAN VIDEOLARNI O'QISH VA HIMOYA QILISH
$SCHEDULED_FILE = 'scheduled.json';
$scheduled_videos = [];
$protected_urls = [];

if (file_exists($SCHEDULED_FILE)) {
    $scheduled_videos = json_decode(file_get_contents($SCHEDULED_FILE), true) ?: [];
    foreach ($scheduled_videos as $sv) {
        $protected_urls[] = $sv['video_url'];
    }
}

// 🧹 ESKI FAYLLARNI TOZALASH (Server xotirasini asrash)
$upload_dir = __DIR__ . '/uploads';
if (is_dir($upload_dir)) {
    $files = glob($upload_dir . '/*');
    $now = time();
    foreach ($files as $f) {
        if (is_file($f) && basename($f) != '.htaccess') {
            // Agar fayl aynan rejalashtirilgan videolarga tegishli bo'lsa, tegmaymiz
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

// 2️⃣ ANIQ VAQTGA BELGILANGAN VIDEOLARNI TEKSHIRISH VA JOYLASHTIRISH
$current_time = time();
$scheduled_triggered = false;

foreach ($scheduled_videos as $index => $sv) {
    if ($current_time >= $sv['post_time']) {
        // Vaqti keldi! GitHub'ni aynan shu video uchun ishga tushiramiz
        $url = "https://api.github.com/repos/" . $GITHUB_REPO . "/dispatches";
        $data = array(
            "event_type" => "telegram_post",
            "client_payload" => array(
                "video_url" => $sv['video_url'],
                "caption" => $sv['caption'],
                "custom_name" => isset($sv['custom_name']) ? $sv['custom_name'] : "",
                "platform" => isset($sv['platform']) ? $sv['platform'] : "both"
            )
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
            echo "✅ Aniq vaqtga belgilangan video joylandi!\n";
            // Ro'yxatdan o'chiramiz (faqat bittasini post qilamiz, keyingisi keyingi daqiqada)
            array_splice($scheduled_videos, $index, 1);
            file_put_contents($SCHEDULED_FILE, json_encode($scheduled_videos, JSON_PRETTY_PRINT));
            $scheduled_triggered = true;
            break; 
        } else {
            echo "❌ Rejadagi videoni yuborishda xatolik: HTTP $httpcode\n";
        }
    }
}

// 3️⃣ STANDART (HAR X SOATDA) NAVBATNI TEKSHIRISH
// Agar bu daqiqada aniq vaqtga belgilangan video chiqmagan bo'lsa, navbatni tekshiramiz
if (!$scheduled_triggered) {
    $interval_seconds = $config['interval_hours'] * 3600;
    
    if ($current_time >= ($config['last_run'] + $interval_seconds)) {
        // Vaqti keldi! GitHub'ni ishga tushiramiz (faqat telegram_post)
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
            $config['last_run'] = $current_time;
            file_put_contents($CONFIG_FILE, json_encode($config));
            echo "✅ Standart navbat (Queue) ishga tushdi!\n";
        } else {
            echo "❌ Navbat yuborishda xatolik: HTTP $httpcode\n";
        }
    } else {
        $remaining = ($config['last_run'] + $interval_seconds) - $current_time;
        echo "⏳ Standart navbat uchun hali erta. " . round($remaining/60) . " daqiqa qoldi.\n";
    }
}
?>
