from flask import Flask, Response, jsonify
import yt_dlp
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <h1>Flask Server is Running</h1>
    <p>To fetch masked videos, use the following route:</p>
    <pre>/get_video/&lt;video_id&gt;</pre>
    <p>Example:</p>
    <pre><a href="/get_video/gkD7TbavRwA" target="_blank">http://127.0.0.1:5000/get_video/gkD7TbavRwA</a></pre>
    """

@app.route('/get_video/<video_id>')
def get_video(video_id):
    youtube_url = f"https://www.youtube.com/watch?v={video_id}"

    # Use yt-dlp to fetch the video stream URL
    try:
        ydl_opts = {
            'format': 'best',  # Fetch the best available format
            'quiet': True,
            'noplaylist': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(youtube_url, download=False)
            video_url = result['url']  # Get the direct video stream URL

    except Exception as e:
        return jsonify({"error": f"Failed to fetch video: {str(e)}"}), 500

    # Stream the video content directly from the YouTube stream URL
    def generate():
        with requests.get(video_url, stream=True) as r:
            r.raise_for_status()  # Ensure the request was successful
            for chunk in r.iter_content(chunk_size=8192):
                yield chunk

    return Response(generate(), content_type="video/mp4")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
