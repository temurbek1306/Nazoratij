import asyncio
from google.antigravity import LocalAgentConfig, CapabilitiesConfig
from google.antigravity.triggers import every
from google.antigravity.utils.interactive import run_interactive_loop

from agent_tools import get_pending_video, expose_video_url, post_to_instagram

async def hourly_reels_trigger(ctx):
    prompt = (
        "Vaqt bo'ldi! Iltimos, `get_pending_video` asbobidan foydalanib navbatdagi videoni tekshir. "
        "Agar video bor bo'lsa, `expose_video_url` orqali uni internetga chiqar. "
        "Keyin shu videoni Instagram Reels ga moslab zo'r, zamonaviy va trenddagi o'zbekcha matn (caption), smayliklar va heshteglar o'ylab top! "
        "Nihoyat, `post_to_instagram` orqali videoni o'zing tuzgan yozuv bilan Instagramga joyla. Barcha natijani hisobot ber."
    )
    await ctx.send(prompt)

# Agent konfiguratsiyasi
config = LocalAgentConfig(
    system_instructions=(
        "Sen Instagram uchun professional SMM menejer va AI Agentsan. "
        "Sening vazifang - mijozing uchun berilgan videolarga kreativ, zamonaviy, e'tiborni tortuvchi o'zbekcha yozuvlar (caption) yaratish. "
        "Har safar video qo'yganingda, post ma'nosi bilan bog'liq kulgili, qiziqarli yoki motivatsion gaplar va zo'r heshteglar qo'shishing kerak."
    ),
    tools=[get_pending_video, expose_video_url, post_to_instagram],
    # Har 7200 soniyada (2 soat) avtomatik trigger ishlaydi
    triggers=[every(7200, hourly_reels_trigger)],
    capabilities=CapabilitiesConfig()
)

async def main():
    print("=========================================================")
    print("🤖 Antigravity Instagram Agent ishga tushdi!")
    print("Agent har 1 soatda avtomatik o'zi uyg'onib, video joylaydi.")
    print("Siz hozir ham (kutib o'tirmasdan) bevosita agentga yozib:")
    print(" 'Hozir bitta video qo'yib yubor' deb buyruq berishingiz mumkin!")
    print("=========================================================\n")
    
    await run_interactive_loop(config)

if __name__ == "__main__":
    asyncio.run(main())
