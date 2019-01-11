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
