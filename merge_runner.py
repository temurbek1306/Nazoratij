import os
import requests
import subprocess
import json

def send_telegram_video(bot_token, chat_id, video_path, caption, reply_markup=None):
    url = f"https://api.telegram.org/bot{bot_token}/sendVideo"
    with open(video_path, 'rb') as f:
        files = {'video': f}
        data = {'chat_id': chat_id, 'caption': caption, 'parse_mode': 'HTML'}
        if reply_markup:
            data['reply_markup'] = json.dumps(reply_markup)
        response = requests.post(url, data=data, files=files)
        return response.json()

def main():
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    admin_id = os.getenv("TELEGRAM_ADMIN_ID")
    video_urls = os.getenv("VIDEO_URLS", "").split(",")
    run_id = os.getenv("GITHUB_RUN_ID")

    if not bot_token or not admin_id or not video_urls:
        print("Missing required environment variables.")
        return

    print(f"Downloading {len(video_urls)} videos...")
    
    input_files = []
    for i, url in enumerate(video_urls):
        url = url.strip()
        if not url:
            continue
        filepath = f"temp_input_{i}.mp4"
        r = requests.get(url, stream=True)
        if r.status_code == 200:
            with open(filepath, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024*1024):
                    f.write(chunk)
            input_files.append(filepath)
            print(f"Downloaded video {i+1}")

    if len(input_files) < 2:
        print("Not enough videos downloaded.")
        return

    print("Normalizing videos...")
    std_files = []
    for i, f in enumerate(input_files):
        std_f = f"std_{i}.mp4"
        # Normalize to 1080x1920, 30fps, SAR 1:1, and stereo 44.1kHz audio
        cmd = [
            "ffmpeg", "-y", "-i", f,
            "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30",
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "aac", "-ar", "44100", "-ac", "2",
            std_f
        ]
        subprocess.run(cmd, check=True)
        std_files.append(std_f)

    durations = []
    for f in std_files:
        cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", f]
        output = subprocess.check_output(cmd).decode('utf-8').strip()
        durations.append(float(output))
    
    crossfade_duration = 0.3
    output_video = "merged_high_res.mp4"
    
    if len(std_files) == 2:
        offset = durations[0] - crossfade_duration
        if offset < 0: offset = 0
        
        filter_str = f"[0:v]format=yuv420p[v0];[1:v]format=yuv420p[v1];[v0][v1]xfade=transition=fade:duration={crossfade_duration}:offset={offset}[v];[0:a][1:a]acrossfade=d={crossfade_duration}:curve1=nofade:curve2=nofade[a]"
        
        cmd = [
            "ffmpeg", "-y",
            "-i", std_files[0],
            "-i", std_files[1],
            "-filter_complex", filter_str,
            "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac",
            output_video
        ]
        print(f"Running ffmpeg (2 videos): {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
    else:
        print("More than 2 videos, using simple concat.")
        with open("concat_list.txt", "w") as f:
            for filepath in std_files:
                f.write(f"file '{filepath}'\n")
        
        cmd = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", "concat_list.txt", 
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac",
            output_video
        ]
        subprocess.run(cmd, check=True)

    preview_video = "merged_preview.mp4"
    cmd = [
        "ffmpeg", "-y", "-i", output_video,
        "-vf", "scale=480:-2,format=yuv420p", "-c:v", "libx264", "-crf", "28", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "64k",
        preview_video
    ]
    subprocess.run(cmd, check=True)

    keyboard = {
        "inline_keyboard": [
            [{"text": "✅ Tasdiqlash va Davom etish", "callback_data": f"approve_merged_{run_id}"}],
            [{"text": "❌ O'chirish", "callback_data": f"delete_merged_{run_id}"}]
        ]
    }
    
    caption = "🎬 <b>Birlashtirilgan Video Tayyor!</b>\n\nBu kichraytirilgan prevyu. Agar ma'qul bo'lsa, 'Tasdiqlash' tugmasini bosing va asl HD video tarmoqlarga joylanadi."
    print("Sending preview to Telegram...")
    res = send_telegram_video(bot_token, admin_id, preview_video, caption, reply_markup=keyboard)
    print("Telegram response:", res)

if __name__ == "__main__":
    main()
