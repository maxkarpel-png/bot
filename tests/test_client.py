import json
import threading
import unittest
from dataclasses import replace
from http.server import BaseHTTPRequestHandler, HTTPServer

from polymarket_bot.client import PolymarketClient
from polymarket_bot.config import load_config


class _Handler(BaseHTTPRequestHandler):
    last_method = ""
    last_body = b""

    def do_GET(self):  # noqa: N802
        _Handler.last_method = "GET"
        length = int(self.headers.get("Content-Length") or "0")
        _Handler.last_body = self.rfile.read(length)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"yes": [{"price": "0.4", "size": "2"}], "no": []}).encode("utf-8"))

    def log_message(self, format, *args):  # noqa: A003
        return


class TestClient(unittest.TestCase):
    def test_get_request_has_no_body(self) -> None:
        server = HTTPServer(("127.0.0.1", 0), _Handler)
        thread = threading.Thread(target=server.serve_forever)
        thread.daemon = True
        thread.start()
        try:
            base = f"http://127.0.0.1:{server.server_port}"
            config = replace(load_config(), base_url=base)
            client = PolymarketClient(config)
            client.get_orderbook("abc")
            self.assertEqual(_Handler.last_method, "GET")
            self.assertEqual(_Handler.last_body, b"")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)


if __name__ == "__main__":
    unittest.main()
