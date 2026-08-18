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
        
    ydl_opts = {
        'format': 'all',  # <-- CRASH-PROOF JAADU: yt-dlp format filter nahi karega, sirf list dega
        'quiet': True,
        'extractor_args': {'youtubetab': {'skip': 'authcheck'}},
        'noplaylist': True,
        'ignoreerrors': True, # Kisi bhi internal error par crash hone se rokega
    }
    
    if os.path.exists("cookies.txt"):
        ydl_opts['cookiefile'] = 'cookies.txt'
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            if not info:
                return jsonify({'error': 'Video extract nahi ho paya. URL ya Cookies check karein.'}), 500
            
            video_link = None
            formats = info.get('formats', [])
            
            # 1. Aisa format dhoondo jisme Video + Audio dono hon
            combined = [
                f for f in formats 
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none'
            ]
            
            if combined:
                # MP4 ko priority
                mp4s = [f for f in combined if f.get('ext') == 'mp4']
                if mp4s:
                    mp4s.sort(key=lambda x: x.get('height') or 0, reverse=True)
                    video_link = mp4s[0].get('url')
                else:
                    combined.sort(key=lambda x: x.get('height') or 0, reverse=True)
                    video_link = combined[0].get('url')
            
            # 2. Agar combined nahi mila, toh fallback to best available URL
            if not video_link:
                for f in reversed(formats):
                    if f.get('url'):
                        video_link = f.get('url')
                        break
                        
            # 3. Agar info dict me direct url ho
            if not video_link and info.get('url'):
                video_link = info.get('url')
                
            if not video_link:
                return jsonify({'error': 'Is video ka direct download link nahi mil paya.'}), 500

            return jsonify({
                'url': video_link,
                'title': info.get('title', 'Unknown Title'),
                'channel': info.get('uploader') or info.get('channel', 'Unknown Channel')
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)