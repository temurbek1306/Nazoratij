<?php
// ==========================================
// TELEGRAM "PULT" BOTI - PHP WEBHOOK
// ==========================================

// Sozlamalar
$TELEGRAM_TOKEN = "8674470670:AAER3Y3EfZ44eFUhxKTpsGX_X_Vg6LvKYOQ";
$ADMIN_ID = 5701828462;
$GITHUB_PAT = "SIZNING_GITHUB_PAT_TOKENINGIZ"; // Buni GitHub'dan olasiz
$GITHUB_REPO = "temurbek1306/InstagaramAvtoReels";

// Kelayotgan ma'lumotni o'qish
$update = json_decode(file_get_contents('php://input'), TRUE);

if (isset($update['message'])) {
    $chat_id = $update['message']['chat']['id'];
    $message_id = $update['message']['message_id'];
    
    // XAVFSIZLIK: Faqatgina ADMIN (Siz) uchun ishlashi kerak
    if ($chat_id != $ADMIN_ID) {
        sendMessage($chat_id, "⛔️ Kechirasiz, siz ushbu botdan foydalanish huquqiga ega emassiz.");
        exit;
    }
    
    // Video kelganini tekshirish
    if (isset($update['message']['video'])) {
        $file_id = $update['message']['video']['file_id'];
        
        sendMessage($chat_id, "⏳ Video qabul qilindi! Yozishib olib, GitHub'ga tayyorlayapman...");
        
        // Telegram API orqali fayl manzilini olish
        $file_path = getFilePath($file_id);
        
        if ($file_path) {
            $video_url = "https://api.telegram.org/file/bot" . $TELEGRAM_TOKEN . "/" . $file_path;
            
            // GitHub Actions'ga buyruq yuborish
            $github_result = triggerGitHubAction($video_url);
            
            if ($github_result) {
                sendMessage($chat_id, "🚀 GitHub'ga buyruq berildi! \n\nHozir fonda videongiz Insta va YouTube ga joylanmoqda. Ish tugagach, sizga yakuniy xabar yuboraman.");
            } else {
                sendMessage($chat_id, "❌ GitHub'ga ulanishda xatolik yuz berdi. GITHUB_PAT yoki REPO nomini tekshiring.");
            }
        } else {
            sendMessage($chat_id, "❌ Videoni tortib olishda xatolik yuz berdi (Fayl hajmi 20MB dan oshmasligi kerak).");
        }
    } else {
        $text = isset($update['message']['text']) ? $update['message']['text'] : "";
        if ($text == "/start") {
            sendMessage($chat_id, "👋 Salom, Boss! Men sizning Avto Reels tizimingiz pultiman.\n\nMenga istalgan videoni (Reels/Shorts) tashlang, men uni darhol fon rejimida Instagram va YouTube ga joylayman!");
        } else {
            sendMessage($chat_id, "Iltimos, menga faqat video fayl yuboring.");
        }
    }
}

// Yordamchi funksiya: Telegramga xabar yozish
function sendMessage($chat_id, $text) {
    global $TELEGRAM_TOKEN;
    $url = "https://api.telegram.org/bot" . $TELEGRAM_TOKEN . "/sendMessage";
    $data = array(
        'chat_id' => $chat_id,
        'text' => $text
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
}

// Yordamchi funksiya: Faylning haqiqiy yuklab olish linkini olish
function getFilePath($file_id) {
    global $TELEGRAM_TOKEN;
    $url = "https://api.telegram.org/bot" . $TELEGRAM_TOKEN . "/getFile?file_id=" . $file_id;
    
    // curl orqali olish (xavfsizroq)
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

// Yordamchi funksiya: GitHub Actions'ni ishga tushirish (Webhook/Dispatch)
function triggerGitHubAction($video_url) {
    global $GITHUB_PAT, $GITHUB_REPO;
    
    $url = "https://api.github.com/repos/" . $GITHUB_REPO . "/dispatches";
    
    $data = array(
        "event_type" => "telegram_post",
        "client_payload" => array(
            "video_url" => $video_url
        )
    );
    
    $payload = json_encode($data);
    
    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_HTTPHEADER, array(
        'Accept: application/vnd.github.v3+json',
        'Authorization: Bearer ' . $GITHUB_PAT,
        'User-Agent: Telegram-PHP-Webhook',
        'Content-Type: application/json'
    ));
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $payload);
    
    $response = curl_exec($ch);
    $httpcode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    
    return ($httpcode >= 200 && $httpcode < 300);
}
?>
