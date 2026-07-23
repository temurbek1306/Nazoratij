import os

content = open('php_bot/bot.php', 'r', encoding='utf-8').read()

search_1 = """    elseif ($text == "🔖 Doimiy Hashteglar") {
        file_put_contents("state.txt", "waiting_for_global_tags");
        $msg = "🔖 <b>Doimiy Matn/Hashteglar</b>\n\nBu yerda yozgan har qanday matningiz (masalan, Yaponcha yozuv yoki hashteglar) har bir poistingiz oxiriga avtomatik qistiriladi.\n\n👇 <i>Yangi doimiy matnni yuboring:</i>";
        sendMessage($chat_id, $msg);
    }"""

replace_1 = """    elseif ($text == "🔖 Doimiy Hashteglar") {
        $mode = file_exists("hashtag_mode.txt") ? file_get_contents("hashtag_mode.txt") : "caption_and_tags";
        $mode_text = "";
        if ($mode == "caption_and_tags") $mode_text = "Izoh + Hashteglar";
        elseif ($mode == "tags_only") $mode_text = "Faqat Hashteglar";
        elseif ($mode == "off") $mode_text = "O'chirilgan";
        
        $keyboard = json_encode([
            "inline_keyboard" => [
                [["text" => "✍️ Hashteglarni o'zgartirish", "callback_data" => "edit_global_tags"]],
                [["text" => ($mode == "caption_and_tags" ? "✅ " : "") . "Izoh + Hashteglar", "callback_data" => "hmod_caption_and_tags"]],
                [["text" => ($mode == "tags_only" ? "✅ " : "") . "Faqat Hashteglar", "callback_data" => "hmod_tags_only"]],
                [["text" => ($mode == "off" ? "✅ " : "") . "❌ O'chirib qo'yish", "callback_data" => "hmod_off"]]
            ]
        ]);
        sendMessage($chat_id, "🔖 <b>Doimiy Hashteglar Sozlamasi</b>\n\nHozirgi holat: <b>$mode_text</b>\n\nQanday ishlashini tanlang:", $keyboard);
    }"""

search_2 = """    elseif (strpos($data, "post_a_") === 0 || strpos($data, "post_b_") === 0 || strpos($data, "post_c_") === 0 || strpos($data, "cancel_") === 0) {
        // A, B, C matnlari tanlanganda yoki Bekor qilinganda
        triggerGitHubAction("telegram_command", array("command" => $data));
        
        // Takror bosilmasligi uchun tugmalarni o'chirib tashlash
        $url = "https://api.telegram.org/bot" . $TELEGRAM_TOKEN . "/editMessageReplyMarkup";
        file_get_contents($url . "?chat_id=$chat_id&message_id=$message_id&reply_markup=" . json_encode(["inline_keyboard" => []]));
    }"""

replace_2 = """    elseif (strpos($data, "post_a_") === 0 || strpos($data, "post_b_") === 0 || strpos($data, "post_c_") === 0 || strpos($data, "cancel_") === 0) {
        triggerGitHubAction("telegram_command", array("command" => $data));
        $url = "https://api.telegram.org/bot" . $TELEGRAM_TOKEN . "/editMessageReplyMarkup";
        file_get_contents($url . "?chat_id=$chat_id&message_id=$message_id&reply_markup=" . json_encode(["inline_keyboard" => []]));
    }
    elseif (strpos($data, "hmod_") === 0) {
        $mode = str_replace("hmod_", "", $data);
        file_put_contents("hashtag_mode.txt", $mode);
        updateGitHubFile($GITHUB_REPO, "hashtag_mode.txt", $mode, $GITHUB_PAT);
        
        $mode_text = "";
        if ($mode == "caption_and_tags") $mode_text = "Izoh + Hashteglar";
        elseif ($mode == "tags_only") $mode_text = "Faqat Hashteglar";
        elseif ($mode == "off") $mode_text = "O'chirilgan";
        
        $keyboard = json_encode([
            "inline_keyboard" => [
                [["text" => "✍️ Hashteglarni o'zgartirish", "callback_data" => "edit_global_tags"]],
                [["text" => ($mode == "caption_and_tags" ? "✅ " : "") . "Izoh + Hashteglar", "callback_data" => "hmod_caption_and_tags"]],
                [["text" => ($mode == "tags_only" ? "✅ " : "") . "Faqat Hashteglar", "callback_data" => "hmod_tags_only"]],
                [["text" => ($mode == "off" ? "✅ " : "") . "❌ O'chirib qo'yish", "callback_data" => "hmod_off"]]
            ]
        ]);
        
        $url = "https://api.telegram.org/bot" . $TELEGRAM_TOKEN . "/editMessageText";
        $msg = "🔖 <b>Doimiy Hashteglar Sozlamasi</b>\n\nHozirgi holat: <b>$mode_text</b>\n\nQanday ishlashini tanlang:";
        file_get_contents($url . "?chat_id=$chat_id&message_id=$message_id&text=" . urlencode($msg) . "&parse_mode=HTML&reply_markup=" . $keyboard);
        exit;
    }
    elseif ($data == "edit_global_tags") {
        file_put_contents("state.txt", "waiting_for_global_tags");
        $msg = "🔖 <b>Doimiy Matn/Hashteglar</b>\n\nBu yerda yozgan har qanday matningiz poistingizga qo'shiladi.\n\n👇 <i>Yangi doimiy matnni yuboring:</i>";
        sendMessage($chat_id, $msg);
        exit;
    }"""

content = content.replace(search_1, replace_1)
content = content.replace(search_2, replace_2)

open('php_bot/bot.php', 'w', encoding='utf-8').write(content)
print("bot.php updated.")
