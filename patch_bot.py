import re

with open("php_bot/bot.php", "r", encoding="utf-8") as f:
    content = f.read()

helper_function = """// --- Tarmoqlarni tanlash klaviaturasi ---
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
"""

if "function get_platforms_keyboard" not in content:
    content = content.replace("function sendMessage($chat_id, $text, $keyboard = null) {", helper_function + "\nfunction sendMessage($chat_id, $text, $keyboard = null) {")

# Replace occurrences of hardcoded platform json_encode block
regex = re.compile(r'\$keyboard = json_encode\(\[\s*"inline_keyboard" => \[\s*\[\["text" => "📸 Instagram".*?\]\s*\);', re.DOTALL)
content = regex.sub('$keyboard = get_platforms_keyboard($chat_id);', content)

# Remove old platform_ handler
old_handler_regex = re.compile(r'    if \(strpos\(\$data, "platform_"\) === 0\) \{.*?\n    \}', re.DOTALL)

new_handlers = """    // Toggle handling
    if (strpos($data, "toggle_") === 0) {
        $key = str_replace("toggle_", "", $data);
        $state_file = "platforms_" . $chat_id . ".json";
        $platforms = json_decode(file_get_contents($state_file), true);
        $platforms[$key] = !$platforms[$key];
        file_put_contents($state_file, json_encode($platforms));
        
        $keyboard = get_platforms_keyboard($chat_id);
        $url = "https://api.telegram.org/bot" . $TELEGRAM_TOKEN . "/editMessageReplyMarkup";
        file_get_contents($url . "?chat_id=$chat_id&message_id=$message_id&reply_markup=" . $keyboard);
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
        sendMessage($chat_id, "✅ Tarmoqlar tasdiqlandi!\\n\\nEndi izohni kim yozadi?", $keyboard);
        $url = "https://api.telegram.org/bot" . $TELEGRAM_TOKEN . "/editMessageReplyMarkup";
        file_get_contents($url . "?chat_id=$chat_id&message_id=$message_id&reply_markup=" . json_encode(["inline_keyboard" => []]));
        exit;
    }"""
content = old_handler_regex.sub(new_handlers, content)

with open("php_bot/bot.php", "w", encoding="utf-8") as f:
    f.write(content)

print("Patch applied to bot.php")
