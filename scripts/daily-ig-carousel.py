#!/usr/bin/env python3
"""
BOBA Daily IG Carousel 產生器
用法：python3 scripts/daily-ig-carousel.py <twitter_text_file> <cover_image> <date> <output_dir>
範例：python3 scripts/daily-ig-carousel.py /tmp/boba_daily_x.txt output/drafts/daily-0327-ig-base.png "3/27" output/ig-0327/

產出：
  output_dir/slide-00-cover.png  — 封面（4:5 Pepe AI 圖 + overlay）
  output_dir/slide-01.png        — 第 1 則新聞
  ...
  output_dir/slide-08.png        — 第 8 則新聞
"""

import re, os, sys, subprocess, shutil, tempfile
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading

def parse_stories(twitter_file):
    with open(twitter_file, 'r', encoding='utf-8') as f:
        raw = f.read()
    blocks = re.split(r'\n———\n', raw)
    stories = []
    for block in blocks:
        block = block.strip()
        if re.match(r'^[0-9]️⃣', block):
            lines = block.split('\n')
            raw_title = lines[0].strip()
            clean_title = re.sub(r'^[0-9]️⃣\s*', '', raw_title)
            body = '\n'.join(lines[1:]).strip()
            stories.append({'title': clean_title, 'body': body})
    return stories

def _font_face(font_url):
    return f"""@font-face {{
    font-family: 'Noto Sans TC';
    src: url('{font_url}') format('truetype');
    font-weight: 100 900;
  }}"""


def generate_slide_html(num, title, body, cover_url, logo_url, total, font_url=''):
    return f'''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  {_font_face(font_url) if font_url else ''}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    width: 1080px;
    height: 1350px;
    font-family: 'Noto Sans TC', -apple-system, 'Heiti TC', sans-serif;
    overflow: hidden;
    background: #000;
  }}
  .card {{
    position: relative;
    width: 1080px;
    height: 1350px;
  }}
  .bg {{
    position: absolute;
    top: -20px; left: -20px;
    width: calc(100% + 40px);
    height: calc(100% + 40px);
    background: url('{cover_url}') center/cover no-repeat;
    filter: blur(10px) brightness(0.28);
    z-index: 1;
  }}
  .overlay {{
    position: relative;
    z-index: 2;
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }}
  .main {{
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: 60px 72px;
    gap: 32px;
  }}
  .badge {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 48px;
    height: 48px;
    background: #FF8374;
    border-radius: 12px;
    color: white;
    font-size: 24px;
    font-weight: 800;
  }}
  .title {{
    font-size: 44px;
    font-weight: 900;
    line-height: 1.45;
    color: white;
    text-shadow: 0 2px 24px rgba(0,0,0,0.6);
  }}
  .divider {{
    width: 60px;
    height: 4px;
    background: #FF8374;
    border-radius: 2px;
  }}
  .body-text {{
    font-size: 29px;
    font-weight: 400;
    line-height: 1.9;
    color: rgba(255,255,255,0.85);
    text-shadow: 0 1px 16px rgba(0,0,0,0.5);
  }}
  .bottom {{
    background: rgba(0,0,0,0.55);
    padding: 22px 72px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-top: 1px solid rgba(255,255,255,0.08);
  }}
  .brand {{
    display: flex;
    align-items: center;
    gap: 14px;
  }}
  .brand-logo {{ height: 36px; }}
  .brand-sep {{
    width: 1px;
    height: 24px;
    background: rgba(255,255,255,0.2);
  }}
  .brand-name {{
    font-size: 16px;
    color: rgba(255,255,255,0.65);
    font-weight: 500;
    letter-spacing: 0.5px;
  }}
  .brand-handle {{
    font-size: 13px;
    color: rgba(255,255,255,0.35);
    margin-top: 2px;
  }}
  .page-num {{
    font-size: 15px;
    color: rgba(255,255,255,0.35);
    letter-spacing: 2px;
  }}
</style>
</head>
<body>
<div class="card">
  <div class="bg"></div>
  <div class="overlay">
    <div class="main">
      <div class="badge">{num}</div>
      <h1 class="title">{title}</h1>
      <div class="divider"></div>
      <p class="body-text">{body}</p>
    </div>
    <div class="bottom">
      <div class="brand">
        <img class="brand-logo" src="{logo_url}" />
        <div class="brand-sep"></div>
        <div>
          <div class="brand-name">珍奶科技日報 BOBA Daily</div>
          <div class="brand-handle">@bobadao_lfg</div>
        </div>
      </div>
      <span class="page-num">{num} / {total}</span>
    </div>
  </div>
</div>
</body>
</html>'''

def generate_cover_html(cover_url, logo_url, date, hook, font_url='', port=18765):
    """Generate cover HTML with headline + same bottom bar as content slides"""
    return f'''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  {_font_face(font_url) if font_url else ''}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    width: 1080px;
    height: 1350px;
    font-family: 'Noto Sans TC', -apple-system, 'Heiti TC', sans-serif;
    overflow: hidden;
    background: #000;
  }}
  .card {{
    position: relative;
    width: 1080px;
    height: 1350px;
  }}
  .bg-img {{
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 100%;
    object-fit: cover;
    z-index: 1;
  }}
  .gradient {{
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 60%;
    background: linear-gradient(transparent 0%, rgba(0,0,0,0.6) 40%, rgba(0,0,0,0.88) 100%);
    z-index: 2;
  }}
  .overlay {{
    position: relative;
    z-index: 3;
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
  }}
  .headline {{
    padding: 0 72px 24px;
    display: flex;
    flex-direction: column;
    gap: 16px;
  }}
  .date-badge {{
    display: inline-flex;
    align-items: center;
    background: #FF8374;
    border-radius: 8px;
    padding: 8px 18px;
    width: fit-content;
    font-size: 16px;
    font-weight: 700;
    color: white;
    letter-spacing: 1px;
  }}
  .hook {{
    font-size: 40px;
    font-weight: 900;
    line-height: 1.4;
    color: white;
    text-shadow: 0 2px 20px rgba(0,0,0,0.5);
  }}
  .swipe {{
    font-size: 16px;
    color: rgba(255,255,255,0.45);
    letter-spacing: 0.5px;
    margin-top: 4px;
  }}
  .bottom {{
    background: rgba(0,0,0,0.55);
    padding: 22px 72px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-top: 1px solid rgba(255,255,255,0.08);
  }}
  .brand {{
    display: flex;
    align-items: center;
    gap: 14px;
  }}
  .brand-logo {{ height: 36px; }}
  .brand-sep {{
    width: 1px;
    height: 24px;
    background: rgba(255,255,255,0.2);
  }}
  .brand-name {{
    font-size: 16px;
    color: rgba(255,255,255,0.65);
    font-weight: 500;
    letter-spacing: 0.5px;
  }}
  .brand-handle {{
    font-size: 13px;
    color: rgba(255,255,255,0.35);
    margin-top: 2px;
  }}
  .date-text {{
    font-size: 15px;
    color: rgba(255,255,255,0.4);
    letter-spacing: 2px;
  }}
</style>
</head>
<body>
<div class="card">
  <img class="bg-img" src="{cover_url}" />
  <div class="gradient"></div>
  <div class="overlay">
    <div style="flex:1"></div>
    <div class="headline">
      <div class="date-badge"><img src="http://localhost:{port}/boba-emoji.png" style="height:1.2em;vertical-align:middle;margin-right:4px"> {date} 每日快報</div>
      <h1 class="hook">{hook}</h1>
      <div class="swipe">👉 滑動看完整 8 則新聞</div>
    </div>
    <div class="bottom">
      <div class="brand">
        <img class="brand-logo" src="{logo_url}" />
        <div class="brand-sep"></div>
        <div>
          <div class="brand-name">珍奶科技日報 BOBA Daily</div>
          <div class="brand-handle">@bobadao_lfg</div>
        </div>
      </div>
      <span class="date-text">{date}</span>
    </div>
  </div>
</div>
</body>
</html>'''

def _find_chrome():
    candidates = [
        '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        '/Applications/Chromium.app/Contents/MacOS/Chromium',
        '/usr/bin/google-chrome',
        '/usr/bin/google-chrome-stable',
        '/usr/bin/chromium-browser',
        '/usr/bin/chromium',
        '/snap/bin/chromium',
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path
    # Try PATH
    import shutil as _shutil
    for name in ('google-chrome', 'google-chrome-stable', 'chromium-browser', 'chromium'):
        found = _shutil.which(name)
        if found:
            return found
    raise FileNotFoundError(
        "找不到 Chrome/Chromium。請安裝 Google Chrome 或 Chromium。"
    )


def chrome_screenshot(html_path, output_path, port):
    """Use Chrome headless to screenshot HTML at 1080x1350"""
    abs_output = os.path.abspath(output_path)
    url = f'http://localhost:{port}/{os.path.basename(html_path)}'
    subprocess.run([
        _find_chrome(),
        '--headless=new', '--disable-gpu',
        '--no-sandbox',
        f'--screenshot={abs_output}',
        '--window-size=1080,1600',
        '--hide-scrollbars',
        f'--disk-cache-dir=/tmp/chrome-ig-{os.getpid()}',
        url
    ], capture_output=True, timeout=30)
    # Crop to 1080x1350
    subprocess.run([
        'magick', abs_output,
        '-crop', '1080x1350+0+0', '+repage',
        abs_output
    ], check=True)

def main():
    if len(sys.argv) < 5:
        print("用法：python3 daily-ig-carousel.py <twitter_text> <cover_image> <date> <output_dir>")
        sys.exit(1)

    twitter_file = sys.argv[1]
    cover_image = os.path.abspath(sys.argv[2])
    date = sys.argv[3]
    output_dir = sys.argv[4]

    orig_cwd = os.getcwd()
    output_dir = os.path.abspath(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    # Parse stories + extract hook from Twitter text header
    stories = parse_stories(twitter_file)
    total = len(stories)
    print(f"📋 解析到 {total} 則新聞")

    # Extract hook (the line between header and first ———)
    with open(twitter_file, 'r', encoding='utf-8') as f:
        raw = f.read()
    blocks = re.split(r'\n———\n', raw)
    hook = blocks[0].strip().split('\n')[-1].replace('👇🧵', '').strip() if blocks else ''

    # Resolve paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    boba_dir = os.path.dirname(script_dir)
    port = 18765

    # Setup temp dir for HTML files + static assets
    tmpdir = tempfile.mkdtemp(prefix='boba-ig-')
    shutil.copy(cover_image, os.path.join(tmpdir, 'cover.png'))

    # Copy boba emoji PNG for inline use
    boba_emoji_src = os.path.join(boba_dir, 'img', 'boba-emoji.png')
    if os.path.isfile(boba_emoji_src):
        shutil.copy(boba_emoji_src, os.path.join(tmpdir, 'boba-emoji.png'))

    # Copy bundled font if available
    font_url = ''
    font_src = os.path.join(boba_dir, 'img', 'fonts', 'NotoSansTC.ttf')
    if os.path.isfile(font_src):
        shutil.copy(font_src, os.path.join(tmpdir, 'NotoSansTC.ttf'))
        font_url = f'http://localhost:{port}/NotoSansTC.ttf'

    # Convert logo to PNG (prefer webp over svg to avoid rsvg-convert dependency)
    logo_webp = os.path.join(boba_dir, 'img', 'blue.webp')
    logo_svg = os.path.join(boba_dir, 'img', 'blue.svg')
    logo_src = logo_webp if os.path.exists(logo_webp) else logo_svg
    logo_png = os.path.join(tmpdir, 'logo.png')
    magick_cmd = ['magick', '-background', 'none', logo_src,
                  '-trim', '+repage', '-resize', 'x80', logo_png]
    if logo_src.endswith('.svg'):
        magick_cmd = ['magick', '-background', 'none', '-density', '200',
                      logo_src, '-trim', '+repage', '-resize', 'x80', logo_png]
    subprocess.run(magick_cmd, check=True)
    os.chdir(tmpdir)
    handler = SimpleHTTPRequestHandler
    handler.log_message = lambda *a: None  # silence logs
    server = HTTPServer(('localhost', port), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    # Generate cover (HTML/CSS, with headline + same bottom bar as content slides)
    cover_html = generate_cover_html(
        cover_url=f'http://localhost:{port}/cover.png',
        logo_url=f'http://localhost:{port}/logo.png',
        date=date,
        hook=hook,
        font_url=font_url,
        port=port,
    )
    cover_html_path = os.path.join(tmpdir, 'slide-cover.html')
    with open(cover_html_path, 'w', encoding='utf-8') as f:
        f.write(cover_html)
    cover_output = os.path.join(output_dir, 'slide-00-cover.png')
    chrome_screenshot(cover_html_path, cover_output, port)
    print(f"✅ 封面：{cover_output}")

    # Generate each slide
    for i, story in enumerate(stories, 1):
        html_content = generate_slide_html(
            num=i,
            title=story['title'],
            body=story['body'],
            cover_url=f'http://localhost:{port}/cover.png',
            logo_url=f'http://localhost:{port}/logo.png',
            total=total,
            font_url=font_url,
        )
        html_path = os.path.join(tmpdir, f'slide-{i:02d}.html')
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        output_path = os.path.join(output_dir, f'slide-{i:02d}.png')
        chrome_screenshot(html_path, output_path, port)
        print(f"✅ Slide {i}/{total}：{output_path}")

    server.shutdown()
    shutil.rmtree(tmpdir, ignore_errors=True)

    print(f"\n✅ IG Carousel 完成：{output_dir}/")
    print(f"   封面 + {total} 張內容 slides")

if __name__ == '__main__':
    main()
