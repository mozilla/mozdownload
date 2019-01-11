import os
import pytest

from wptserve import server


@pytest.fixture
def httpd():
    HERE = os.path.dirname(os.path.abspath(__file__))
    httpd = server.WebTestHttpd(port=8080,
                                        doc_root=os.path.join(HERE, 'data'),
                                        host='127.0.0.1')
    return httpd
