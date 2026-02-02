from http.server import BaseHTTPRequestHandler
import requests
import json
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Ambil parameter domain dari URL
        query = parse_qs(urlparse(self.path).query)
        target = query.get('domain', [None])[0]

        if not target:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Domain parameter is required")
            return

        # Ambil data dari crt.sh
        url = f"https://crt.sh/?q=%.{target}&output=json"
        
        try:
            response = requests.get(url, timeout=15)
            data = response.json()
            
            # Cleaning data (ambil unique subdomains saja)
            subdomains = set()
            for entry in data:
                # crt.sh seringkali punya multiple domains dipisah \n
                names = entry['name_value'].split('\n')
                for name in names:
                    if name.endswith(target) and "*" not in name:
                        subdomains.add(name)

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*') # Biar bisa dipanggil dari frontend
            self.end_headers()
            
            self.wfile.write(json.dumps(sorted(list(subdomains))).encode())
        
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())
