"""Web chat for jev_llm.  Stdlib only.  `python server.py` then open http://localhost:8000

POST /api/chat  {"key": "...", "messages": [{role, content}...], "max_words": 60}
    -> text/event-stream of {"text": "...", "rounds": n, "seconds": s} then {"done": true, "stats": {...}}
The key is used for that request's TypeSafe calls and nothing else; it is never logged or stored.
If the request has no key, TYPESAFE_API_KEY from the environment is used (self-hosted mode).
"""
import json, os, sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from jev_llm import HERE, Generator, Jev, api_key, load_vocab

BASE_GROUPS = load_vocab(16)  # ponytail: parse words.txt once, not per request
try:
    SERVER_KEY = api_key()  # self-hosted mode: env var or .env; visitors then need no key of their own
except SystemExit:
    SERVER_KEY = ""


class Handler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        if self.path == "/api/config":
            body = json.dumps({"server_key": bool(SERVER_KEY)}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            return self.wfile.write(body)
        if self.path.split("?")[0] not in ("/", "/index.html"):
            return self.send_error(404)
        body = open(os.path.join(HERE, "index.html"), "rb").read()  # re-read so edits show without restart
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.path != "/api/chat":
            return self.send_error(404)
        try:
            req = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0)) or b"{}"))
            messages = [{"role": m["role"], "content": str(m["content"])} for m in req["messages"]]
            assert messages and messages[-1]["role"] == "user"
        except Exception:
            return self.send_error(400, "bad request")
        key = (req.get("key") or SERVER_KEY).strip()
        if not key:
            return self.send_error(401, "no API key")
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("X-Accel-Buffering", "no")
        self.end_headers()

        def emit(obj):
            self.wfile.write(f"data: {json.dumps(obj)}\n\n".encode())
            self.wfile.flush()

        gen = Generator(BASE_GROUPS, jev=Jev(key))
        try:
            emit({"text": "", "rounds": 0, "seconds": 0})
            reply, stats = gen.generate(
                messages[-1]["content"], messages[:-1], max_words=min(int(req.get("max_words", 60)), 120),
                on_token=lambda t: emit({"text": t, "rounds": gen.jev.rounds, "seconds": round(gen.jev.seconds, 1)}))
            emit({"text": reply, "done": True, "stats": stats})
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            pass  # client hit stop; generate() unwinds on the next emit
        except Exception as e:
            try:
                emit({"error": str(e)})
            except OSError:
                pass

    def log_message(self, fmt, *args):
        if args and str(args[1:2]) not in ("('200',)",):
            sys.stderr.write("%s %s\n" % (self.address_string(), fmt % args))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"jev-llm chat on http://localhost:{port}", flush=True)
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
