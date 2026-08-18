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
        
    # YAHAN SE 'format' HATA DIYA HAI - Taaki yt-dlp crash na ho
    ydl_opts = {
        'quiet': True,
        'extractor_args': {'youtubetab': {'skip': 'authcheck'}},
        'noplaylist': True, # Agar playlist link ho toh sirf single video uthaye
    }
    
    # Agar cookies.txt file bani hai toh use enable karein
    if os.path.exists("cookies.txt"):
        ydl_opts['cookiefile'] = 'cookies.txt'
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            # --- BULLETPROOF FORMAT SELECTION IN PYTHON ---
            video_link = None
            formats = info.get('formats', [])
            
            # Filter: Aise formats jisme Video aur Audio dono maujood hon
            combined_formats = [
                f for f in formats 
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none'
            ]
            
            if combined_formats:
                # MP4 ko priority dein, aur resolution (height) ke hisaab se sort karein
                mp4_formats = [f for f in combined_formats if f.get('ext') == 'mp4']
                if mp4_formats:
                    mp4_formats.sort(key=lambda x: x.get('height', 0) or 0, reverse=True)
                    video_link = mp4_formats[0].get('url')
                else:
                    combined_formats.sort(key=lambda x: x.get('height', 0) or 0, reverse=True)
                    video_link = combined_formats[0].get('url')
            
            # Fallback 1: yt-dlp ka default URL
            if not video_link and info.get('url'):
                video_link = info.get('url')
                
            # Fallback 2: Agar kuch nahi mila toh list ka aakhri valid url utha lo
            if not video_link and formats:
                for f in reversed(formats):
                    if f.get('url'):
                        video_link = f.get('url')
                        break
                        
            if not video_link:
                return jsonify({'error': 'Koi valid video link extract nahi ho paya.'}), 500

            return jsonify({
                'url': video_link,
                'title': info.get('title', 'Unknown Title'),
                'channel': info.get('uploader') or info.get('channel', 'Unknown Channel')
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)