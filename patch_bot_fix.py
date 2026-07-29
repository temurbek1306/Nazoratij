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
    content = content.replace("function sendMessage($chat_id, $text, $reply_markup = null) {", helper_function + "\nfunction sendMessage($chat_id, $text, $reply_markup = null) {")

with open("php_bot/bot.php", "w", encoding="utf-8") as f:
    f.write(content)

print("Patch applied to bot.php")
