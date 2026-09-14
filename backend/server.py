import json, os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse
from store import initialise
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path=urlparse(self.path).path
        if path=='/health':
            status=200; body={'status':'baseline','scanner_implemented':False}
        elif path=='/api/territory':
            status=503; body={'available':False,'reason':'Opportunity scan is not implemented in this baseline','properties':[]}
        else:
            status=404; body={'error':'not_found'}
        self.send_response(status); self.send_header('Content-Type','application/json'); self.end_headers(); self.wfile.write(json.dumps(body).encode())
    def log_message(self, fmt, *args):
        pass
if __name__=='__main__':
    initialise()
    ThreadingHTTPServer(('0.0.0.0',int(os.environ.get('PORT','10000'))),Handler).serve_forever()
