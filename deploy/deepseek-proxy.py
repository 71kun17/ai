import json, os, sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.request import Request, urlopen
from urllib.error import HTTPError

DEEPSEEK_KEY = os.environ.get("DEEPSEEK_KEY", "")
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"

class ProxyHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        body_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(body_len)
        req_json = json.loads(body)
        messages = []
        input_val = req_json.get("input", [])
        if isinstance(input_val, list):
            for item in input_val:
                if isinstance(item, dict):
                    role = item.get("role", "user")
                    content = item.get("content", "")
                    if isinstance(content, list):
                        text_parts = [p.get("text", "") for p in content if p.get("type") == "input_text"]
                        content = "\n".join(text_parts)
                    messages.append({"role": role, "content": content})
        chat_req = {
            "model": req_json.get("model", "deepseek-chat"),
            "messages": messages,
            "stream": req_json.get("stream", False),
        }
        for key in ["max_tokens", "temperature", "top_p"]:
            if key in req_json:
                chat_req[key] = req_json[key]
        auth_key = self.headers.get("Authorization", "").replace("Bearer ", "") or DEEPSEEK_KEY
        req = Request(DEEPSEEK_URL, data=json.dumps(chat_req).encode(),
                      headers={"Content-Type": "application/json",
                               "Authorization": f"Bearer {auth_key}"})
        try:
            resp = urlopen(req, timeout=120)
            chat_resp = json.loads(resp.read())
            choice = chat_resp.get("choices", [{}])[0]
            msg = choice.get("message", {})
            output = [{
                "type": "message",
                "id": chat_resp.get("id", ""),
                "status": "completed",
                "role": "assistant",
                "content": [{"type": "output_text", "text": msg.get("content", "")}]
            }]
            responses_format = {
                "id": chat_resp.get("id", ""),
                "object": "response",
                "model": chat_resp.get("model", ""),
                "output": output,
                "usage": chat_resp.get("usage", {}),
            }
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(responses_format).encode())
        except HTTPError as e:
            self.send_response(e.code)
            self.end_headers()
            self.wfile.write(e.read())

    def log_message(self, format, *args):
        print(f"[Proxy] {args[0]}")

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
    server = HTTPServer(("127.0.0.1", port), ProxyHandler)
    print(f"DeepSeek Proxy on 127.0.0.1:{port}")
    server.serve_forever()