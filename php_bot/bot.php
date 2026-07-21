<?php
// ==========================================
// TELEGRAM "PULT" BOTI - PHP WEBHOOK V3.0
// ==========================================

$TELEGRAM_TOKEN = "8674470670:AAER3Y3EfZ44eFUhxKTpsGX_X_Vg6LvKYOQ";
$ADMIN_ID = 5701828462;
$GITHUB_PAT = "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";
$GITHUB_REPO = "temurbek1306/InstagaramAvtoReels";

$update = json_decode(file_get_contents('php://input'), TRUE);

if (isset($update['message'])) {
    $chat_id = $update['message']['chat']['id'];
    
    if ($chat_id != $ADMIN_ID) {
        sendMessage($chat_id, "⛔️ Kechirasiz, siz ushbu botdan foydalanish huquqiga ega emassiz.");
        exit;
    }
    
    // Video upload
    if (isset($update['message']['video'])) {
        $file_id = $update['message']['video']['file_id'];
        $file_path = getFilePath($file_id);
        
        if ($file_path) {
            $video_url = "https://api.telegram.org/file/bot" . $TELEGRAM_TOKEN . "/" . $file_path;
            
            // Fayl manzilini vaqtincha saqlab qo'yamiz (Tugma bosilganda o'qish uchun)
            file_put_contents("last_video.txt", $video_url);
            
            $keyboard = json_encode([
                "inline_keyboard" => [
                    [
                        ["text" => "📥 Navbatga qo'shish", "callback_data" => "act_queue"],
                        ["text" => "🚀 Hozir joylash", "callback_data" => "act_postnow"]
                    ]
                ]
            ]);
            sendMessage($chat_id, "🎬 Video qabul qilindi!\n\nNima qilamiz? Hozirning o'zida post qilaymi yoki navbatga qo'shaymi?", $keyboard);
        }
        exit;
    }
    
    // Tugma (Callback) bosilganda
    if (isset($update['callback_query'])) {
        $chat_id = $update['callback_query']['message']['chat']['id'];
        $data = $update['callback_query']['data'];
        $message_id = $update['callback_query']['message']['message_id'];
        
        if ($data == "act_queue" || $data == "act_postnow") {
            if (file_exists("last_video.txt")) {
                $video_url = file_get_contents("last_video.txt");
                
                if ($data == "act_queue") {
                    sendMessage($chat_id, "📥 Video faqat navbatga (Queue) qo'shildi! Vaqti kelganda avtomatik joylanadi.");
                    triggerGitHubAction("telegram_queue", array("video_url" => $video_url));
                } else {
                    sendMessage($chat_id, "🚀 Video hozir joylash uchun tayyorlanmoqda...");
                    triggerGitHubAction("telegram_post", array("video_url" => $video_url));
                }
                
                // Takror bosilmasligi uchun tugmalarni o'chirib tashlash
                $url = "https://api.telegram.org/bot" . $TELEGRAM_TOKEN . "/editMessageReplyMarkup";
                file_get_contents($url . "?chat_id=$chat_id&message_id=$message_id&reply_markup=" . json_encode(["inline_keyboard" => []]));
            } else {
                sendMessage($chat_id, "❌ Video manzili topilmadi. Qaytadan yuboring.");
            }
            exit;
        }
        elseif (strpos($data, "post_a_") === 0 || strpos($data, "post_b_") === 0 || strpos($data, "post_c_") === 0 || strpos($data, "cancel_") === 0) {
            // A, B, C matnlari tanlanganda yoki Bekor qilinganda
            triggerGitHubAction("telegram_command", array("command" => $data));
            
            // Takror bosilmasligi uchun tugmalarni o'chirib tashlash
            $url = "https://api.telegram.org/bot" . $TELEGRAM_TOKEN . "/editMessageReplyMarkup";
            file_get_contents($url . "?chat_id=$chat_id&message_id=$message_id&reply_markup=" . json_encode(["inline_keyboard" => []]));
            exit;
        }
    }
    
    // Text commands
    $text = isset($update['message']['text']) ? $update['message']['text'] : "";
    
    $main_keyboard = json_encode([
        "keyboard" => [
            [["text" => "🚀 Hozir Joylash"]],
            [["text" => "📊 Statistika"], ["text" => "📋 Navbat (Queue)"]],
            [["text" => "⚙️ Vaqt Sozlamalari"]],
            [["text" => "🗑 Eski videolarni o'chirish"], ["text" => "🗓️ Kontent Reja"]]
        ],
        "resize_keyboard" => true,
        "one_time_keyboard" => false
    ]);
    
    $settings_keyboard = json_encode([
        "keyboard" => [
            [["text" => "Har 1 soatda"], ["text" => "Har 2 soatda"]],
            [["text" => "Har 3 soatda"], ["text" => "Har 4 soatda"]],
            [["text" => "🔙 Ortga"]]
        ],
        "resize_keyboard" => true,
        "one_time_keyboard" => false
    ]);

    if ($text == "/start" || $text == "/menu" || $text == "🔙 Ortga") {
        setupBotCommands();
        sendMessage($chat_id, "👋 Salom, Boss! Ultra God Mode (v3.0) aktiv.\n\nPastdagi menyudan kerakli tugmani tanlang:", $main_keyboard);
    } 
    elseif ($text == "🚀 Hozir Joylash") {
        sendMessage($chat_id, "🚀 <b>Videoni joylash jarayoni boshlandi!</b>\n\nNavbatdagi (Pending) video hozir tarmoqlarga joylanadi (1-2 daqiqa kuting).");
        triggerGitHubAction("telegram_post", array("video_url" => ""));
    }
    elseif ($text == "📊 Statistika" || $text == "/stats") {
        sendMessage($chat_id, "⏳ Statistika yig'ilmoqda...");
        triggerGitHubAction("telegram_command", array("command" => "stats"));
    }
    elseif ($text == "📋 Navbat (Queue)" || $text == "/list") {
        sendMessage($chat_id, "⏳ Navbat tekshirilmoqda...");
        triggerGitHubAction("telegram_command", array("command" => "list"));
    }
    elseif ($text == "🗑 Eski videolarni o'chirish" || $text == "/clear") {
        sendMessage($chat_id, "⏳ Tozalanmoqda...");
        triggerGitHubAction("telegram_command", array("command" => "clear"));
    }
    elseif ($text == "🗓️ Kontent Reja" || $text == "/strategy") {
        sendMessage($chat_id, "⏳ AI Tahlil boshlandi! Butun O'zbekiston tarmog'i skaner qilinmoqda...");
        triggerGitHubAction("telegram_command", array("command" => "strategy"));
    }
    elseif ($text == "⚙️ Vaqt Sozlamalari" || $text == "/settings") {
        sendMessage($chat_id, "⚙️ <b>Vaqt Sozlamalari</b>\n\nVideolar har necha soatda avtomatik post qilinishini tanlang:", $settings_keyboard);
    }
    elseif (strpos($text, "Har ") === 0 && strpos($text, " soatda") !== false) {
        $hours = (int) filter_var($text, FILTER_SANITIZE_NUMBER_INT);
        if ($hours > 0) {
            $config_file = 'config.json';
            $config = ["interval_hours" => 2, "last_run" => 0];
            if (file_exists($config_file)) {
                $config = json_decode(file_get_contents($config_file), true);
            }
            $config['interval_hours'] = $hours;
            file_put_contents($config_file, json_encode($config));
            sendMessage($chat_id, "✅ Vaqt sozlandi! Endi videolar har <b>$hours soatda</b> post qilinadi.", $main_keyboard);
        }
    }
    elseif ($text != "") {
        // Brainstorming or invalid
        sendMessage($chat_id, "🧠 AI o'ylamoqda... / Link tekshirilmoqda...");
        triggerGitHubAction("telegram_command", array("command" => "brainstorm", "prompt" => $text));
    }
}

// ==========================
// YORDAMCHI FUNKSIYALAR
// ==========================

function setupBotCommands() {
    global $TELEGRAM_TOKEN;
    $url = "https://api.telegram.org/bot" . $TELEGRAM_TOKEN . "/setMyCommands";
    $commands = [
        ["command" => "start", "description" => "Asosiy menyuni ochish"],
        ["command" => "stats", "description" => "Hozirgi statistika"],
        ["command" => "list", "description" => "Navbatdagi videolar"],
        ["command" => "strategy", "description" => "1 Oylik AI Reja"],
        ["command" => "settings", "description" => "Vaqt sozlamalari"]
    ];
    $data = ['commands' => json_encode($commands)];
    
    $options = [
        'http' => [
            'header'  => "Content-type: application/x-www-form-urlencoded\r\n",
            'method'  => 'POST',
            'content' => http_build_query($data)
        ]
    ];
    $context  = stream_context_create($options);
    file_get_contents($url, false, $context);
}

function sendMessage($chat_id, $text, $reply_markup = null) {
    global $TELEGRAM_TOKEN;
    $url = "https://api.telegram.org/bot" . $TELEGRAM_TOKEN . "/sendMessage";
    $data = array(
        'chat_id' => $chat_id,
        'text' => $text,
        'parse_mode' => 'HTML'
    );
    if ($reply_markup) {
        $data['reply_markup'] = $reply_markup;
    }
    
    $options = array(
        'http' => array(
            'header'  => "Content-type: application/x-www-form-urlencoded\r\n",
            'method'  => 'POST',
            'content' => http_build_query($data)
        )
    );
    $context  = stream_context_create($options);
    file_get_contents($url, false, $context);
}

function getFilePath($file_id) {
    global $TELEGRAM_TOKEN;
    $url = "https://api.telegram.org/bot" . $TELEGRAM_TOKEN . "/getFile?file_id=" . $file_id;
    $result = file_get_contents($url);
    if ($result) {
        $json = json_decode($result, true);
        if (isset($json['result']['file_path'])) {
            return $json['result']['file_path'];
        }
    }
    return false;
}

function triggerGitHubAction($event_type, $payload_data) {
    global $GITHUB_PAT, $GITHUB_REPO;
    $url = "https://api.github.com/repos/" . $GITHUB_REPO . "/dispatches";
    $data = array(
        "event_type" => $event_type,
        "client_payload" => $payload_data
    );
    
    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_HTTPHEADER, array(
        'Accept: application/vnd.github.v3+json',
        'Authorization: Bearer ' . $GITHUB_PAT,
        'User-Agent: Telegram-PHP-Webhook',
        'Content-Type: application/json'
    ));
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
    $response = curl_exec($ch);
    $httpcode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    
    return ($httpcode >= 200 && $httpcode < 300);
}
?>
