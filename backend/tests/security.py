"""Resource-contained HTTP regression tests. Run after `cargo build` with inference requirements installed.

Uses only loopback and temporary data. The executable shim injects controlled inference
failures/delays, but delegates image validation and normal inference to the real script.
"""
import concurrent.futures
import http.client
import io
import json
import os
from pathlib import Path
import resource
import socket
import subprocess
import sys
import tempfile
import time
import unittest

from PIL import Image

BACKEND = Path(__file__).resolve().parents[1]
BINARY = Path(os.environ.get("BACKEND_BINARY", BACKEND / "target/debug/Cricket-Ready-Backend"))


def contained():
    resource.setrlimit(resource.RLIMIT_AS, (2 * 1024**3, 2 * 1024**3))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def picture(fmt="JPEG", size=(43, 31)):
    buffer = io.BytesIO()
    Image.new("RGB", size, (147, 36, 71)).save(buffer, fmt)
    return buffer.getvalue()


class Security(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)
        self.pending = self.root / "pending"
        self.temp = self.root / "tmp"
        self.temp.mkdir()
        (self.root / "nn-classifier").symlink_to(BACKEND / "nn-classifier", target_is_directory=True)
        self.mode = self.root / "mode"
        self.mode.write_text("real")
        self.shim = self.root / "python"
        self.shim.write_text(f'''#!{sys.executable}
import os, pathlib, sys, time
mode = pathlib.Path({str(self.mode)!r}).read_text()
validation = sys.argv[2] in ("--normalize", "--validate")
if mode == "validation-hang" or (not validation and mode == "hang"):
    pathlib.Path({str(self.root / 'child.pid')!r}).write_text(str(os.getpid()))
    time.sleep(90)
if not validation and mode == "fail":
    print("PRIVATE DIAGNOSTIC /secret/model.pth", file=sys.stderr)
    sys.exit(1)
if not validation and mode == "invalid":
    print('{{"prediction":"unknown","confidence":3}}')
    sys.exit(0)
os.execv({sys.executable!r}, [{sys.executable!r}] + sys.argv[1:])
''')
        self.shim.chmod(0o700)
        self.log = open(self.root / "server.log", "w+")
        self.start()

    def start(self):
        env = dict(os.environ, HTTP_LOOPBACK="1", PYTHON_EXECUTABLE=str(self.shim),
                   TRAINING_PENDING_DIR=str(self.pending), TMPDIR=str(self.temp),
                   OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1", MKL_NUM_THREADS="1")
        self.server = subprocess.Popen([str(BINARY)], cwd=self.root, env=env,
                                       stdout=self.log, stderr=self.log, preexec_fn=contained)
        for _ in range(100):
            if self.server.poll() is not None:
                self.fail("Server failed: " + (self.root / "server.log").read_text())
            try:
                with socket.create_connection(("127.0.0.1", 49161), timeout=.1):
                    return
            except OSError:
                time.sleep(.05)
        self.fail("Server did not listen")

    def stop(self):
        self.server.terminate()
        self.server.wait(timeout=10)

    def tearDown(self):
        self.stop()
        self.log.close()
        self.directory.cleanup()

    def request(self, fields, route="/training", headers=None):
        body = b""
        for name, value in fields:
            body += f'--boundary\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n'.encode() + value + b"\r\n"
        body += b"--boundary--\r\n"
        connection = http.client.HTTPConnection("127.0.0.1", 49161, timeout=75)
        connection.request("POST", route, body, {"Content-Type": "multipart/form-data; boundary=boundary", **(headers or {})})
        result = connection.getresponse()
        answer = (result.status, result.read(), dict(result.getheaders()))
        connection.close()
        return answer

    def contribute(self, image=None, label=b"match_ready"):
        return self.request([("image", image if image is not None else picture()), ("label", label)])

    def test_contributions_normalized_quarantined_unique_and_persistent(self):
        for fmt, label in [("JPEG", b"match_ready"), ("PNG", b"not_match_ready")]:
            status, body, _ = self.contribute(picture(fmt) + b"PRIVATE TRAILING DATA", label)
            self.assertEqual(status, 200, body)
            value = json.loads(body)
            self.assertEqual(value["review_status"], "pending")
            path = self.pending / label.decode() / value["filename"]
            self.assertNotIn(b"PRIVATE", path.read_bytes())
            with Image.open(path) as image:
                self.assertEqual((image.format, image.size), ("JPEG", (43, 31)))
        previous = list(self.pending.glob("*/*.jpg"))
        self.assertEqual(self.contribute()[0], 200)
        self.assertEqual(len(list(self.pending.glob("*/*.jpg"))), 3)
        self.stop()
        self.start()
        self.assertTrue(all(path.exists() for path in previous))
        self.assertFalse((self.root / "dataset").exists())
        self.assertEqual(list(self.temp.iterdir()), [])

    def test_fields_bytes_and_invalid_content(self):
        for fields in [[], [("image", b"")], [("image", picture())],
                       [("image", picture()), ("label", b"../escape")],
                       [("image", picture()), ("image", picture())],
                       [("image", picture()), ("label", b"match_ready"), ("label", b"match_ready")],
                       [("extra", b"x")]]:
            self.assertEqual(self.request(fields)[0], 400)
        self.assertEqual(self.contribute(b"x" * (5 * 1024 * 1024 + 1))[0], 413)
        self.assertEqual(self.contribute(label=b"x" * 16)[0], 413)
        self.assertEqual(self.contribute(b"not an image")[0], 400)
        self.assertEqual(self.contribute(picture()[:-50])[0], 400)
        # Exactly the byte cap reaches validation, rather than the size rejection.
        self.assertEqual(self.contribute(b"x" * (5 * 1024 * 1024))[0], 400)

    def test_formats_and_dimension_boundaries(self):
        for fmt in ["BMP", "GIF", "TIFF", "WEBP"]:
            self.assertEqual(self.contribute(picture(fmt))[0], 400, fmt)
        for size, status in [((4096, 1), 200), ((4097, 1), 400),
                             ((3000, 4000), 200), ((3001, 4000), 400)]:
            self.assertEqual(self.contribute(picture("PNG", size))[0], status, size)
        animated = io.BytesIO()
        Image.new("RGB", (2, 3)).save(animated, "PNG", save_all=True,
                                     append_images=[Image.new("RGB", (2, 3), "red")])
        self.assertEqual(self.contribute(animated.getvalue())[0], 400)

    def test_quotas_and_retention(self):
        target = self.pending / "match_ready"
        for number in range(500):
            (target / f"{number}.jpg").write_bytes(b"x")
        self.assertEqual(self.contribute()[0], 503)
        for path in target.iterdir():
            os.utime(path, (time.time() - 8 * 86400,) * 2)
        self.assertEqual(self.contribute()[0], 200)
        self.assertEqual(len(list(target.iterdir())), 1)
        for path in target.iterdir():
            path.unlink()
        large = target / "quota.jpg"
        with large.open("wb") as file:
            file.truncate(256 * 1024 * 1024)
        self.assertEqual(self.contribute()[0], 503)

    def test_real_prediction_and_safe_failures(self):
        status, body, _ = self.request([("image", picture())], "/predict")
        self.assertEqual(status, 200, body)
        value = json.loads(body)
        self.assertIn(value["prediction"], ["match_ready", "not_match_ready"])
        self.assertTrue(0 <= value["confidence"] <= 1)
        for mode in ["fail", "invalid"]:
            self.mode.write_text(mode)
            status, body, _ = self.request([("image", picture())], "/predict")
            self.assertEqual((status, body), (500, b"Image processing failed"))
        self.assertIn("PRIVATE DIAGNOSTIC", (self.root / "server.log").read_text())
        self.shim.unlink()
        self.assertEqual(self.request([("image", picture())], "/predict")[0], 500)
        self.assertEqual(list(self.temp.iterdir()), [])

    def test_timeout_concurrency_and_cleanup(self):
        self.mode.write_text("hang")
        with concurrent.futures.ThreadPoolExecutor() as pool:
            future = pool.submit(self.request, [("image", picture())], "/predict")
            pidfile = self.root / "child.pid"
            for _ in range(100):
                if pidfile.exists(): break
                time.sleep(.05)
            self.assertTrue(pidfile.exists())
            self.assertEqual(self.request([("image", picture())], "/predict")[0], 503)
            self.assertEqual(self.contribute()[0], 200)
            self.assertEqual(future.result()[0], 504)
        with self.assertRaises(ProcessLookupError):
            os.kill(int(pidfile.read_text()), 0)
        self.mode.write_text("real")
        self.assertEqual(self.contribute()[0], 200)
        self.assertEqual(list(self.temp.iterdir()), [])

    def test_validation_deadline_and_admission(self):
        self.mode.write_text("validation-hang")
        with concurrent.futures.ThreadPoolExecutor() as pool:
            requests = [pool.submit(self.contribute) for _ in range(2)]
            time.sleep(1)
            self.assertEqual(self.contribute()[0], 503)
            self.assertEqual([r.result()[0] for r in requests], [504, 504])
        self.assertEqual(list(self.temp.iterdir()), [])

    def test_cors_and_rate_limit(self):
        connection = http.client.HTTPConnection("127.0.0.1", 49161)
        connection.request("OPTIONS", "/training", headers={"Origin": "https://alexheffernan.dev",
            "Access-Control-Request-Method": "POST", "Access-Control-Request-Headers": "ngrok-skip-browser-warning,content-type"})
        result = connection.getresponse()
        self.assertEqual(result.status, 200)
        self.assertEqual(result.getheader("access-control-allow-origin"), "https://alexheffernan.dev")
        result.read()
        connection.close()
        self.assertNotIn("access-control-allow-origin", self.request([], headers={"Origin": "https://evil.invalid"})[2])
        statuses = [self.request([])[0] for _ in range(25)]
        self.assertIn(429, statuses)


if __name__ == "__main__":
    unittest.main(verbosity=2)
