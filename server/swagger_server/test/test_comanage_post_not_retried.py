"""fabric-comanage-api >= 0.3.0 must not retry POST (1.x hotfix).

0.2.0 retried POST on 429/5xx. A COU or role create that landed in COmanage
but answered 5xx was replayed, which can leave a duplicate COU or role. Reads,
PUTs and DELETEs are idempotent and keep their retries.

Drives the real client against a local stub registry. Like the other 1.x
hotfix tests, main cannot collect it (its test package imports
flask_testing); verify it with the v2-develop toolchain.
"""

import http.server
import threading

import pytest
import requests
from comanage_api import ComanageApi


class _Stub(http.server.BaseHTTPRequestHandler):
    hits = []

    def _answer(self):
        self.rfile.read(int(self.headers.get("Content-Length", 0)))
        _Stub.hits.append(self.command)
        status, body = int(self.path.split("/")[1]), b"{}"
        self.send_response(status)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    do_GET = do_POST = _answer

    def log_message(self, *args):
        pass


@pytest.fixture(scope="module")
def registry():
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), _Stub)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield "http://127.0.0.1:{0}".format(server.server_address[1])
    server.shutdown()


@pytest.fixture(autouse=True)
def no_retry_sleep(monkeypatch):
    monkeypatch.setattr("urllib3.util.retry.time.sleep", lambda seconds: None)
    _Stub.hits.clear()


def _client(registry, status):
    return ComanageApi("{0}/{1}".format(registry, status), "user", "pass", 1, "org")


@pytest.mark.parametrize("status", [429, 500, 503])
def test_cou_create_is_sent_once(registry, status):
    with pytest.raises(requests.exceptions.HTTPError) as caught:
        _client(registry, status).cous_add(name="probe", description="probe")
    assert _Stub.hits == ["POST"]
    assert caught.value.response.status_code == status


@pytest.mark.parametrize("status", [429, 500, 503])
def test_role_create_is_sent_once(registry, status):
    with pytest.raises(requests.exceptions.HTTPError):
        _client(registry, status).coperson_roles_add(
            coperson_id=1, cou_id=2, status="Active", affiliation="member"
        )
    assert _Stub.hits == ["POST"]


def test_reads_still_retry(registry):
    with pytest.raises(requests.exceptions.RetryError):
        _client(registry, 503).cous_view_per_co()
    assert _Stub.hits == ["GET"] * 4
