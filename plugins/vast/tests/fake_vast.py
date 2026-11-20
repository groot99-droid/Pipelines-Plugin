"""A fake Vast.ai API on 127.0.0.1 for the tests: offers, instances, and a record of every request.

It checks the Bearer key on every call and answers 401 to any other, so a test can prove the
server sends the key it read and nothing else.
"""

from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

FAKE_KEY = "fake-vast-key-0123456789abcdef"


class FakeVast:
    def __init__(self):
        self.offers = [
            {"id": 101, "gpu_name": "RTX 3090", "num_gpus": 1, "gpu_ram": 24576, "dph_total": 0.25,
             "reliability2": 0.995, "verified": None, "verification": "verified", "geolocation": "US",
             "cpu_ram": 65536, "disk_space": 200, "inet_down": 900, "cuda_max_good": 12.4,
             "storage_cost": 0.146},     # the live shape: `verified` null, $/GB/month for the disk
            {"id": 202, "gpu_name": "RTX 4090", "num_gpus": 1, "gpu_ram": 24564, "dph_total": 1.20,
             "reliability2": 0.99, "verified": True, "geolocation": "DE", "cpu_ram": 65536,
             "disk_space": 300, "inet_down": 2000, "cuda_max_good": 12.2},
            {"id": 303, "gpu_name": "H100 SXM", "num_gpus": 1, "gpu_ram": 81920, "dph_total": 12.0,
             "reliability2": 0.99, "verified": True, "geolocation": "US", "cpu_ram": 262144,
             "disk_space": 1000, "inet_down": 5000, "cuda_max_good": 12.4},
        ]
        self.instances = {}
        self.requests = []
        self.next_id = 9000
        self.user = {"balance": 42.5, "credit": 0.0, "email": "someone@example.com", "api_key": "never-shown"}
        self.lock = threading.Lock()

    def start(self):
        fake = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def _reply(self, code, payload):
                body = json.dumps(payload).encode()
                self.send_response(code)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def _handle(self):
                length = int(self.headers.get("Content-Length") or 0)
                body = json.loads(self.rfile.read(length) or b"null") if length else None
                with fake.lock:
                    fake.requests.append({"method": self.command, "path": self.path, "body": body,
                                          "auth": self.headers.get("Authorization")})
                    if self.headers.get("Authorization") != "Bearer " + FAKE_KEY:
                        return self._reply(401, {"msg": "bad key"})
                    code, payload = fake.route(self.command, self.path.split("?")[0], body)
                self._reply(code, payload)

            do_GET = do_PUT = do_POST = do_DELETE = _handle

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True)
        self.thread.start()
        return f"http://127.0.0.1:{self.server.server_address[1]}/api/v0"

    def stop(self):
        self.server.shutdown()
        self.server.server_close()

    def route(self, method, path, body):
        parts = [p for p in path.split("/") if p][2:]  # drop api, v0
        if method == "GET" and parts == ["users", "current"]:
            return 200, self.user
        if method == "PUT" and parts == ["search", "asks"]:
            query = (body or {}).get("q", {})
            offers = list(self.offers)
            if "id" in query:      # the live API matches nothing on `id`
                offers = []
            if "ask_contract_id" in query:
                offers = [o for o in offers if o["id"] == query["ask_contract_id"]["eq"]]
            if "dph_total" in query:
                offers = [o for o in offers if o["dph_total"] <= query["dph_total"]["lte"]]
            if "cuda_max_good" in query:
                offers = [o for o in offers if o["cuda_max_good"] >= query["cuda_max_good"]["gte"]]
            if "gpu_name" in query:
                offers = [o for o in offers if o["gpu_name"] == query["gpu_name"]["eq"]]
            return 200, {"offers": sorted(offers, key=lambda o: o["dph_total"])}
        if method == "PUT" and len(parts) == 2 and parts[0] == "asks":
            offer = next((o for o in self.offers if o["id"] == int(parts[1])), None)
            if offer is None:
                return 404, {"msg": "no such ask"}
            self.next_id += 1
            self.instances[self.next_id] = {"id": self.next_id, "actual_status": "running",
                                            "ssh_host": "ssh5.vast.ai", "ssh_port": 31000 + self.next_id % 1000,
                                            "gpu_name": offer["gpu_name"], "dph_total": offer["dph_total"],
                                            "label": body.get("label"), "onstart": body.get("onstart"),
                                            "image": body.get("image")}
            return 200, {"success": True, "new_contract": self.next_id}
        if method == "GET" and parts == ["instances"]:
            return 200, {"instances": list(self.instances.values())}
        if len(parts) == 2 and parts[0] == "instances":
            instance = self.instances.get(int(parts[1]))
            if method == "GET":
                return 200, {"instances": instance}
            if instance is None:
                return 404, {"msg": "no such instance"}
            if method == "PUT":
                instance["actual_status"] = "stopped" if (body or {}).get("state") == "stopped" else instance["actual_status"]
                return 200, {"success": True}
            if method == "DELETE":
                del self.instances[int(parts[1])]
                return 200, {"success": True}
        if method == "POST" and len(parts) == 3 and parts[0] == "instances" and parts[2] == "ssh":
            return 200, {"success": True}
        return 404, {"msg": "not routed: " + method + " " + path}
