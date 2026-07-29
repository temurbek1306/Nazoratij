import re
import os

new_secrets = """          TELEGRAM_CHANNEL_ID: ${{ secrets.TELEGRAM_CHANNEL_ID }}
          FB_PAGE_ID: ${{ secrets.FB_PAGE_ID }}
          FB_PAGE_ACCESS_TOKEN: ${{ secrets.FB_PAGE_ACCESS_TOKEN }}
          TIKTOK_CLIENT_KEY: ${{ secrets.TIKTOK_CLIENT_KEY }}
          TIKTOK_CLIENT_SECRET: ${{ secrets.TIKTOK_CLIENT_SECRET }}
          TIKTOK_REFRESH_TOKEN: ${{ secrets.TIKTOK_REFRESH_TOKEN }}"""

def update_yaml(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # We want to insert new_secrets just before TELEGRAM_BOT_TOKEN or anywhere inside the env: block
    if "TELEGRAM_CHANNEL_ID" not in content:
        # find TELEGRAM_BOT_TOKEN and insert before it
        content = content.replace("TELEGRAM_BOT_TOKEN:", new_secrets + "\n          TELEGRAM_BOT_TOKEN:")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Updated {file_path}")
    else:
        print(f"Secrets already in {file_path}")

update_yaml(".github/workflows/autopost.yml")
update_yaml(".github/workflows/merge_videos.yml")

print("Done")
