import re
from flask import Flask, Response, jsonify, request
import yt_dlp
import requests

app = Flask(__name__)  # Ensure this is the app instance used

@app.route('/get_video/<video_id>')
def get_video(video_id):
    # Validate the video ID format (YouTube video IDs are 11 characters)
    if not re.match(r'^[a-zA-Z0-9_-]{11}$', video_id):
        return jsonify({"error": "Invalid video ID"}), 400

    youtube_url = f"https://www.youtube.com/watch?v={video_id}"

    try:
        # Fetch video info using yt-dlp
        ydl_opts = {
            'format': 'best',
            'quiet': True,
            'noplaylist': True,
            'cookiefile': 'cookies.txt',
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(youtube_url, download=False)
            video_url = result['url']
    except Exception as e:
        app.logger.error(f"Error fetching video: {e}")
        return jsonify({"error": f"Failed to fetch video: {str(e)}"}), 500

    # Stream video content
    def generate():
        with requests.get(video_url, stream=True) as r:
            r.raise_for_status()
            for chunk in r.iter_content(chunk_size=8192):
                yield chunk

    return Response(generate(), content_type="video/mp4")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
