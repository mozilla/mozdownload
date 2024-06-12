import os

import pytest

from wptserve import (
    handlers,
    request,
    routes as default_routes,
    server,
)


@handlers.handler
def basic_auth_handler(req, response):
    # Allow the test to specify the username and password

    username = b"mozilla"
    password = b"mozilla"

    auth = request.Authentication(req.headers)
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


@pytest.fixture(scope="session")
def httpd():
    HERE = os.path.dirname(os.path.abspath(__file__))

    routes = [
        ("GET", "/basic_auth", basic_auth_handler),
    ]
    routes.extend(default_routes.routes)

    httpd = server.WebTestHttpd(
        host="127.0.0.1",
        port=0,
        doc_root=os.path.join(HERE, 'data'),
        routes=routes,
        )

    httpd.start()
    yield httpd
    httpd.stop()


def pytest_runtest_setup(item):
    ci_enabled = os.getenv('CI', False)
    for marker in item.iter_markers():
        if marker.name == 'ci_only' and not ci_enabled:
            pytest.skip("""
                Can not run this test when not running in CI environment
                """)
