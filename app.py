from flask import Flask, request, jsonify
import yt_dlp
import os

app = Flask(__name__)

# --- HARDCODED COOKIES DATA ---
RAW_COOKIE_DATA = '''# Netscape HTTP Cookie File
# https://curl.haxx.se/rfc/cookie_spec.html
# This is a generated file! Do not edit.

.youtube.com	TRUE	/	TRUE	1802573191	PREF	f6=40000000&f7=140&tz=Asia.Calcutta&f2=8000000&f4=4000000&f5=30000
.youtube.com	TRUE	/	TRUE	1791171415	__Secure-BUCKET	CEU
.youtube.com	TRUE	/	TRUE	1791539815	LOGIN_INFO	AFmmF2swRAIgRN8BkM4bZv3xkj63Pul6vZW0D3EyKkw5g6K5SY-ioDYCIGU0vw32znhoiEaaDQ8kSRkZzpcafQHWL2TVft0njEUu:QUQ3MjNmeDlCVHh6cHNFRGFZSWJRMDBha3hQMHhyTHR2WFpkNUlZUjJWbzBTZ1BtSzdzQi1ZOE5qaHNGd0V1YnByV1loVHEybnE1bGhnUzd1VGl6SkxyRTVCVjJjTmxmVndkUzBPb0JQZlVWdGlqNnJlQkVoVU42bktEUHpOaDJ4R3VfV2UwWmVwR0FCOEVSWWR2S05FSmFpTEd1T2U4OHJWdkJpWkZrT09ENGs2LWJNeVIzTUZKOXY1N2kyZWtBb25zWnozNWxFYXZQY1dxckNZdG9vS0JLTGpmM0ZTakNxdw==
.youtube.com	TRUE	/	FALSE	1801233679	HSID	ApJ1viuO6XRhm-IZf
.youtube.com	TRUE	/	TRUE	1801233679	SSID	Ai_q8BMo-KSQRPQnP
.youtube.com	TRUE	/	FALSE	1801233679	APISID	ongqyKKdPsdB3nni/AvaHFqwja2Va-r9Ke
.youtube.com	TRUE	/	TRUE	1801233679	SAPISID	3x748pXN0DTerEZX/AyTjyaf-r9MI29R4N
.youtube.com	TRUE	/	TRUE	1801233679	__Secure-1PAPISID	3x748pXN0DTerEZX/AyTjyaf-r9MI29R4N
.youtube.com	TRUE	/	TRUE	1801233679	__Secure-3PAPISID	3x748pXN0DTerEZX/AyTjyaf-r9MI29R4N
.youtube.com	TRUE	/	FALSE	1801233679	SID	g.a000BAkzjOrhghtgmGo3eLf_qT4Hy664P8BxVd-O3E7mwvUDU6shuQzmHNIlT553H1klt5JFCQACgYKAe8SARQSFQHGX2MiwDEjLax2U4GdrV92hVrobxoVAUF8yKoGDt1R61lJPiXLNrGUGZDy0076
.youtube.com	TRUE	/	TRUE	1801233679	__Secure-1PSID	g.a000BAkzjOrhghtgmGo3eLf_qT4Hy664P8BxVd-O3E7mwvUDU6shpL9GfAt7tIrffiraoqm2-gACgYKAQcSARQSFQHGX2MieJyzJskQdhJVLWQPExJ6ARoVAUF8yKrw7ZXcpKPwpkFLrDjnqNFt0076
.youtube.com	TRUE	/	TRUE	1801233679	__Secure-3PSID	g.a000BAkzjOrhghtgmGo3eLf_qT4Hy664P8BxVd-O3E7mwvUDU6shBJNNFvUzGiqfA3uFFSPaRQACgYKAR4SARQSFQHGX2MikJvu07b-lAHa9yxUY4MaaRoVAUF8yKqlHq1xuo6jrFbPaSqkpjMQ0076
.youtube.com	TRUE	/	TRUE	0	wide	1
.youtube.com	TRUE	/	TRUE	1802573923	__Secure-1PSIDTS	sidts-CjQBXMw41W1a2BLILm9fxP1eg3pmcehbB4sDppZNBYWG7LUoRRZCP9T2p0Ll3rKqM537yOq9EAA
.youtube.com	TRUE	/	TRUE	1802573923	__Secure-3PSIDTS	sidts-CjQBXMw41W1a2BLILm9fxP1eg3pmcehbB4sDppZNBYWG7LUoRRZCP9T2p0Ll3rKqM537yOq9EAA
.youtube.com	TRUE	/	FALSE	1802573923	SIDCC	AKEyXzXcyGNnZHzHNT8tz2R65A52NNB_37nlhYA0MyyLx4E--ZMoMpj0pgwaz5tVp_hjhiRoyBc
.youtube.com	TRUE	/	TRUE	1802573923	__Secure-1PSIDCC	AKEyXzV7_BGJ-JPgXdW4YsyUZi1ztgw_wvLBGiGpEVm4zDeFJxxx5GBXs2cdUhbtPqr-H70a1w
.youtube.com	TRUE	/	TRUE	1802573923	__Secure-3PSIDCC	AKEyXzVJbOC15gqketofxCO0pRyLsqDIzOAREoMf52vI8W66siJixmpNYfWFusqKrXxK8v6_qg
.youtube.com	TRUE	/	TRUE	1802570776	VISITOR_INFO1_LIVE	jQ9cj0p_tZM
.youtube.com	TRUE	/	TRUE	1802570776	VISITOR_PRIVACY_METADATA	CgJJThIEGgAgEw%3D%3D
.youtube.com	TRUE	/	TRUE	0	YSC	22-XHggHz5E
.youtube.com	TRUE	/	TRUE	1802566218	__Secure-ROLLOUT_TOKEN	CLq0w-2YmKq27gEQx-Wksa70iQMY_-O53fqolgM%3D
.youtube.com	TRUE	/	TRUE	1802566218	__Secure-YNID	21.YT=nM3lLNV3ClZB0QNFPdPd48NUNqSOemo4tvsDDgBvJ2ZrIK-w47ED3FNMhoAySzWj1qE92qzIkC4oQL4ukUzmw2GY0nIWFTCTE5oB8LBHpKGftdDXxXUtWDIb9CRLKFOkv9FktlbMmsxGi5bxtiNCweW51DSROA5fXnvxwMJrwR4VGO7vplMPzP9O7NGmM_oUZxGbvnqTJDTsgRtXOUQOUFrlhF8CqgXd7IrO7lx0Qk1ijkoeLFDZI4kvihidfcuCvqhJ_AcQY-VhZSh3XIDynSqVCq5dZMHLop8HpXwA4iz1gNMt4nqXqLnxdlmhGG_idWb0FFqhWTQCJuiFxbjbkQ'''

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
        # YAHAN SIRF 'web' RAKHA HAI KUKYI COOKIES BHI WEB KI HAIN
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
            
            video_link = None
            formats = info.get('formats', [])
            
            for f_id in ['22', '18']:
                for f in formats:
                    if str(f.get('format_id')) == f_id and f.get('url'):
                        video_link = f.get('url')
                        break
                if video_link:
                    break
            
            if not video_link:
                combined = []
                for f in formats:
                    url = f.get('url', '')
                    protocol = f.get('protocol', '')
                    
                    if not url: continue
                    if 'm3u8' in protocol or 'm3u8' in url or 'manifest' in url: continue
                    if 'sb/' in url or '/storyboard' in url: continue
                    
                    if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                        combined.append(f)
                
                if combined:
                    combined.sort(key=lambda x: x.get('height') or 0, reverse=True)
                    video_link = combined[0].get('url')

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