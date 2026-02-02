from http.server import BaseHTTPRequestHandler
import requests
import json
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Ambil parameter dari URL
        parsed_path = urlparse(self.path)
        query = parse_qs(parsed_path.query)
        target = query.get('domain', [None])[0]

        if not target:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Domain is required"}).encode())
            return

        # Request ke crt.sh
        url = f"https://crt.sh/?q=%.{target}&output=json"
        
        try:
            # Timeout ditambah biar nggak gampang mati
            response = requests.get(url, timeout=20)
            
            if response.status_code != 200:
                raise Exception("crt.sh is busy")

            data = response.json()
            subdomains = set()
            for entry in data:
                names = entry['name_value'].split('\n')
                for name in names:
                    # Filter: hapus wildcard dan pastikan domain cocok
                    clean_name = name.replace("*.", "")
                    if clean_name.endswith(target):
                        subdomains.add(clean_name.lower())

            # Response sukses
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            result = sorted(list(subdomains))
            self.wfile.write(json.dumps(result).encode())
        
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
