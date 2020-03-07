import base64
import os

import pytest
from six.moves.urllib.parse import parse_qs, urlparse

from wptserve import (
    handlers,
    request,
    routes as default_routes,
    server,
)

class Authentication(request.Authentication):
    """Override the faulty decode_basic method in request.Authentication
       The original method uses base64.decodestring which gives an error if a str
       is passed instead of a bytestring.
       base64.b64decode works on both str and bytestring"""
    def decode_basic(self, data):
        decoded_data = base64.b64decode(data).decode()
        return decoded_data.split(":", 1)

@handlers.handler
def http_auth_handler(req, response):
    # Allow the test to specify the username and password

    url_fragments = urlparse(req.url)
    query_options = parse_qs(url_fragments.query)
    username = query_options.get("username", ["guest"])[0]
    password = query_options.get("password", ["guest"])[0]

    auth = Authentication(req.headers)
    content = """<!doctype html>
        <title>HTTP Authentication</title>
        <p id="status">{}</p>"""

    if auth.username == username and auth.password == password:
        response.status = 200
        response.content = content.format("success")

    else:
        response.status = 401
        response.headers.set("WWW-Authenticate", "Basic realm=\"secret\"")
        response.content = content.format("restricted")


@pytest.fixture
def httpd():
    HERE = os.path.dirname(os.path.abspath(__file__))
    routes = [("GET", "/http_auth", http_auth_handler),
              ]
    routes.extend(default_routes.routes)
    httpd = server.WebTestHttpd(
        host="127.0.0.1",
        port=8080,
        doc_root=os.path.join(HERE, 'data'),
        routes=routes,
        )
    httpd.start(block=False)
    yield httpd
    httpd.stop()


def pytest_runtest_setup(item):
    ci_enabled = os.getenv('CI', False)
    for marker in item.iter_markers():
        if marker.name == 'ci_only' and not ci_enabled:
            pytest.skip("""
                Can not run this test when not running in CI environment
                """)
