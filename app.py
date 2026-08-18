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
        'format': 'all',  
        'quiet': True,
        'extractor_args': {'youtubetab': {'skip': 'authcheck'}},
        'noplaylist': True,
        'ignoreerrors': True,
    }
    
    if os.path.exists("cookies.txt"):
        ydl_opts['cookiefile'] = 'cookies.txt'
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            if not info:
                return jsonify({'error': 'Video fetch nahi ho paya.'}), 500
            
            video_link = None
            formats = info.get('formats', [])
            
            # --- THE MASTER FIX: Target specific pre-merged formats ---
            # 22 = 720p MP4, 18 = 360p MP4 (Inme audio/video hamesha combined hota hai)
            for f_id in ['22', '18']:
                for f in formats:
                    if str(f.get('format_id')) == f_id and f.get('url'):
                        video_link = f.get('url')
                        break
                if video_link:
                    break
            
            # Agar kisi wajah se 22 ya 18 na mile, tab filter use karein
            if not video_link:
                combined = []
                for f in formats:
                    url = f.get('url', '')
                    protocol = f.get('protocol', '')
                    
                    if not url: continue
                    if 'm3u8' in protocol or 'm3u8' in url or 'manifest' in url: continue
                    if 'sb/' in url or '/storyboard' in url: continue
                    
                    # Agar audio aur video dono hain
                    if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                        combined.append(f)
                
                if combined:
                    combined.sort(key=lambda x: x.get('height') or 0, reverse=True)
                    video_link = combined[0].get('url')

            # Agar audio nahi mil raha (Shorts me kabhi-kabhi), toh sirf video utha lo
            if not video_link:
                video_only = []
                for f in formats:
                    url = f.get('url', '')
                    protocol = f.get('protocol', '')
                    if not url: continue
                    if 'm3u8' in protocol or 'm3u8' in url or 'manifest' in url: continue
                    if 'sb/' in url or '/storyboard' in url: continue
                    
                    if f.get('vcodec') != 'none':
                        video_only.append(f)
                        
                if video_only:
                    video_only.sort(key=lambda x: x.get('height') or 0, reverse=True)
                    video_link = video_only[0].get('url')

            if not video_link:
                return jsonify({'error': 'Is video ka direct MP4 stream maujood nahi hai.'}), 500

            return jsonify({
                'url': video_link,
                'title': info.get('title', 'Unknown Title'),
                'channel': info.get('uploader') or info.get('channel', 'Unknown Channel')
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)