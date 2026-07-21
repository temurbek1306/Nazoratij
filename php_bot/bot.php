<?php
// ==========================================
// TELEGRAM "PULT" BOTI - PHP WEBHOOK V2.0
// ==========================================

// Sozlamalar
$TELEGRAM_TOKEN = "8674470670:AAER3Y3EfZ44eFUhxKTpsGX_X_Vg6LvKYOQ";
$ADMIN_ID = 5701828462;
$GITHUB_PAT = "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"; // Buni GitHub'dan olasiz
$GITHUB_REPO = "temurbek1306/InstagaramAvtoReels";

// Kelayotgan ma'lumotni o'qish
$update = json_decode(file_get_contents('php://input'), TRUE);

// 1. CALLBACK QUERY (Tugmalar bosilganda)
if (isset($update['callback_query'])) {
    $callback_query = $update['callback_query'];
    $chat_id = $callback_query['message']['chat']['id'];
    $data = $callback_query['data'];
    
    if ($chat_id != $ADMIN_ID) exit;
    
    // answerCallbackQuery (Yuklanmoqda animatsiyasini to'xtatish uchun)
    file_get_contents("https://api.telegram.org/bot" . $TELEGRAM_TOKEN . "/answerCallbackQuery?callback_query_id=" . $callback_query['id']);
    
    if (strpos($data, "cmd_") === 0) {
        $cmd = str_replace("cmd_", "", $data);
        sendMessage($chat_id, "⏳ Buyruq qabul qilindi. GitHub muloqot qilmoqda...");
        triggerGitHubAction("telegram_command", array("command" => $cmd));
    }
    exit;
}

// 2. ODDY XABAR (Matn yoki Video)
if (isset($update['message'])) {
    $chat_id = $update['message']['chat']['id'];
    
    if ($chat_id != $ADMIN_ID) {
        sendMessage($chat_id, "⛔️ Kechirasiz, siz ushbu botdan foydalanish huquqiga ega emassiz.");
        exit;
    }
    
    // Video kelganda
    if (isset($update['message']['video'])) {
        $file_id = $update['message']['video']['file_id'];
        sendMessage($chat_id, "⏳ Video qabul qilindi! GitHub'ga tayyorlayapman...");
        $file_path = getFilePath($file_id);
        
        if ($file_path) {
            $video_url = "https://api.telegram.org/file/bot" . $TELEGRAM_TOKEN . "/" . $file_path;
            $github_result = triggerGitHubAction("telegram_post", array("video_url" => $video_url));
            if ($github_result) {
                sendMessage($chat_id, "🚀 GitHub'ga buyruq berildi! Fonda IG/YT ga joylanmoqda.");
            } else {
                sendMessage($chat_id, "❌ GitHub'ga ulanishda xatolik yuz berdi.");
            }
        } else {
            sendMessage($chat_id, "❌ Videoni tortib olishda xatolik yuz berdi (Max hajmi 20MB).");
        }
    } 
    // Matn kelganda
    else {
        $text = isset($update['message']['text']) ? $update['message']['text'] : "";
        
        if ($text == "/start" || $text == "/menu") {
            $keyboard = json_encode([
                "inline_keyboard" => [
                    [
                        ["text" => "📊 Statistika", "callback_data" => "cmd_stats"],
                        ["text" => "🚀 Zudlik bilan Post", "callback_data" => "cmd_post_now"]
                    ],
                    [
                        ["text" => "📋 Navbat (Queue)", "callback_data" => "cmd_list"],
                        ["text" => "🧹 Tozalash", "callback_data" => "cmd_clear"]
                    ]
                ]
            ]);
            sendMessage($chat_id, "👋 Salom, Boss! Ultra God Mode (v2.0) aktiv.\n\nQuyidagi tugmalardan birini tanlang yoki menga biror savol bering (AI Brainstorm):", $keyboard);
        } 
        elseif (in_array($text, ["/list", "/stats", "/post_now", "/clear"])) {
            sendMessage($chat_id, "⏳ Buyruq qabul qilindi...");
            $cmd = str_replace("/", "", $text);
            triggerGitHubAction("telegram_command", array("command" => $cmd));
        } 
        elseif ($text != "") {
            // Brainstorming yoki Link yuklab olish
            sendMessage($chat_id, "🧠 AI o'ylamoqda... / Link tekshirilmoqda...");
            triggerGitHubAction("telegram_command", array("command" => "brainstorm", "prompt" => $text));
        }
    }
}

// Yordamchi funksiyalar
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
    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    $result = curl_exec($ch);
    curl_close($ch);
    
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
