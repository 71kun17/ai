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

        body = self.rfile.read(int(self.headers.get("Content-Length", 0)))

        # GitHub: X-Hub-Signature-256 (HMAC-SHA256)
        sig = self.headers.get("X-Hub-Signature-256", "")
        if sig:
            expected = "sha256=" + hmac.new(SECRET, body, hashlib.sha256).hexdigest()
            if not hmac.compare_digest(sig, expected):
                self.send_response(403); self.end_headers()
                self.wfile.write(b"Invalid signature")
                return
        else:
            # Gitee fallback: X-Gitee-Token
            token = self.headers.get("X-Gitee-Token", "")
            if token != SECRET.decode():
                self.send_response(403); self.end_headers()
                self.wfile.write(b"Invalid token")
                return

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK - deploying")

        subprocess.Popen(["/bin/bash", os.path.join(REPO_DIR, "deploy", "deploy-from-git.sh")])

    def log_message(self, format, *args):
        print(f"[Webhook] {args[0]}")

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 9000), WebhookHandler)
    print("Webhook server on :9000 (GitHub + Gitee compatible)")
    server.serve_forever()
