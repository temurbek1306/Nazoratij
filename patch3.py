import os

content = open('php_bot/bot.php', 'r', encoding='utf-8').read()

search_1 = """    elseif ($text == "🔖 Doimiy Hashteglar") {
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

replace_1 = """    elseif ($text == "🔖 Doimiy Hashteglar") {
        $mode = file_exists("hashtag_mode.txt") ? file_get_contents("hashtag_mode.txt") : "caption_and_tags";
        $mode_text = "";
        if ($mode == "caption_and_tags") $mode_text = "Izoh + Hashteglar";
        elseif ($mode == "tags_only") $mode_text = "Faqat Hashteglar";
        elseif ($mode == "off") $mode_text = "O'chirilgan";
        
        $t = time();
        $current_tags = @file_get_contents("https://raw.githubusercontent.com/temurbek1306/InstagaramAvtoReels/main/viral_tags.txt?t=$t");
        if (!$current_tags) $current_tags = "Hozircha bo'sh.";
        
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
    }"""

search_2 = """    elseif ($data == "edit_global_tags") {
        file_put_contents("state.txt", "waiting_for_global_tags");
        $msg = "🔖 <b>Doimiy Matn/Hashteglar</b>\n\nBu yerda yozgan har qanday matningiz videolarga qo'shiladi.\n\n🔄 <b>Navbatma-navbat ishlashi uchun:</b>\nAgar siz bir nechta xil hashteglarni navbat bilan (1-videoga 1-hashteg, 2-videoga 2-hashteg) chiqishini xohlasangiz, ularni <b>===</b> belgisi bilan ajrating.\nMasalan:\n#kulgili #rek\n===\n#uzb #trend\n\n👇 <i>Yangi doimiy matnni yuboring:</i>";
        sendMessage($chat_id, $msg);
        exit;
    }"""

replace_2 = """    elseif ($data == "edit_global_tags") {
        file_put_contents("state.txt", "waiting_for_global_tags");
        
        $t = time();
        $current_tags = @file_get_contents("https://raw.githubusercontent.com/temurbek1306/InstagaramAvtoReels/main/viral_tags.txt?t=$t");
        if (!$current_tags) $current_tags = "Hozircha bo'sh.";
        
        $msg = "🔖 <b>Doimiy Matn/Hashteglar</b>\n\nBu yerda yozgan har qanday matningiz videolarga qo'shiladi.\n\n📝 <b>Hozirgi saqlangan matn:</b>\n<pre>$current_tags</pre>\n\n🔄 <b>Navbatma-navbat ishlashi uchun:</b>\nAgar siz bir nechta xil hashteglarni navbat bilan (1-videoga 1-hashteg, 2-videoga 2-hashteg) chiqishini xohlasangiz, ularni <b>===</b> belgisi bilan ajrating.\nMasalan:\n#kulgili #rek\n===\n#uzb #trend\n\n👇 <i>Yangi doimiy matnni yuboring (Diqqat: yangisini yuborsangiz, eskisi butunlay o'chib ketadi!):</i>";
        sendMessage($chat_id, $msg);
        exit;
    }"""

search_3 = """    elseif (strpos($data, "hmod_") === 0) {
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
    }"""

replace_3 = """    elseif (strpos($data, "hmod_") === 0) {
        $mode = str_replace("hmod_", "", $data);
        file_put_contents("hashtag_mode.txt", $mode);
        updateGitHubFile($GITHUB_REPO, "hashtag_mode.txt", $mode, $GITHUB_PAT);
        
        $mode_text = "";
        if ($mode == "caption_and_tags") $mode_text = "Izoh + Hashteglar";
        elseif ($mode == "tags_only") $mode_text = "Faqat Hashteglar";
        elseif ($mode == "off") $mode_text = "O'chirilgan";
        
        $t = time();
        $current_tags = @file_get_contents("https://raw.githubusercontent.com/temurbek1306/InstagaramAvtoReels/main/viral_tags.txt?t=$t");
        if (!$current_tags) $current_tags = "Hozircha bo'sh.";
        
        $keyboard = json_encode([
            "inline_keyboard" => [
                [["text" => "✍️ Hashteglarni o'zgartirish", "callback_data" => "edit_global_tags"]],
                [["text" => ($mode == "caption_and_tags" ? "✅ " : "") . "Izoh + Hashteglar", "callback_data" => "hmod_caption_and_tags"]],
                [["text" => ($mode == "tags_only" ? "✅ " : "") . "Faqat Hashteglar", "callback_data" => "hmod_tags_only"]],
                [["text" => ($mode == "off" ? "✅ " : "") . "❌ O'chirib qo'yish", "callback_data" => "hmod_off"]]
            ]
        ]);
        
        $url = "https://api.telegram.org/bot" . $TELEGRAM_TOKEN . "/editMessageText";
        $msg = "🔖 <b>Doimiy Hashteglar Sozlamasi</b>\n\n⚙️ Hozirgi rejim: <b>$mode_text</b>\n\n📝 <b>Joriy saqlangan hashteglar:</b>\n<pre>$current_tags</pre>\n\n👇 <i>Qanday ishlashini tanlang:</i>";
        file_get_contents($url . "?chat_id=$chat_id&message_id=$message_id&text=" . urlencode($msg) . "&parse_mode=HTML&reply_markup=" . $keyboard);
        exit;
    }"""

if search_1 in content:
    content = content.replace(search_1, replace_1)
    print("search_1 replaced")
else:
    print("search_1 not found")

if search_2 in content:
    content = content.replace(search_2, replace_2)
    print("search_2 replaced")
else:
    print("search_2 not found")
    
if search_3 in content:
    content = content.replace(search_3, replace_3)
    print("search_3 replaced")
else:
    print("search_3 not found")

open('php_bot/bot.php', 'w', encoding='utf-8').write(content)
print("bot.php patched successfully.")
