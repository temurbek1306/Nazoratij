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
    if (isset($update['message']['video']) || isset($update['message']['document'])) {
        $video_obj = isset($update['message']['video']) ? $update['message']['video'] : $update['message']['document'];
        
        $file_size = isset($video_obj['file_size']) ? $video_obj['file_size'] : 0;
        
        // Telegram Bot API orqali faqat 20MB gacha bo'lgan fayllarni yuklab olish mumkin
        if ($file_size > 20000000) {
            sendMessage($chat_id, "❌ <b>Xatolik! Video hajmi juda katta.</b>\n\nTelegram Bot API faqat <b>20 MB</b> gacha bo'lgan fayllarni qabul qila oladi. Siz yuborgan video esa 20 MB dan oshib ketgan. Iltimos, kichikroq video yuboring yoki siqilgan holda jo'nating.");
            exit;
        }
        
        $file_id = $video_obj['file_id'];
        $file_path = getFilePath($file_id);
        
        if ($file_path) {
            $video_url = "https://api.telegram.org/file/bot" . $TELEGRAM_TOKEN . "/" . $file_path;
            
            if (file_exists("state.txt") && file_get_contents("state.txt") == "waiting_for_multiple_videos") {
                $current_group = "";
                if (file_exists("last_video_group.txt")) {
                    $current_group = file_get_contents("last_video_group.txt");
                }
                $current_group .= $video_url . "\n";
                file_put_contents("last_video_group.txt", $current_group);
                
                $count = count(array_filter(explode("\n", $current_group)));
                sendMessage($chat_id, "✅ $count-video qabul qilindi. Yana yuboring yoki pastdagi '✅ Birlashtirishni boshlash' tugmasini bosing.");
                exit;
            }
            
            // Videoni nomi sifatida caption ni olish (agar mavjud bo'lsa)
            $video_name_custom = "";
            if (isset($update['message']['caption'])) {
                $video_name_custom = preg_replace('/[^A-Za-z0-9_]/', '_', $update['message']['caption']);
                $video_name_custom = substr($video_name_custom, 0, 40);
                $video_name_custom = trim($video_name_custom, "_");
            }
            file_put_contents("last_custom_name.txt", $video_name_custom);
            
            // Fayl manzilini vaqtincha saqlab qo'yamiz (Tugma bosilganda o'qish uchun)
            file_put_contents("last_video.txt", $video_url);
            
            if ($video_name_custom == "") {
                file_put_contents("state.txt", "waiting_for_video_name");
                $keyboard = json_encode([
                    "inline_keyboard" => [
                        [["text" => "⏭ Nom bermasdan o'tkazib yuborish", "callback_data" => "skip_naming"]]
                    ]
                ]);
                sendMessage($chat_id, "🎬 Video qabul qilindi!\n\n✏️ Iltimos, bu videoga ixtiyoriy qisqa nom bering (keyingi yuborgan matningiz nom sifatida qabul qilinadi).", $keyboard);
            } else {
                $keyboard = get_platforms_keyboard($chat_id);
                sendMessage($chat_id, "🎬 Video qabul qilindi! Nomi: <b>$video_name_custom</b>\n\nQaysi tarmoqqa joylaymiz?", $keyboard);
            }
        } else {
            sendMessage($chat_id, "❌ Videoni qabul qilishda xatolik yuz berdi (Fayl hajmi juda katta bo'lishi mumkin).");
        }
        exit;
    }
    
    // Text commands
    $text = isset($update['message']['text']) ? $update['message']['text'] : "";
    
    // Videoga nom berish qismi
    if (file_exists("state.txt") && file_get_contents("state.txt") == "waiting_for_video_name" && $text != "") {
        if (strpos($text, "/") !== 0 && !in_array($text, ["☁️ Web-App orqali yuklash", "➕ Yangi Video Qo'shish", "🔖 Doimiy Hashteglar", "🚀 Hozir Joylash", "📊 Statistika", "📋 Navbat (Queue)", "🗑 Eski videolarni o'chirish", "⚙️ Vaqt Sozlamalari", "🔙 Ortga"])) {
            $video_name_custom = preg_replace('/[^A-Za-z0-9_]/', '_', $text);
            $video_name_custom = substr($video_name_custom, 0, 40);
            $video_name_custom = trim($video_name_custom, "_");
            
            file_put_contents("last_custom_name.txt", $video_name_custom);
            file_put_contents("state.txt", "none");
            
            if (file_exists("platforms_" . $chat_id . ".json")) unlink("platforms_" . $chat_id . ".json");
            $keyboard = get_platforms_keyboard($chat_id);
            sendMessage($chat_id, "✅ Videoga <b>$video_name_custom</b> deb nom berildi!\n\nQaysi tarmoqqa joylaymiz?", $keyboard);
            exit;
        }
    }
    
    // Qo'lda yozilgan izohni qabul qilish qismi
    if (file_exists("state.txt") && file_get_contents("state.txt") == "waiting_for_caption" && $text != "") {
        file_put_contents("last_caption.txt", $text);
        file_put_contents("state.txt", "none");
        
        $keyboard = json_encode([
            "inline_keyboard" => [
                [["text" => "📥 Navbat", "callback_data" => "act_queue_manual"]],
                [["text" => "🚀 Hozir", "callback_data" => "act_postnow_manual"]],
                [["text" => "⏱ Aniq vaqtga", "callback_data" => "act_schedule_manual"]]
            ]
        ]);
        sendMessage($chat_id, "✅ Ajoyib izoh qabul qilindi!\n\nVideoni nima qilamiz?", $keyboard);
        exit;
    }
    
    // Aniq vaqtni qabul qilish qismi
    if (file_exists("state.txt") && file_get_contents("state.txt") == "waiting_for_time" && $text != "") {
        file_put_contents("state.txt", "none");
        
        $time_str = trim($text);
        $timestamp = false;
        
        // Agar faqat soat yozilgan bo'lsa (Masalan: 19:30)
        if (preg_match('/^\d{1,2}:\d{2}$/', $time_str)) {
            $timestamp = strtotime(date("Y-m-d") . " " . $time_str);
            if ($timestamp < time()) {
                $timestamp += 86400; // O'tib ketgan bo'lsa ertasi kunga
            }
        } else {
            // Agar sana bilan yozilgan bo'lsa (Masalan: 25.07.2026 14:00)
            $dt = DateTime::createFromFormat('d.m.Y H:i', $time_str);
            if ($dt) {
                $timestamp = $dt->getTimestamp();
            } else {
                $timestamp = strtotime($time_str);
            }
        }
        
        if (!$timestamp || $timestamp < time() - 3600) {
            sendMessage($chat_id, "❌ Noto'g'ri vaqt formati yoki vaqt o'tib ketgan! Qaytadan yuboring.");
            exit;
        }
        
        if (file_exists("last_video.txt")) {
            $video_url = file_get_contents("last_video.txt");
            $caption = "";
            $mode = file_exists("schedule_mode.txt") ? file_get_contents("schedule_mode.txt") : "";
            
            if (strpos($mode, "_manual") !== false && file_exists("last_caption.txt")) {
                $caption = file_get_contents("last_caption.txt");
            }
            
            $custom_name = "";
            if (file_exists("last_custom_name.txt")) {
                $custom_name = file_get_contents("last_custom_name.txt");
            }
            
            $scheduled_file = "scheduled.json";
            $scheduled_list = [];
            if (file_exists($scheduled_file)) {
                $scheduled_list = json_decode(file_get_contents($scheduled_file), true) ?: [];
            }
            
            $platform = "both";
            if (file_exists("last_platform.txt")) {
                $platform = file_get_contents("last_platform.txt");
            }
            
            $is_artifact = false;
            $artifact_id = "";
            if (strpos($video_url, "artifact:") === 0) {
                $is_artifact = true;
                $artifact_id = str_replace("artifact:", "", $video_url);
                $video_url = "";
            }
            
            $scheduled_list[] = [
                "video_url" => $video_url,
                "artifact_run_id" => $artifact_id,
                "caption" => $caption,
                "custom_name" => $custom_name,
                "post_time" => $timestamp,
                "platform" => $platform
            ];
            
            file_put_contents($scheduled_file, json_encode($scheduled_list, JSON_PRETTY_PRINT));
            
            $formatted_time = date("d.m.Y H:i", $timestamp);
            sendMessage($chat_id, "✅ Video ro'yxatga olindi!\n\nVideo aynan <b>$formatted_time</b> da avtomatik tarzda joylanadi.");
        } else {
            sendMessage($chat_id, "❌ Video manzili topilmadi.");
        }
        
        exit;
    }
    
    // Video yaratish promptini qabul qilish
    if (file_exists("state.txt") && strpos(file_get_contents("state.txt"), "waiting_for_veo_prompt_") === 0 && $text != "") {
        $state_val = file_get_contents("state.txt");
        $ratio = str_replace("waiting_for_veo_prompt_", "", $state_val);
        
        file_put_contents("state.txt", "none");
        sendMessage($chat_id, "🎬 Video g'oyasi qabul qilindi! AI uni $ratio formatida yaratishni boshladi (2-3 daqiqa kuting)...");
        triggerGitHubAction("telegram_command", ["command" => "generate_video", "prompt" => $ratio . "|||" . $text]);
        exit;
    }



    // Doimiy hashteglarni qabul qilish
    if (file_exists("state.txt") && file_get_contents("state.txt") == "waiting_for_global_tags" && $text != "") {
        file_put_contents("state.txt", "none");
        sendMessage($chat_id, "⏳ GitHub serveriga yozilmoqda...");
        file_put_contents("viral_tags.txt", $text);
        updateGitHubFile($GITHUB_REPO, "viral_tags.txt", $text, $GITHUB_PAT);
        
        $main_keyboard_temp = json_encode([
            "keyboard" => [
                [["text" => "☁️ Web-App orqali yuklash"], ["text" => "➕ Yangi Video Qo'shish"]],
                [["text" => "🎞 Videolarni Birlashtirish"], ["text" => "🚀 Hozir Joylash"]],
                [["text" => "📋 Navbat (Queue)"], ["text" => "🔖 Doimiy Hashteglar"]],
                [["text" => "⚙️ Vaqt Sozlamalari"], ["text" => "📊 Statistika"]],
                [["text" => "🗑 Eski videolarni o'chirish"]]
            ],
            "resize_keyboard" => true,
            "one_time_keyboard" => false
        ]);
        
        sendMessage($chat_id, "✅ Muvaffaqiyatli saqlandi! Endi har bir videoning tagiga ushbu matn/hashteg avtomatik qo'shiladi.", $main_keyboard_temp);
        exit;
    }
    
    $main_keyboard = json_encode([
        "keyboard" => [
            [["text" => "☁️ Web-App orqali yuklash"], ["text" => "➕ Yangi Video Qo'shish"]],
            [["text" => "🎞 Videolarni Birlashtirish"], ["text" => "🚀 Hozir Joylash"]],
            [["text" => "📋 Navbat (Queue)"], ["text" => "🔖 Doimiy Hashteglar"]],
            [["text" => "⚙️ Vaqt Sozlamalari"], ["text" => "📊 Statistika"]],
            [["text" => "🗑 Eski videolarni o'chirish"]]
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
    elseif ($text == "☁️ Web-App orqali yuklash" || $text == "/upload") {
        $bot_url = "https://" . $_SERVER['HTTP_HOST'] . dirname($_SERVER['REQUEST_URI']);
        $webapp_url = rtrim($bot_url, '/') . "/upload.html";
        
        $webapp_keyboard = json_encode([
            "inline_keyboard" => [
                [
                    ["text" => "🌐 Katta Videoni Yuklash", "web_app" => ["url" => $webapp_url]]
                ]
            ]
        ]);
        sendMessage($chat_id, "☁️ <b>Maxsus Web-App ga xush kelibsiz!</b>\n\nTelegramning 20MB limitidan qochish uchun, pastdagi tugmani bosing va videoni to'g'ridan-to'g'ri serverga yuklang.", $webapp_keyboard);
    }
    elseif ($text == "🎞 Videolarni Birlashtirish") {
        file_put_contents("state.txt", "waiting_for_multiple_videos");
        file_put_contents("last_video_group.txt", ""); // clear existing
        $keyboard = json_encode([
            "keyboard" => [
                [["text" => "✅ Birlashtirishni boshlash"]],
                [["text" => "🔙 Ortga"]]
            ],
            "resize_keyboard" => true,
            "one_time_keyboard" => false
        ]);
        sendMessage($chat_id, "🎬 <b>Videolarni Birlashtirish rejimi yondi!</b>\n\nMenga birlashtirmoqchi bo'lgan videolaringizni ketma-ket yuboring (har birini jo'natib kutib turing).\n\nTugatgach, pastdagi tugmani bosing.", $keyboard);
    }
    elseif ($text == "✅ Birlashtirishni boshlash") {
        if (file_exists("state.txt") && file_get_contents("state.txt") == "waiting_for_multiple_videos") {
            $group = "";
            if (file_exists("last_video_group.txt")) {
                $group = file_get_contents("last_video_group.txt");
            }
            $videos = array_filter(explode("\n", $group));
            if (count($videos) < 2) {
                sendMessage($chat_id, "⚠️ Birlashtirish uchun kamida 2 ta video yuborishingiz kerak!");
                exit;
            }
            
            file_put_contents("state.txt", "none");
            sendMessage($chat_id, "⏳ <b>Birlashtirish jarayoni serverda boshlandi!</b>\nBu 2-3 daqiqa vaqt olishi mumkin. Tayyor bo'lgach, sizga prevyusini yuboraman.", $main_keyboard);
            
            triggerGitHubAction("telegram_command", array(
                "command" => "merge_videos",
                "prompt" => implode(",", $videos)
            ));
            exit;
        }
    }

    elseif ($text == "➕ Yangi Video Qo'shish") {
        sendMessage($chat_id, "📥 <b>Yangi video qo'shish</b>\n\nVideoni shunchaki Telegram botga yuboring (fayl yoki galereya orqali). Qolganini o'zim hal qilaman!");
    }
    elseif ($text == "🔖 Doimiy Hashteglar") {
        $mode = file_exists("hashtag_mode.txt") ? file_get_contents("hashtag_mode.txt") : "caption_and_tags";
        $mode_text = "";
        if ($mode == "caption_and_tags") $mode_text = "Izoh + Hashteglar";
        elseif ($mode == "tags_only") $mode_text = "Faqat Hashteglar";
        elseif ($mode == "off") $mode_text = "O'chirilgan";
        
        if (file_exists("viral_tags.txt")) {
            $current_tags = file_get_contents("viral_tags.txt");
        } else {
            $t = time();
            $current_tags = @file_get_contents("https://raw.githubusercontent.com/temurbek1306/InstagaramAvtoReels/main/viral_tags.txt?t=$t");
            if (!$current_tags) $current_tags = "Hozircha bo'sh.";
        }
        
        $keyboard = json_encode([
            "inline_keyboard" => [
                [["text" => "✍️ Hashteglarni o'zgartirish", "callback_data" => "edit_global_tags"]],
                [["text" => ($mode == "caption_and_tags" ? "✅ " : "") . "Izoh + Hashteglar", "callback_data" => "hmod_caption_and_tags"]],
                [["text" => ($mode == "tags_only" ? "✅ " : "") . "Faqat Hashteglar", "callback_data" => "hmod_tags_only"]],
                [["text" => ($mode == "off" ? "✅ " : "") . "❌ O'chirib qo'yish", "callback_data" => "hmod_off"]]
            ]
        ]);
        $msg = "🔖 <b>Doimiy Hashteglar Sozlamasi</b>\n\n⚙️ Hozirgi rejim: <b>$mode_text</b>\n\n📝 <b>Joriy saqlangan hashteglar:</b>\n<pre>$current_tags</pre>\n\n👇 <i>Qanday ishlashini tanlang:</i>";
        sendMessage($chat_id, $msg, $keyboard);
    }
    elseif ($text == "🚀 Hozir Joylash") {
        $keyboard = json_encode([
            "inline_keyboard" => [
                [["text" => "✅ Ha, Hozir joylash", "callback_data" => "confirm_postnow"]],
                [["text" => "❌ Yo'q, bekor qilish", "callback_data" => "confirm_cancel"]]
            ]
        ]);
        sendMessage($chat_id, "⚠️ <b>Diqqat!</b>\n\nRostdan ham navbatdagi videoni hoziroq tarmoqlarga joylamoqchimisiz?", $keyboard);
    }
    elseif ($text == "📊 Statistika" || $text == "/stats") {
        sendMessage($chat_id, "⏳ Statistika yig'ilmoqda...");
        triggerGitHubAction("telegram_command", array("command" => "stats"));
    }
    elseif ($text == "📋 Navbat (Queue)" || $text == "/list") {
        
        $scheduled_msg = "";
        if (file_exists("scheduled.json")) {
            $scheduled_videos = json_decode(file_get_contents("scheduled.json"), true) ?: [];
            if (count($scheduled_videos) > 0) {
                $scheduled_msg = "⏱ <b>Aniq vaqtga belgilangan videolar:</b>\n\n";
                $keyboard_buttons = [];
                $row = [];
                foreach ($scheduled_videos as $i => $sv) {
                    $time = date("d.m.Y H:i", $sv['post_time']);
                    $scheduled_msg .= ($i+1) . ". 🕰 <b>$time</b> da chiqadi\n";
                    $row[] = ["text" => "🗑 " . ($i+1), "callback_data" => "delsched_" . $i];
                    if (count($row) == 5) {
                        $keyboard_buttons[] = $row;
                        $row = [];
                    }
                }
                if (!empty($row)) {
                    $keyboard_buttons[] = $row;
                }
                $reply_markup = json_encode(["inline_keyboard" => $keyboard_buttons]);
                sendMessage($chat_id, $scheduled_msg, $reply_markup);
            }
        }
        
        sendMessage($chat_id, "⏳ Oddiy navbat hisoblanmoqda...");
        
        $config_file = 'config.json';
        $interval = 2;
        $last_run = 0;
        if (file_exists($config_file)) {
            $config = json_decode(file_get_contents($config_file), true);
            $interval = isset($config['interval_hours']) ? $config['interval_hours'] : 2;
            $last_run = isset($config['last_run']) ? $config['last_run'] : 0;
        }
        
        triggerGitHubAction("telegram_command", array(
            "command" => "list", 
            "interval" => $interval,
            "last_run" => $last_run
        ));
    }
    elseif ($text == "🗑 Eski videolarni o'chirish" || $text == "/clear") {
        $keyboard = json_encode([
            "inline_keyboard" => [
                [["text" => "⚠️ Ha, Hammasini o'chirish", "callback_data" => "confirm_clear"]],
                [["text" => "❌ Yo'q, bekor qilish", "callback_data" => "confirm_cancel"]]
            ]
        ]);
        sendMessage($chat_id, "⚠️ <b>Diqqat! Xavfli amaliyot!</b>\n\nRostdan ham barcha eski va joylangan videolarni serverdan o'chirib yubormoqchimisiz?", $keyboard);
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

// ==========================================
// CALLBACK QUERIES (Tugmalar bosilganda)
// ==========================================
if (isset($update['callback_query'])) {
    $chat_id = $update['callback_query']['message']['chat']['id'];
    
    if ($chat_id != $ADMIN_ID) {
        sendMessage($chat_id, "⛔️ Kechirasiz, siz ushbu botdan foydalanish huquqiga ega emassiz.");
        exit;
    }
    
    $data = $update['callback_query']['data'];
    $message_id = $update['callback_query']['message']['message_id'];
    
    if ($data == "start_merging") {
        if (file_exists("state.txt") && file_get_contents("state.txt") == "waiting_for_multiple_videos") {
            $group = "";
            if (file_exists("last_video_group.txt")) {
                $group = file_get_contents("last_video_group.txt");
            }
            $videos = array_filter(explode("\n", $group));
            if (count($videos) < 2) {
                sendMessage($chat_id, "⚠️ Birlashtirish uchun kamida 2 ta video yuborishingiz kerak!");
                exit;
            }
            
            file_put_contents("state.txt", "none");
            
            $url = "https://api.telegram.org/bot" . $TELEGRAM_TOKEN . "/editMessageReplyMarkup";
            file_get_contents($url . "?chat_id=$chat_id&message_id=$message_id&reply_markup=" . urlencode(json_encode(["inline_keyboard" => []])));
            
            sendMessage($chat_id, "⏳ <b>Birlashtirish jarayoni serverda boshlandi!</b>\nBu 2-3 daqiqa vaqt olishi mumkin. Tayyor bo'lgach, sizga prevyusini yuboraman.");
            
            triggerGitHubAction("telegram_command", array(
                "command" => "merge_videos",
                "prompt" => implode(",", $videos)
            ));
            exit;
        }
    }
    
    if (strpos($data, "approve_merged_") === 0) {
        $run_id = str_replace("approve_merged_", "", $data);
        file_put_contents("last_video.txt", "artifact:" . $run_id);
        file_put_contents("state.txt", "waiting_for_video_name");
        
        $url = "https://api.telegram.org/bot" . $TELEGRAM_TOKEN . "/editMessageReplyMarkup";
        file_get_contents($url . "?chat_id=$chat_id&message_id=$message_id&reply_markup=" . urlencode(json_encode(["inline_keyboard" => []])));
        
        $keyboard = json_encode([
            "inline_keyboard" => [
                [["text" => "⏭ Nom bermasdan o'tkazib yuborish", "callback_data" => "skip_naming"]]
            ]
        ]);
        sendMessage($chat_id, "✅ Video tasdiqlandi!\n\n✏️ Iltimos, bu videoga ixtiyoriy qisqa nom bering:", $keyboard);
        exit;
    }
    
    if (strpos($data, "delete_merged_") === 0) {
        $url = "https://api.telegram.org/bot" . $TELEGRAM_TOKEN . "/editMessageReplyMarkup";
        file_get_contents($url . "?chat_id=$chat_id&message_id=$message_id&reply_markup=" . urlencode(json_encode(["inline_keyboard" => []])));
        
        sendMessage($chat_id, "🗑 Video bekor qilindi va o'chirildi.");
        exit;
    }
    
    if ($data == "skip_naming") {
        file_put_contents("state.txt", "none");
        if (file_exists("platforms_" . $chat_id . ".json")) unlink("platforms_" . $chat_id . ".json");
        $keyboard = get_platforms_keyboard($chat_id);
        sendMessage($chat_id, "✅ Faylga avtomatik nom beriladi.\n\nQaysi tarmoqqa joylaymiz?", $keyboard);
        $url = "https://api.telegram.org/bot" . $TELEGRAM_TOKEN . "/editMessageReplyMarkup";
        file_get_contents($url . "?chat_id=$chat_id&message_id=$message_id&reply_markup=" . urlencode(json_encode(["inline_keyboard" => []])));
        exit;
    }
    
    // Toggle handling
    if (strpos($data, "toggle_") === 0) {
        $key = str_replace("toggle_", "", $data);
        $state_file = "platforms_" . $chat_id . ".json";
        $platforms = json_decode(file_get_contents($state_file), true);
        $platforms[$key] = !$platforms[$key];
        file_put_contents($state_file, json_encode($platforms));
        
        $keyboard = get_platforms_keyboard($chat_id);
        $url = "https://api.telegram.org/bot" . $TELEGRAM_TOKEN . "/editMessageReplyMarkup";
        file_get_contents($url . "?chat_id=$chat_id&message_id=$message_id&reply_markup=" . urlencode($keyboard));
        exit;
    }
    
    // Confirm handling
    if ($data == "platform_confirm") {
        $state_file = "platforms_" . $chat_id . ".json";
        $platforms = json_decode(file_get_contents($state_file), true);
        
        $selected = [];
        foreach($platforms as $k => $v) {
            if ($v) $selected[] = $k;
        }
        
        if (empty($selected)) {
            $url = "https://api.telegram.org/bot" . $TELEGRAM_TOKEN . "/answerCallbackQuery";
            file_get_contents($url . "?callback_query_id=" . $update['callback_query']['id'] . "&text=" . urlencode("Hech bo'lmasa 1 ta tarmoqni tanlang!") . "&show_alert=true");
            exit;
        }
        
        file_put_contents("last_platform.txt", implode(",", $selected));
        
        $keyboard = json_encode([
            "inline_keyboard" => [
                [
                    ["text" => "🤖 AI O'zi yozsin", "callback_data" => "video_ai"],
                    ["text" => "✍️ O'zim yozaman", "callback_data" => "video_manual"]
                ]
            ]
        ]);
        sendMessage($chat_id, "✅ Tarmoqlar tasdiqlandi!

Endi izohni kim yozadi?", $keyboard);
        $url = "https://api.telegram.org/bot" . $TELEGRAM_TOKEN . "/editMessageReplyMarkup";
        file_get_contents($url . "?chat_id=$chat_id&message_id=$message_id&reply_markup=" . urlencode(json_encode(["inline_keyboard" => []])));
        exit;
    }
    
    if ($data == "video_ai") {
        file_put_contents("state.txt", "none");
        $keyboard = json_encode([
            "inline_keyboard" => [
                [["text" => "📥 Navbat", "callback_data" => "act_queue_ai"]],
                [["text" => "🚀 Hozir", "callback_data" => "act_postnow_ai"]],
                [["text" => "⏱ Aniq vaqtga", "callback_data" => "act_schedule_ai"]]
            ]
        ]);
        sendMessage($chat_id, "🤖 AI yozishga tayyor!\n\nVideoni nima qilamiz?", $keyboard);
        $url = "https://api.telegram.org/bot" . $TELEGRAM_TOKEN . "/editMessageReplyMarkup";
        file_get_contents($url . "?chat_id=$chat_id&message_id=$message_id&reply_markup=" . urlencode(json_encode(["inline_keyboard" => []])));
        exit;
    }
    
    if ($data == "video_manual") {
        file_put_contents("state.txt", "waiting_for_caption");
        sendMessage($chat_id, "✍️ Iltimos, video uchun izohni (caption) jo'nating.\n\n*(Keyingi xabaringiz to'g'ridan-to'g'ri izoh sifatida qabul qilinadi)*");
        $url = "https://api.telegram.org/bot" . $TELEGRAM_TOKEN . "/editMessageReplyMarkup";
        file_get_contents($url . "?chat_id=$chat_id&message_id=$message_id&reply_markup=" . urlencode(json_encode(["inline_keyboard" => []])));
        exit;
    }
    
    if (strpos($data, "act_schedule_") === 0) {
        file_put_contents("state.txt", "waiting_for_time");
        file_put_contents("schedule_mode.txt", $data); // act_schedule_manual or act_schedule_ai
        
        $msg = "⏱ <b>Videoni qachon joylaymiz?</b>\n\n";
        $msg .= "Quyidagi formatlardan birida yozing:\n";
        $msg .= "• Bugun uchun faqat soat: <b>19:30</b>\n";
        $msg .= "• Boshqa kun uchun: <b>25.07.2026 14:00</b>\n\n";
        $msg .= "<i>Iltimos, vaqtni kiriting:</i>";
        
        sendMessage($chat_id, $msg);
        $url = "https://api.telegram.org/bot" . $TELEGRAM_TOKEN . "/editMessageReplyMarkup";
        file_get_contents($url . "?chat_id=$chat_id&message_id=$message_id&reply_markup=" . urlencode(json_encode(["inline_keyboard" => []])));
        exit;
    }
    
    if (strpos($data, "act_queue_") === 0 || strpos($data, "act_postnow_") === 0) {
        if (file_exists("last_video.txt")) {
            $video_url = file_get_contents("last_video.txt");
            $caption = "";
            
            if (strpos($data, "_manual") !== false && file_exists("last_caption.txt")) {
                $caption = file_get_contents("last_caption.txt");
            }
            
            $custom_name = "";
            if (file_exists("last_custom_name.txt")) {
                $custom_name = file_get_contents("last_custom_name.txt");
            }
            
            $platform = "both";
            if (file_exists("last_platform.txt")) {
                $platform = file_get_contents("last_platform.txt");
            }
            
            $is_artifact = false;
            $artifact_id = "";
            if (strpos($video_url, "artifact:") === 0) {
                $is_artifact = true;
                $artifact_id = str_replace("artifact:", "", $video_url);
                $video_url = ""; // Don't send as url
            }
            
            if (strpos($data, "act_queue") === 0) {
                sendMessage($chat_id, "✅ Video navbatga qo'shilmoqda... (Background processing)");
                triggerGitHubAction("telegram_queue", array(
                    "video_url" => $video_url,
                    "artifact_run_id" => $artifact_id,
                    "caption" => $caption,
                    "custom_name" => $custom_name,
                    "platform" => $platform
                ));
            } else {
                sendMessage($chat_id, "🚀 Video hoziroq tarmoqlarga joylanmoqda! (Kuting...)");
                triggerGitHubAction("telegram_post", array(
                    "video_url" => $video_url,
                    "artifact_run_id" => $artifact_id,
                    "caption" => $caption,
                    "custom_name" => $custom_name,
                    "platform" => $platform
                ));
            }
            
            // Takror bosilmasligi uchun tugmalarni o'chirib tashlash
            $url = "https://api.telegram.org/bot" . $TELEGRAM_TOKEN . "/editMessageReplyMarkup";
            file_get_contents($url . "?chat_id=$chat_id&message_id=$message_id&reply_markup=" . urlencode(json_encode(["inline_keyboard" => []])));
        } else {
            sendMessage($chat_id, "❌ Video manzili topilmadi. Qaytadan yuboring.");
        }
        exit;
    }
    elseif (strpos($data, "post_a_") === 0 || strpos($data, "post_b_") === 0 || strpos($data, "post_c_") === 0 || strpos($data, "cancel_") === 0) {
        // A, B, C matnlari tanlanganda yoki Bekor qilinganda
        triggerGitHubAction("telegram_command", array("command" => $data));
        
        file_get_contents($url . "?chat_id=$chat_id&message_id=$message_id&reply_markup=" . urlencode(json_encode(["inline_keyboard" => []])));
        exit;
    }

    elseif (strpos($data, "hmod_") === 0) {
        $mode = str_replace("hmod_", "", $data);
        file_put_contents("hashtag_mode.txt", $mode);
        updateGitHubFile($GITHUB_REPO, "hashtag_mode.txt", $mode, $GITHUB_PAT);
        
        $mode_text = "";
        if ($mode == "caption_and_tags") $mode_text = "Izoh + Hashteglar";
        elseif ($mode == "tags_only") $mode_text = "Faqat Hashteglar";
        elseif ($mode == "off") $mode_text = "O'chirilgan";
        
        if (file_exists("viral_tags.txt")) {
            $current_tags = file_get_contents("viral_tags.txt");
        } else {
            $t = time();
            $current_tags = @file_get_contents("https://raw.githubusercontent.com/temurbek1306/InstagaramAvtoReels/main/viral_tags.txt?t=$t");
            if (!$current_tags) $current_tags = "Hozircha bo'sh.";
        }
        
        $keyboard = json_encode([
            "inline_keyboard" => [
                [["text" => "✍️ Hashteglarni o'zgartirish", "callback_data" => "edit_global_tags"]],
                [["text" => ($mode == "caption_and_tags" ? "✅ " : "") . "Izoh + Hashteglar", "callback_data" => "hmod_caption_and_tags"]],
                [["text" => ($mode == "tags_only" ? "✅ " : "") . "Faqat Hashteglar", "callback_data" => "hmod_tags_only"]],
                [["text" => ($mode == "off" ? "✅ " : "") . "❌ O'chirib qo'yish", "callback_data" => "hmod_off"]]
            ]
        ]);
        
        $url = "https://api.telegram.org/bot" . $TELEGRAM_TOKEN . "/editMessageText";
        $msg = "🔖 <b>Doimiy Hashteglar Sozlamasi</b>

⚙️ Hozirgi rejim: <b>$mode_text</b>

📝 <b>Joriy saqlangan hashteglar:</b>
<pre>$current_tags</pre>

👇 <i>Qanday ishlashini tanlang:</i>";
        file_get_contents($url . "?chat_id=$chat_id&message_id=$message_id&text=" . urlencode($msg) . "&parse_mode=HTML&reply_markup=" . urlencode($keyboard));
        
        $url_ans = "https://api.telegram.org/bot" . $TELEGRAM_TOKEN . "/answerCallbackQuery";
        file_get_contents($url_ans . "?callback_query_id=" . $update['callback_query']['id'] . "&text=" . urlencode("Saqlandi!"));
        exit;
    }
    elseif ($data == "edit_global_tags") {
        file_put_contents("state.txt", "waiting_for_global_tags");
        
        if (file_exists("viral_tags.txt")) {
            $current_tags = file_get_contents("viral_tags.txt");
        } else {
            $t = time();
            $current_tags = @file_get_contents("https://raw.githubusercontent.com/temurbek1306/InstagaramAvtoReels/main/viral_tags.txt?t=$t");
            if (!$current_tags) $current_tags = "Hozircha bo'sh.";
        }
        
        $msg = "🔖 <b>Doimiy Matn/Hashteglar</b>

Bu yerda yozgan har qanday matningiz videolarga qo'shiladi.

📝 <b>Hozirgi saqlangan matn:</b>
<pre>$current_tags</pre>

🔄 <b>Navbatma-navbat ishlashi uchun:</b>
Agar siz bir nechta xil hashteglarni navbat bilan (1-videoga 1-hashteg, 2-videoga 2-hashteg) chiqishini xohlasangiz, ularni <b>===</b> belgisi bilan ajrating.
Masalan:
#kulgili #rek
===
#uzb #trend

👇 <i>Yangi doimiy matnni yuboring (Diqqat: yangisini yuborsangiz, eskisi butunlay o'chib ketadi!):</i>";
        sendMessage($chat_id, $msg);
        
        $url_ans = "https://api.telegram.org/bot" . $TELEGRAM_TOKEN . "/answerCallbackQuery";
        file_get_contents($url_ans . "?callback_query_id=" . $update['callback_query']['id']);
        exit;
    }
    elseif (strpos($data, "del_") === 0) {
        // O'chirish komandasini yuboramiz
        triggerGitHubAction("telegram_command", array("command" => $data));
        
        // Callback'ga vizual javob
        $url = "https://api.telegram.org/bot" . $TELEGRAM_TOKEN . "/answerCallbackQuery";
        file_get_contents($url . "?callback_query_id=" . $update['callback_query']['id'] . "&text=" . urlencode("⏳ O'chirish jarayoni boshlandi..."));
        exit;
    }
    elseif (strpos($data, "delsched_") === 0) {
        $index = (int) str_replace("delsched_", "", $data);
        $scheduled_file = "scheduled.json";
        if (file_exists($scheduled_file)) {
            $scheduled_videos = json_decode(file_get_contents($scheduled_file), true) ?: [];
            if (isset($scheduled_videos[$index])) {
                array_splice($scheduled_videos, $index, 1);
                file_put_contents($scheduled_file, json_encode($scheduled_videos, JSON_PRETTY_PRINT));
                sendMessage($chat_id, "✅ Aniq vaqtli video (T/r: " . ($index+1) . ") navbatdan o'chirildi!");
                
                $url = "https://api.telegram.org/bot" . $TELEGRAM_TOKEN . "/answerCallbackQuery";
                file_get_contents($url . "?callback_query_id=" . $update['callback_query']['id'] . "&text=" . urlencode("O'chirildi!"));
                
                // Takror bosilmasligi uchun tugmalarni o'chirib tashlash
                $url = "https://api.telegram.org/bot" . $TELEGRAM_TOKEN . "/editMessageReplyMarkup";
                file_get_contents($url . "?chat_id=$chat_id&message_id=$message_id&reply_markup=" . urlencode(json_encode(["inline_keyboard" => []])));
                exit;
            }
        }
        $url = "https://api.telegram.org/bot" . $TELEGRAM_TOKEN . "/answerCallbackQuery";
        file_get_contents($url . "?callback_query_id=" . $update['callback_query']['id'] . "&text=" . urlencode("Topilmadi!"));
        exit;
    }
    elseif ($data == "confirm_postnow") {
        sendMessage($chat_id, "🚀 <b>Videoni joylash jarayoni boshlandi!</b>\n\nNavbatdagi (Pending) video hozir tarmoqlarga joylanadi (1-2 daqiqa kuting).");
        triggerGitHubAction("telegram_post", array("video_url" => ""));
        $url = "https://api.telegram.org/bot" . $TELEGRAM_TOKEN . "/editMessageReplyMarkup";
        file_get_contents($url . "?chat_id=$chat_id&message_id=$message_id&reply_markup=" . urlencode(json_encode(["inline_keyboard" => []])));
        exit;
    }
    elseif ($data == "confirm_clear") {
        sendMessage($chat_id, "⏳ Tozalanmoqda...");
        triggerGitHubAction("telegram_command", array("command" => "clear"));
        $url = "https://api.telegram.org/bot" . $TELEGRAM_TOKEN . "/editMessageReplyMarkup";
        file_get_contents($url . "?chat_id=$chat_id&message_id=$message_id&reply_markup=" . urlencode(json_encode(["inline_keyboard" => []])));
        exit;
    }
    elseif ($data == "confirm_cancel") {
        $url = "https://api.telegram.org/bot" . $TELEGRAM_TOKEN . "/editMessageText";
        file_get_contents($url . "?chat_id=$chat_id&message_id=$message_id&text=" . urlencode("❌ Amaliyot bekor qilindi."));
        exit;
    }
    elseif (strpos($data, "veoratio_") === 0) {
        $ratio = str_replace("veoratio_", "", $data);
        file_put_contents("state.txt", "waiting_for_veo_prompt_" . $ratio);
        
        $msg = "✅ Format tanlandi: <b>$ratio</b>\n\nEndi videoda nimalar sodir bo'lishini xohlaysiz? Qisqacha (ingliz tilida yozsangiz yaxshiroq tushunadi) yoki o'zbekcha yozing:\n\n<i>Masalan: A futuristic cyberpunk city at night with neon lights and a flying car, cinematic 4k</i>";
        
        $url = "https://api.telegram.org/bot" . $TELEGRAM_TOKEN . "/editMessageText";
        file_get_contents($url . "?chat_id=$chat_id&message_id=$message_id&text=" . urlencode($msg) . "&parse_mode=HTML");
        exit;
    }
}

// ==========================
// YORDAMCHI FUNKSIYALAR
// ==========================

function setupBotCommands() {
    global $TELEGRAM_TOKEN;
    $url = "https://api.telegram.org/bot" . $TELEGRAM_TOKEN . "/setMyCommands";
    $commands = [
        ["command" => "start", "description" => "Asosiy menyuni ochish"]
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

// --- Tarmoqlarni tanlash klaviaturasi ---
function get_platforms_keyboard($chat_id) {
    $state_file = "platforms_" . $chat_id . ".json";
    if (!file_exists($state_file)) {
        // Default: all enabled (No TikTok)
        $platforms = ["ig" => true, "yt" => true, "tg" => true, "fb" => true];
        file_put_contents($state_file, json_encode($platforms));
    } else {
        $platforms = json_decode(file_get_contents($state_file), true);
    }
    
    $btn_ig = ($platforms['ig'] ? "✅" : "❌") . " Instagram";
    $btn_yt = ($platforms['yt'] ? "✅" : "❌") . " YouTube";
    $btn_tg = ($platforms['tg'] ? "✅" : "❌") . " Telegram";
    $btn_fb = ($platforms['fb'] ? "✅" : "❌") . " Facebook";
    
    $keyboard = json_encode([
        "inline_keyboard" => [
            [["text" => $btn_ig, "callback_data" => "toggle_ig"], ["text" => $btn_yt, "callback_data" => "toggle_yt"]],
            [["text" => $btn_tg, "callback_data" => "toggle_tg"], ["text" => $btn_fb, "callback_data" => "toggle_fb"]],
            [["text" => "▶️ TASDIQLASH (Davom etish)", "callback_data" => "platform_confirm"]]
        ]
    ]);
    return $keyboard;
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
    curl_close($ch);
    return json_decode($response, TRUE);
}

function updateGitHubFile($repo, $path, $content, $token) {
    $url = "https://api.github.com/repos/$repo/contents/$path";
    
    // 1. Get current SHA
    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_HTTPHEADER, ['User-Agent: PHP-Bot', "Authorization: Bearer $token"]);
    $res = curl_exec($ch);
    $data = json_decode($res, true);
    $sha = isset($data['sha']) ? $data['sha'] : null;
    curl_close($ch);
    
    // 2. Put new content
    $put_data = [
        "message" => "Update viral tags via bot",
        "content" => base64_encode($content)
    ];
    if ($sha) $put_data["sha"] = $sha;
    
    $ch2 = curl_init($url);
    curl_setopt($ch2, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch2, CURLOPT_CUSTOMREQUEST, "PUT");
    curl_setopt($ch2, CURLOPT_POSTFIELDS, json_encode($put_data));
    curl_setopt($ch2, CURLOPT_HTTPHEADER, ['User-Agent: PHP-Bot', "Authorization: Bearer $token", 'Content-Type: application/json']);
    curl_exec($ch2);
    curl_close($ch2);
}
?>
