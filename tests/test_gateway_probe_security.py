"""Adversarial gateway probe tests for redirected bearer and URL validation."""
import importlib.util
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
import unittest

source=Path(__file__).resolve().parents[1]/"scripts"/"collective_gateway_probe.py"
spec=importlib.util.spec_from_file_location("probe_for_security_test",source)
probe=importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


class ProbeSecurityTests(unittest.TestCase):
    def test_rejects_gateway_path_or_port_smuggling(self):
        episode="collective-"+"a"*32
        for base in ("https://example.org/route", "https://example.org:bad",
                     "https://user:pass@example.org", "http://192.0.2.5",
                     "http://localhost.evil.org"):
            with self.subTest(base=base):
                with self.assertRaises(ValueError):
                    probe.probe(base,episode,"synthetic-test-bearer-123456")

    def test_rejects_ambiguous_episode_id(self):
        for episode in ("collective-abc", "collective-../x",
                        "collective-"+("x"*32), "collective-"+("a"*33)):
            with self.subTest(episode=episode):
                with self.assertRaises(ValueError):
                    probe.probe("https://example.org",episode,"synthetic-test-bearer-123456")

    def test_cross_origin_redirect_cannot_receive_worker_bearer(self):
        episode="collective-"+"b"*32
        token="synthetic-test-bearer-123456"
        captured=[]
        class Destination(BaseHTTPRequestHandler):
            def log_message(self,*_):pass
            def do_GET(self):
                captured.append(self.headers.get("Authorization"))
                raw=json.dumps({"episode_id":episode,"agent_id":"lappy"}).encode()
                self.send_response(200)
                self.send_header("Content-Length",str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)
        destination=ThreadingHTTPServer(("127.0.0.1",0),Destination)
        class Gateway(BaseHTTPRequestHandler):
            def log_message(self,*_):pass
            def do_GET(self):
                if self.path=="/healthz":
                    raw=b'{"service":"rezon-collective","status":"alive"}'
                    self.send_response(200)
                    self.send_header("Content-Length",str(len(raw)))
                    self.end_headers()
                    self.wfile.write(raw)
                else:
                    self.send_response(302)
                    self.send_header("Location",f"http://127.0.0.1:{destination.server_port}/stolen")
                    self.end_headers()
        gateway=ThreadingHTTPServer(("127.0.0.1",0),Gateway)
        threads=[Thread(target=s.serve_forever,daemon=True) for s in (destination,gateway)]
        for t in threads:t.start()
        try:
            try:
                result=probe.probe(f"http://127.0.0.1:{gateway.server_port}",episode,token)
            except Exception:
                result={}
            self.assertEqual(captured,[],"Bearer was forwarded to a redirect destination")
            self.assertNotEqual(result.get("episode"),"authorized")
        finally:
            for s in (gateway,destination):s.shutdown();s.server_close()
            for t in threads:t.join(timeout=5)
