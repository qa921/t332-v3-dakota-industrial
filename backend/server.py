import json, os, hmac
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
from store import initialise
from provider import scan_nearby
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed=urlparse(self.path)
        path=parsed.path
        if path=='/health':
            status=200; body={'status':'ok','scanner_implemented':True}
        elif path=='/api/territory' and (not os.environ.get('ACCESS_TOKEN') or not hmac.compare_digest(self.headers.get('Authorization',''),'Bearer '+os.environ['ACCESS_TOKEN'])):
            status=401; body={'error':'unauthorized'}
        elif path=='/api/territory':
            query=parse_qs(parsed.query)
            result=scan_nearby(
                (query.get('lat') or [None])[0],
                (query.get('lon') or [None])[0],
                (query.get('radius_km') or [None])[0],
                (query.get('min_age') or [None])[0],
                (query.get('limit') or [None])[0],
            )
            status=200 if result.get('available') else 503
            body=result
        else:
            status=404; body={'error':'not_found'}
        self.send_response(status); self.send_header('Content-Type','application/json'); self.send_header('Cache-Control','no-store'); self.send_header('X-Content-Type-Options','nosniff'); self.end_headers(); self.wfile.write(json.dumps(body).encode())
    def log_message(self, fmt, *args):
        pass
if __name__=='__main__':
    initialise()
    ThreadingHTTPServer(('0.0.0.0',int(os.environ.get('PORT','10000'))),Handler).serve_forever()
