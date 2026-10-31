import html
import json
import os

from instagram_api import InstagramAPI
from bot_controller import send_telegram_msg


def _api():
    return InstagramAPI(os.getenv("IG_ACCESS_TOKEN"), os.getenv("IG_ACCOUNT_ID"))


def _short(text, size=70):
    return html.escape((text or "(matnsiz)").replace("\n", " ")[:size])


def _report(result, success_text):
    """Graph API javobini admin uchun tushunarli xabarga aylantiradi."""
    if "error" in result:
        send_telegram_msg(f"❌ Instagram rad etdi: {_short(result['error'].get('message'), 300)}")
    else:
        send_telegram_msg(success_text)


def show_stats(api):
    profile = api.get_profile_stats() or {}
    stats = api.get_account_insights()
    msg = f"📊 <b>Instagram statistikasi</b>\n\n👥 Obunachilar: {profile.get('followers', '?')}\n🎬 Postlar: {profile.get('media', '?')}\n\n<b>Oxirgi kun:</b>\n"
    msg += "\n".join(f"• {html.escape(k)}: {v}" for k, v in stats.items()) or "Ma'lumot yo'q."
    send_telegram_msg(msg)


def show_media(api):
    items = api.get_media_list()
    if not items:
        send_telegram_msg("📭 Postlar topilmadi.")
        return
    msg = "📱 <b>Oxirgi postlar:</b>\n\n"
    keyboard = []
    for i, m in enumerate(items, 1):
        msg += f"{i}. {_short(m.get('caption'))}\n❤️ {m.get('like_count', 0)} 💬 {m.get('comments_count', 0)} | {m.get('permalink', '')}\n\n"
        toggle = "off" if m.get("comments_enabled", True) else "on"
        keyboard.append([
            {"text": f"💬 {i}", "callback_data": f"ig_cm_{m['id']}"},
            {"text": f"📈 {i}", "callback_data": f"ig_ins_{m['id']}"},
            {"text": f"🔕 {i}" if toggle == "off" else f"🔔 {i}", "callback_data": f"ig_c{toggle}_{m['id']}"},
            {"text": f"🗑 {i}", "callback_data": f"ig_askdel_{m['id']}"},
        ])
    send_telegram_msg(msg, reply_markup=json.dumps({"inline_keyboard": keyboard}))


def show_comments(api, media_id):
    comments = api.get_comments(media_id)[:8]
    if not comments:
        send_telegram_msg("💬 Izohlar yo'q.")
        return
    for c in comments:
        keyboard = [[
            {"text": "↩️ Javob", "callback_data": f"ig_reply_{c['id']}"},
            {"text": "🙈 Yashirish", "callback_data": f"ig_hide_{c['id']}"},
            {"text": "🗑 O'chirish", "callback_data": f"ig_rm_{c['id']}"},
        ]]
        send_telegram_msg(f"<b>{_short(c.get('username'), 40)}</b>: {_short(c.get('text'), 500)}", reply_markup=json.dumps({"inline_keyboard": keyboard}))


def show_insights(api, media_id):
    stats = api.get_media_insights(media_id)
    body = "\n".join(f"• {html.escape(k)}: {v}" for k, v in stats.items()) or "Ma'lumot yo'q."
    send_telegram_msg(f"📈 <b>Post statistikasi</b>\n\n{body}")


def show_links(title, items):
    if not items:
        send_telegram_msg(f"{title}\n\nHech narsa topilmadi.")
        return
    lines = [f"• {_short(i.get('caption'))}\n{i.get('permalink', '')}" for i in items]
    send_telegram_msg(title + "\n\n" + "\n\n".join(lines))


def handle(command, prompt):
    api = _api()
    action, _, target = command[3:].partition("_")
    try:
        if action == "stats":
            show_stats(api)
        elif action == "media":
            show_media(api)
        elif action == "cm":
            show_comments(api, target)
        elif action == "ins":
            show_insights(api, target)
        elif action == "con":
            _report(api.set_comments_enabled(target, True), "🔔 Izohlar yoqildi.")
        elif action == "coff":
            _report(api.set_comments_enabled(target, False), "🔕 Izohlar o'chirildi.")
        elif action == "del":
            _report(api.delete_media(target), "🗑 Post o'chirildi.")
        elif action == "hide":
            _report(api.hide_comment(target), "🙈 Izoh yashirildi.")
        elif action == "rm":
            _report(api.delete_comment(target), "🗑 Izoh o'chirildi.")
        elif action == "reply":
            ok = api.reply_to_comment(target, prompt)
            send_telegram_msg("✅ Javob yuborildi." if ok else "❌ Javob yuborilmadi.")
        elif action == "tags":
            show_links("🏷 <b>Sizni belgilagan postlar</b>", api.get_tagged_media())
        elif action == "story":
            media = json.loads(prompt)
            api.publish_story(media["url"], media["is_video"])
            send_telegram_msg("✅ Story joylandi!")
        elif action == "post":
            post = json.loads(prompt)
            if len(post["urls"]) == 1:
                api.publish_photo(post["urls"][0], post["caption"])
            else:
                api.publish_carousel(post["urls"], post["caption"])
            send_telegram_msg("✅ Post joylandi!")
        else:
            send_telegram_msg("❓ Noma'lum Instagram komandasi.")
    except Exception as e:
        send_telegram_msg(f"❌ Instagram xatosi: {_short(str(e), 300)}")
