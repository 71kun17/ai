import json, os, sys, time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.request import Request, urlopen
from urllib.error import HTTPError

KEY = os.environ.get("DEEPSEEK_KEY", "")
URL = "https://api.deepseek.com/v1/chat/completions"
ROLE_MAP = {"developer": "system"}
MODEL_MAP = {"gpt-5.5": "deepseek-v4-pro", "gpt-5.4": "deepseek-v4-pro",
             "gpt-5.1": "deepseek-v4-pro", "gpt-5": "deepseek-v4-pro",
             "gpt-5.2": "deepseek-v4-pro", "gpt-5.3-codex": "deepseek-v4-pro",
             "o1": "deepseek-v4-pro", "o3": "deepseek-v4-pro", "o4-mini": "deepseek-v4-pro",
             "gpt-5.4-mini": "deepseek-v4-flash"}

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            cl = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(cl))
            msgs = []
            inp = body.get("input", [])
            if isinstance(inp, dict): inp = [inp]
            for item in inp:
                if isinstance(item, dict):
                    role = ROLE_MAP.get(item.get("role","user"), item.get("role","user"))
                    content = item.get("content", "")
                    if isinstance(content, list):
                        parts = [p.get("text","") for p in content if isinstance(p,dict) and p.get("type","") in ("input_text","output_text","text")]
                        content = "\n".join(parts) if parts else ""
                    msgs.append({"role": role, "content": content})
            inst = body.get("instructions", "")
            if inst: msgs.insert(0, {"role": "system", "content": inst})

            model = MODEL_MAP.get(body.get("model", ""), body.get("model", "deepseek-v4-pro"))
            is_stream = body.get("stream", True)

            cr = {"model": model, "messages": msgs, "stream": is_stream}
            for k in ["max_output_tokens","max_tokens","temperature","top_p"]:
                if k in body:
                    cr["max_tokens" if k=="max_output_tokens" else k] = body[k]

            ak = self.headers.get("Authorization","").replace("Bearer ","") or KEY

            if is_stream:
                self._do_stream(cr, ak)
            else:
                self._do_sync(cr, ak)
        except Exception as e:
            import traceback; traceback.print_exc()
            self.send_response(500); self.end_headers()

    def _do_sync(self, cr, ak):
        r = Request(URL, data=json.dumps(cr).encode(),
                    headers={"Content-Type":"application/json","Authorization":f"Bearer {ak}"})
        resp = urlopen(r, timeout=120)
        crs = json.loads(resp.read())
        ch = crs.get("choices",[{}])[0]
        msg = ch.get("message",{})
        out = {"id":crs.get("id",""),"object":"response","model":crs.get("model",""),
               "output":[{"type":"message","id":crs.get("id",""),"status":"completed",
               "role":"assistant","content":[{"type":"output_text","text":msg.get("content","")}]}],
               "usage":crs.get("usage",{})}
        self.send_response(200)
        self.send_header("Content-Type","application/json")
        self.end_headers()
        self.wfile.write(json.dumps(out).encode())

    def _do_stream(self, cr, ak):
        r = Request(URL, data=json.dumps(cr).encode(),
                    headers={"Content-Type":"application/json","Authorization":f"Bearer {ak}"})
        resp = urlopen(r, timeout=600)
        self.send_response(200)
        self.send_header("Content-Type","text/event-stream")
        self.send_header("Cache-Control","no-cache")
        self.send_header("X-Accel-Buffering","no")
        self.end_headers()

        rid = f"resp_{int(time.time()*1000)}"
        mid = f"msg_{int(time.time()*1000)}"
        full_text = ""
        model_used = cr.get("model", "")
        usage = {}
        chunk = None

        try:
            for line in resp:
                line = line.decode("utf-8", errors="ignore").strip()
                if not line: continue
                if not line.startswith("data:"): continue
                data_str = line[5:].strip()
                if data_str == "[DONE]": break
                try:
                    chunk = json.loads(data_str)
                    choices = chunk.get("choices", [])
                    if not choices: continue
                    delta = choices[0].get("delta", {})
                    text = delta.get("content", "")
                    if text:
                        full_text += text
                        evt = {"type":"response.output_text.delta","item_id":mid,
                               "output_index":0,"content_index":0,"delta":text}
                        self.wfile.write(f"data: {json.dumps(evt, ensure_ascii=False)}\n\n".encode("utf-8"))
                        self.wfile.flush()
                    if "usage" in chunk:
                        usage = chunk["usage"]
                except json.JSONDecodeError:
                    pass

            done_evt = {"type":"response.completed","response":{
                "id":rid,"object":"response","model":model_used,
                "output":[{"type":"message","id":mid,"status":"completed",
                "role":"assistant","content":[{"type":"output_text","text":full_text}]}],
                "usage":usage}}
            self.wfile.write(f"data: {json.dumps(done_evt, ensure_ascii=False)}\n\n".encode("utf-8"))
            self.wfile.write(b"data: [DONE]\n\n")
            self.wfile.flush()
        except Exception as e:
            import traceback; traceback.print_exc()

    def log_message(self, f, *a):
        print(f"[Proxy] {a[0]}", flush=True)

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
    print(f"DeepSeek Proxy on 127.0.0.1:{port}", flush=True)
    HTTPServer(("127.0.0.1", port), Handler).serve_forever()