from flask import Flask, request, jsonify
import yt_dlp
import os

app = Flask(__name__)

# Render ke environment variable se cookies file automatically generate karna
cookie_data = os.environ.get("YOUTUBE_COOKIES")
if cookie_data:
    with open("cookies.txt", "w") as f:
        f.write(cookie_data)

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    video_url = data.get('url')
    
    if not video_url:
        return jsonify({'error': 'URL nahi mila'}), 400
        
    # 'best' format best hota hai direct download ke liye, bina format restriction ke
    ydl_opts = {
        'format': 'best', 
        'quiet': True,
        'extractor_args': {'youtubetab': {'skip': 'authcheck'}},
    }
    
    # Agar cookies.txt file bani hai toh use enable karein
    if os.path.exists("cookies.txt"):
        ydl_opts['cookiefile'] = 'cookies.txt'
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            # Agar 'url' field empty hai, toh 'requested_formats' se URL lene ki koshish karein
            video_link = info.get('url')
            if not video_link and 'formats' in info:
                # Sabse pehla available direct link utha lein
                video_link = info['formats'][0]['url']
                
            return jsonify({
                'url': video_link,
                'title': info.get('title', 'Unknown Title'),
                'channel': info.get('uploader') or info.get('channel', 'Unknown Channel')
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)