import os

import pytest

from wptserve import server

CI_VENDORS = set(["TRAVIS", "APPVEYOR"])


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
    valid_ci_flags = [
        os.getenv(ci, False) for ci in CI_VENDORS]
    run_in_ci_cond = any(valid_ci_flags)
    for marker in item.iter_markers():
        if marker.name == 'ci_vendor' and not run_in_ci_cond:
            pytest.skip("""
                Can not run this test when not running in {vendors}
                """.format(vendors='\n'.join(CI_VENDORS)
                    )
                )