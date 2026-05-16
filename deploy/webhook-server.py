import hmac
import hashlib
import subprocess
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

SECRET = b"CHANGE_THIS_TO_RANDOM_STRING"
REPO_DIR = "/opt/customer-service"

class WebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/deploy":
            self.send_response(404); self.end_headers(); return
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        
        # 验证 Gitee webhook 签名
        sign = self.headers.get("X-Gitee-Token", "")
        if sign != SECRET.decode():
            self.send_response(403)
            self.end_headers()
            self.wfile.write(b"Invalid token")
            return
        
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK - deploying")
        
        # 异步部署（避免webhook超时）
        subprocess.Popen(["/bin/bash", os.path.join(REPO_DIR, "deploy", "deploy-from-git.sh")])

    def log_message(self, format, *args):
        print(f"[Webhook] {args[0]}")

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 9000), WebhookHandler)
    print("Webhook server on :9000")
    server.serve_forever()
