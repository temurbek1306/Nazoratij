import os

content = open('php_bot/bot.php', 'r', encoding='utf-8').read()

search = """    elseif ($data == "edit_global_tags") {
        file_put_contents("state.txt", "waiting_for_global_tags");
        $msg = "🔖 <b>Doimiy Matn/Hashteglar</b>\n\nBu yerda yozgan har qanday matningiz poistingizga qo'shiladi.\n\n👇 <i>Yangi doimiy matnni yuboring:</i>";
        sendMessage($chat_id, $msg);
        exit;
    }"""

replace = """    elseif ($data == "edit_global_tags") {
        file_put_contents("state.txt", "waiting_for_global_tags");
        $msg = "🔖 <b>Doimiy Matn/Hashteglar</b>\n\nBu yerda yozgan har qanday matningiz videolarga qo'shiladi.\n\n🔄 <b>Navbatma-navbat ishlashi uchun:</b>\nAgar siz bir nechta xil hashteglarni navbat bilan (1-videoga 1-hashteg, 2-videoga 2-hashteg) chiqishini xohlasangiz, ularni <b>===</b> belgisi bilan ajrating.\nMasalan:\n#kulgili #rek\n===\n#uzb #trend\n\n👇 <i>Yangi doimiy matnni yuboring:</i>";
        sendMessage($chat_id, $msg);
        exit;
    }"""

if search in content:
    content = content.replace(search, replace)
    open('php_bot/bot.php', 'w', encoding='utf-8').write(content)
    print("Prompt updated successfully.")
else:
    print("Search string not found in bot.php")
