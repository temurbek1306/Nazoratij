<?php
// ==========================================
// TELEGRAM "PULT" BOTI - CUSTOM CRON SCHEDULER v4.0
// ==========================================
// MUHIM YANGILANISH: Telegram diagnostik log qo'shildi
// Har bir cron ishlaganda nima bo'layotganini ko'rish mumkin

date_default_timezone_set('Asia/Tashkent');
$CONFIG_FILE = __DIR__ . '/config.json';
$GITHUB_PAT = "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";
$GITHUB_REPO = "temurbek1306/InstagaramAvtoReels";

// Telegram log funksiyasi
$TELEGRAM_TOKEN = "8674470670:AAER3Y3EfZ44eFUhxKTpsGX_X_Vg6LvKYOQ";
$ADMIN_ID = 5701828462;

function sendTelegramLog($token, $chat_id, $text) {
    $url = "https://api.telegram.org/bot" . $token . "/sendMessage";
    $data = array(
        'chat_id' => $chat_id,
        'text' => $text,
        'parse_mode' => 'HTML'
    );
    $options = array(
        'http' => array(
            'header'  => "Content-type: application/x-www-form-urlencoded\r\n",
            'method'  => 'POST',
            'content' => http_build_query($data),
            'timeout' => 5
        )
    );
    $context = stream_context_create($options);
    @file_get_contents($url, false, $context);
}

// 1️⃣ ANIQ VAQTGA BELGILANGAN VIDEOLARNI O'QISH VA HIMOYA QILISH
$SCHEDULED_FILE = __DIR__ . '/scheduled.json';
$scheduled_videos = [];
$protected_urls = [];

if (file_exists($SCHEDULED_FILE)) {
    $raw_content = file_get_contents($SCHEDULED_FILE);
    $scheduled_videos = json_decode($raw_content, true);
    
    // JSON parse xatosini tekshirish
    if ($scheduled_videos === null && json_last_error() !== JSON_ERROR_NONE) {
        $err = json_last_error_msg();
        sendTelegramLog($TELEGRAM_TOKEN, $ADMIN_ID, "❌ <b>CRON XATO:</b> scheduled.json ni o'qib bo'lmadi!\n\nJSON xato: <code>$err</code>\n\nFayl kontenti:\n<pre>" . htmlspecialchars(substr($raw_content, 0, 500)) . "</pre>");
        $scheduled_videos = [];
    }
    
    if (!is_array($scheduled_videos)) {
        $scheduled_videos = [];
    }
    
    foreach ($scheduled_videos as $sv) {
        if (isset($sv['video_url'])) {
            $protected_urls[] = $sv['video_url'];
        }
    }
} else {
    // scheduled.json mavjud emas - bu normal holat
}

// 🧹 ESKI FAYLLARNI TOZALASH (Server xotirasini asrash)
$upload_dir = __DIR__ . '/uploads';
if (is_dir($upload_dir)) {
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

// Default settings
$config = [
    "interval_hours" => 2,
    "last_run" => 0
];

if (file_exists($CONFIG_FILE)) {
    $config = json_decode(file_get_contents($CONFIG_FILE), true);
    if (!is_array($config)) {
        $config = ["interval_hours" => 2, "last_run" => 0];
    }
} else {
    file_put_contents($CONFIG_FILE, json_encode($config));
}

// 2️⃣ ANIQ VAQTGA BELGILANGAN VIDEOLARNI TEKSHIRISH VA JOYLASHTIRISH
$current_time = time();
$scheduled_triggered = false;
$cron_log = []; // diagnostik log

if (count($scheduled_videos) > 0) {
    $cron_log[] = "📋 scheduled.json da " . count($scheduled_videos) . " ta video bor:";
    foreach ($scheduled_videos as $i => $sv) {
        $post_time = isset($sv['post_time']) ? $sv['post_time'] : 0;
        $formatted = date("d.m.Y H:i:s", $post_time);
        $diff = $post_time - $current_time;
        $has_url = !empty($sv['video_url']) ? "✅ URL bor" : "❌ URL yo'q";
        $is_trial = !empty($sv['is_trial']) ? "🧪 Trial" : "📹 Oddiy";
        
        if ($diff > 0) {
            $mins = round($diff / 60);
            $cron_log[] = "  " . ($i+1) . ". $formatted ($mins daqiqa qoldi) | $is_trial | $has_url";
        } else {
            $cron_log[] = "  " . ($i+1) . ". $formatted (⏰ VAQTI KELDI! " . abs(round($diff/60)) . " daqiqa o'tdi) | $is_trial | $has_url";
        }
    }
}

foreach ($scheduled_videos as $index => $sv) {
    // post_time mavjudligini tekshirish
    if (!isset($sv['post_time']) || !is_numeric($sv['post_time'])) {
        $cron_log[] = "⚠️ #" . ($index+1) . " da post_time noto'g'ri! O'chirilmoqda...";
        array_splice($scheduled_videos, $index, 1);
        file_put_contents($SCHEDULED_FILE, json_encode($scheduled_videos, JSON_PRETTY_PRINT));
        continue;
    }
    
    if ($current_time >= $sv['post_time']) {
        // Vaqti keldi! GitHub'ni aynan shu video uchun ishga tushiramiz
        $cron_log[] = "🚀 #" . ($index+1) . " ning vaqti keldi! GitHub dispatch yuborilmoqda...";
        
        // Video URL mavjudligini tekshirish
        $video_url = isset($sv['video_url']) ? $sv['video_url'] : "";
        if (empty($video_url)) {
            $cron_log[] = "❌ Video URL bo'sh! Bu video o'chirilmoqda.";
            array_splice($scheduled_videos, $index, 1);
            file_put_contents($SCHEDULED_FILE, json_encode($scheduled_videos, JSON_PRETTY_PRINT));
            continue;
        }
        
        // Video URL hali ham ishlaydimi tekshirish
        $check_headers = @get_headers($video_url, 1);
        $url_status = "?";
        if ($check_headers) {
            $url_status = is_array($check_headers[0]) ? $check_headers[0][0] : $check_headers[0];
        }
        $cron_log[] = "🔗 URL holati: $url_status";
        $cron_log[] = "🔗 URL: " . substr($video_url, 0, 80) . "...";
        
        $url = "https://api.github.com/repos/" . $GITHUB_REPO . "/dispatches";
        
        // is_trial ni to'g'ri string ga aylantirish
        $is_trial_val = "false";
        if (isset($sv['is_trial'])) {
            if ($sv['is_trial'] === true || $sv['is_trial'] === "true" || $sv['is_trial'] === 1) {
                $is_trial_val = "true";
            }
        }
        
        $data = array(
            "event_type" => "telegram_post",
            "client_payload" => array(
                "video_url" => $video_url,
                "caption" => isset($sv['caption']) ? $sv['caption'] : "",
                "custom_name" => isset($sv['custom_name']) ? $sv['custom_name'] : "",
                "platform" => isset($sv['platform']) ? $sv['platform'] : "both",
                "is_trial" => $is_trial_val
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
        curl_setopt($ch, CURLOPT_TIMEOUT, 15);
        $response = curl_exec($ch);
        $httpcode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        $curl_error = curl_error($ch);
        curl_close($ch);
        
        if ($httpcode >= 200 && $httpcode < 300) {
            $cron_log[] = "✅ GitHub dispatch MUVAFFAQIYATLI (HTTP $httpcode)!";
            array_splice($scheduled_videos, $index, 1);
            file_put_contents($SCHEDULED_FILE, json_encode($scheduled_videos, JSON_PRETTY_PRINT));
            $scheduled_triggered = true;
            
            // Telegramga xabar
            $trial_badge = ($is_trial_val === "true") ? " 🧪 [Trial]" : "";
            sendTelegramLog($TELEGRAM_TOKEN, $ADMIN_ID, 
                "⏱ <b>Rejalashtirilgan video ishga tushdi!</b>$trial_badge\n\n" .
                "Video GitHub'ga yuborildi va tez orada joylanadi.\n" .
                "Qolgan rejalashtirilgan videolar: " . count($scheduled_videos)
            );
            
            break; 
        } else {
            $cron_log[] = "❌ GitHub dispatch XATO! HTTP $httpcode";
            if ($curl_error) {
                $cron_log[] = "  curl xato: $curl_error";
            }
            if ($response) {
                $cron_log[] = "  javob: " . substr($response, 0, 200);
            }
            
            sendTelegramLog($TELEGRAM_TOKEN, $ADMIN_ID,
                "❌ <b>CRON XATO: Rejalashtirilgan video yuborib bo'lmadi!</b>\n\n" .
                "HTTP: $httpcode\n" .
                "Xato: $curl_error\n" .
                "Javob: " . htmlspecialchars(substr($response, 0, 200))
            );
        }
    }
}

// 3️⃣ STANDART (HAR X SOATDA) NAVBATNI TEKSHIRISH
if (!$scheduled_triggered) {
    $interval_seconds = $config['interval_hours'] * 3600;
    
    if ($current_time >= ($config['last_run'] + $interval_seconds)) {
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
        curl_setopt($ch, CURLOPT_TIMEOUT, 15);
        $response = curl_exec($ch);
        $httpcode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        
        if ($httpcode >= 200 && $httpcode < 300) {
            $config['last_run'] = $current_time;
            file_put_contents($CONFIG_FILE, json_encode($config));
            $cron_log[] = "✅ Standart navbat ishga tushdi!";
        } else {
            $cron_log[] = "❌ Standart navbat xatosi: HTTP $httpcode";
        }
    } else {
        $remaining = ($config['last_run'] + $interval_seconds) - $current_time;
        $cron_log[] = "⏳ Standart navbat: " . round($remaining/60) . " daqiqa qoldi";
    }
}

// 4️⃣ DIAGNOSTIK LOGNI FAYLGA YOZISH (har doim)
$log_line = date("Y-m-d H:i:s") . " | scheduled=" . count($scheduled_videos) . " | " . implode(" | ", $cron_log);
file_put_contents(__DIR__ . '/cron_log.txt', $log_line . "\n", FILE_APPEND);

// Agar scheduled videolar bor bo'lsa va muammo bo'lsa, Telegramga yuborish
if (count($cron_log) > 0 && count($scheduled_videos) > 0 && !$scheduled_triggered) {
    // Faqat 10 daqiqada bir marta diagnostik log yuborish (spam oldini olish)
    $last_diag = 0;
    if (file_exists(__DIR__ . '/last_diag_time.txt')) {
        $last_diag = intval(file_get_contents(__DIR__ . '/last_diag_time.txt'));
    }
    if ($current_time - $last_diag >= 600) {
        file_put_contents(__DIR__ . '/last_diag_time.txt', $current_time);
        sendTelegramLog($TELEGRAM_TOKEN, $ADMIN_ID,
            "🔍 <b>CRON Diagnostika</b> (" . date("H:i") . ")\n\n" . implode("\n", $cron_log)
        );
    }
}

echo implode("\n", $cron_log) . "\n";
echo "Vaqt: " . date("Y-m-d H:i:s") . "\n";
?>
