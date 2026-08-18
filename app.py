from flask import Flask, request, jsonify
import yt_dlp
import os

app = Flask(__name__)

# --- YAHAN APNI COOKIES.TXT KA SAARA TEXT PASTE KAREIN ---
RAW_COOKIE_DATA = '''# Netscape HTTP Cookie File
# https://curl.haxx.se/rfc/cookie_spec.html
# This is a generated file! Do not edit.

# (APNI COOKIES YAHAN PASTE KAREIN...)
'''

with open("cookies.txt", "w", encoding="utf-8") as f:
    f.write(RAW_COOKIE_DATA.strip())

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    video_url = data.get('url')
    
    if not video_url:
        return jsonify({'error': 'URL nahi mila'}), 400
        
    ydl_opts = {
        'format': 'all',  
        'quiet': True,
        'extractor_args': {'youtube': {'player_client': ['web']}},
        'noplaylist': True,
        'ignoreerrors': False, 
        'cookiefile': 'cookies.txt', 
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            if not info:
                return jsonify({'error': 'Video fetch nahi ho paya.'}), 500
            
            formats = info.get('formats', [])
            available_formats = []
            
            for f in formats:
                url = f.get('url', '')
                protocol = f.get('protocol', '')
                ext = f.get('ext', '')
                
                # Faltu links aur m3u8 ko ignore karein
                if not url: continue
                if 'm3u8' in protocol or 'm3u8' in url or 'manifest' in url: continue
                if 'sb/' in url or '/storyboard' in url: continue
                if f.get('vcodec') == 'none': continue # Sirf video formats chahiye
                
                height = f.get('height', 0) or 0
                has_audio = f.get('acodec') != 'none'
                
                # Format ka mast naam banayein (Audio hai ya nahi)
                audio_text = "🔊 (Video + Audio)" if has_audio else "🔇 (Sirf Video / Mute)"
                label = f"{height}p - {ext.upper()} {audio_text}"
                
                available_formats.append({
                    'label': label,
                    'url': url,
                    'height': height
                })
                
            # Highest Quality upar rakhne ke liye sort karein
            available_formats.sort(key=lambda x: x['height'], reverse=True)
            
            # Duplicate quality hatayein
            seen = set()
            unique_formats = []
            for f in available_formats:
                if f['label'] not in seen:
                    seen.add(f['label'])
                    unique_formats.append(f)

            if not unique_formats:
                return jsonify({'error': 'Koi direct stream nahi mili.'}), 500

            return jsonify({
                'title': info.get('title', 'Unknown Title'),
                'channel': info.get('uploader') or info.get('channel', 'Unknown Channel'),
                'formats': unique_formats
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)