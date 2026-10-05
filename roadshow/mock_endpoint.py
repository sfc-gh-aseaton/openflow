#!/usr/bin/env python3
"""Simple HTTP server that echoes request debug info as JSON."""

import json
import datetime
import socket
import traceback
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs


def _ts():
    return datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]


class DebugHandler(BaseHTTPRequestHandler):

    def setup(self):
        super().setup()
        peer = self.client_address
        print(f"[{_ts()}] CONNECT  {peer[0]}:{peer[1]}")
        self._connect_time = datetime.datetime.utcnow()
        self._raw_data = b""

    def handle(self):
        """Wrap the normal handler to catch low-level failures and dump diagnostics."""
        try:
            # rfile is a plain instance attribute set by StreamRequestHandler.setup();
            # wrapping it here captures every byte the HTTP parser reads.
            self.rfile = _CapturingReader(self.rfile, self)
            super().handle()
        except Exception as exc:
            elapsed = (datetime.datetime.utcnow() - self._connect_time).total_seconds()
            peer = self.client_address
            print(
                f"[{_ts()}] FAIL     {peer[0]}:{peer[1]}  "
                f"after {elapsed:.3f}s — {type(exc).__name__}: {exc}"
            )
            print(f"[{_ts()}]          Traceback:\n{''.join(traceback.format_exc()).rstrip()}")
            if self._raw_data:
                preview = self._raw_data[:512]
                printable = preview.replace(b"\r", b"\\r").replace(b"\n", b"\\n")
                print(
                    f"[{_ts()}]          Raw bytes received ({len(self._raw_data)} total, "
                    f"showing up to 512):\n          {printable.decode('latin-1')}"
                )
            else:
                print(f"[{_ts()}]          No bytes received before failure.")

    def finish(self):
        try:
            super().finish()
        except Exception:
            pass
        elapsed = (datetime.datetime.utcnow() - self._connect_time).total_seconds()
        peer = self.client_address
        print(f"[{_ts()}] CLOSE    {peer[0]}:{peer[1]}  after {elapsed:.3f}s")

    def do_GET(self):
        parsed = urlparse(self.path)
        response = {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "method": self.command,
            "path": parsed.path,
            "query_string": parsed.query or None,
            "query_params": parse_qs(parsed.query) or None,
            "source_ip": self.client_address[0],
            "source_port": self.client_address[1],
            "user_agent": self.headers.get("User-Agent"),
            "host": self.headers.get("Host"),
            "accept": self.headers.get("Accept"),
            "headers": dict(self.headers),
        }

        body = json.dumps(response, indent=2).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        print(f"[{_ts()}] REQUEST  {self.client_address[0]}:{self.client_address[1]} — {fmt % args}")

    def log_error(self, fmt, *args):
        peer = self.client_address
        print(f"[{_ts()}] ERROR    {peer[0]}:{peer[1]} — {fmt % args}")


class _CapturingReader:
    """Thin wrapper around the socket file object that records bytes as they're read."""

    def __init__(self, inner, handler):
        self._inner = inner
        self._handler = handler

    def readline(self, *args, **kwargs):
        data = self._inner.readline(*args, **kwargs)
        self._handler._raw_data += data
        return data

    def read(self, *args, **kwargs):
        data = self._inner.read(*args, **kwargs)
        self._handler._raw_data += data
        return data

    def __getattr__(self, name):
        return getattr(self._inner, name)


class VerboseHTTPServer(HTTPServer):
    def handle_error(self, request, client_address):
        print(
            f"[{_ts()}] SERVER_ERROR  {client_address[0]}:{client_address[1]}\n"
            + "".join(traceback.format_exc()).rstrip()
        )


if __name__ == "__main__":
    server = VerboseHTTPServer(("0.0.0.0", 8080), DebugHandler)
    print("Listening on http://0.0.0.0:8080")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
