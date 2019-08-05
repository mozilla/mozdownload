import os

import pytest

from wptserve import server


@pytest.fixture
def httpd():
    HERE = os.path.dirname(os.path.abspath(__file__))
    httpd = server.WebTestHttpd(
        host="127.0.0.1",
        port=8080,
        doc_root=os.path.join(HERE, 'data'),
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