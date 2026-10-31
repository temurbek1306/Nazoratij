import os
import requests

from bot_controller import send_telegram_msg

TOKEN = os.getenv("IG_ACCESS_TOKEN")
ACCOUNT = os.getenv("IG_ACCOUNT_ID")
BASE = "https://graph.facebook.com/v19.0"


def check(label, path, **params):
    """Faqat o'qish so'rovi: hech narsa joylamaydi va o'zgartirmaydi."""
    params["access_token"] = TOKEN
    data = requests.get(f"{BASE}/{path}", params=params, timeout=30).json()
    if "error" in data:
        error = data["error"]
        return data, f"❌ {label}: {error.get('code')} {str(error.get('message'))[:120]}"
    return data, f"✅ {label}"


def run():
    lines = []
    media, line = check("Postlar", f"{ACCOUNT}/media", fields="id,media_type,like_count,comments_count,comments_enabled,permalink", limit=1)
    lines.append(line)
    for label, path, params in [
        ("Profil", ACCOUNT, {"fields": "followers_count,media_count"}),
        ("Ruxsatlar", "me/permissions", {}),
        ("Akkaunt kunlik", f"{ACCOUNT}/insights", {"metric": "reach,follower_count", "period": "day"}),
        ("Akkaunt jami", f"{ACCOUNT}/insights", {"metric": "profile_views,accounts_engaged,total_interactions", "period": "day", "metric_type": "total_value"}),
        ("Belgilashlar", f"{ACCOUNT}/tags", {"fields": "id,permalink", "limit": 1}),
        ("Hashtag", "ig_hashtag_search", {"user_id": ACCOUNT, "q": "uzbekistan"}),
        ("Joylash kvotasi", f"{ACCOUNT}/content_publishing_limit", {"fields": "quota_usage"}),
    ]:
        data, line = check(label, path, **params)
        lines.append(line)
        if label == "Ruxsatlar":
            granted = [p["permission"] for p in data.get("data", []) if p.get("status") == "granted"]
            lines.append("🔑 " + ", ".join(granted))
    if media.get("data"):
        media_id = media["data"][0]["id"]
        for metric in ["reach", "views", "likes", "comments", "shares", "saved"]:
            lines.append(check(f"Post {metric}", f"{media_id}/insights", metric=metric)[1])
    report = "🧪 <b>Instagram diagnostika</b>\n\n" + "\n".join(lines)
    print(report)
    send_telegram_msg(report.replace("<b>", "").replace("</b>", "").replace("<", "").replace(">", ""))


if __name__ == "__main__":
    run()
