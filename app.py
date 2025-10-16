from flask import Flask, request, Response
import requests
from urllib.parse import quote
import re

app = Flask(__name__)

def detect_m3u_type(content):
    if "#EXTM3U" in content and "#EXTINF" in content:
        return "m3u8"
    return "m3u"

def replace_key_uri(line, headers_query):
    match = re.search(r'URI="([^"]+)"', line)
    if match:
        key_url = match.group(1)
        proxied_key_url = f"/proxy/key?url={quote(key_url)}&{headers_query}"
        return line.replace(key_url, proxied_key_url)
    return line

def resolve_m3u8_link(url, headers=None):
    if not url:
        return {"resolved_url": None, "headers": {}}
    current_headers = headers if headers else {"User-Agent": "Mozilla/5.0"}
    try:
        with requests.Session() as session:
            response = session.get(url, headers=current_headers, allow_redirects=True, timeout=(5, 15))
            response.raise_for_status()
            if response.text.strip().startswith("#EXTM3U"):
                return {"resolved_url": response.url, "headers": current_headers}
    except Exception as e:
        print("Errore:", e)
    return {"resolved_url": url, "headers": current_headers}

@app.route("/proxy")
def proxy():
    m3u_url = request.args.get("url", "").strip()
    if not m3u_url:
        return "Errore: Parametro url mancante", 400
    try:
        server_ip = request.host
        response = requests.get(m3u_url, timeout=(10, 30))
        response.raise_for_status()
        m3u_content = response.text
        modified_lines = []
        for line in m3u_content.splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                modified_line = f"http://{server_ip}/proxy/m3u?url={line}"
                modified_lines.append(modified_line)
            else:
                modified_lines.append(line)
        modified_content = "\n".join(modified_lines)
        return Response(modified_content, content_type="application/vnd.apple.mpegurl")
    except Exception as e:
        return f"Errore: {str(e)}", 500

@app.route("/")
def index():
    return "Proxy started!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860, debug=False)
