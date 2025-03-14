#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import json
import os
import re

import pytest
from urllib.parse import parse_qs, urlparse
from wptserve.handlers import json_handler

from mozdownload.treeherder import Treeherder, PLATFORM_MAP

HERE = os.path.dirname(os.path.abspath(__file__))


@json_handler
def handle_rest_api(request, response):
    """Simple JSON handler for the Treeherder Rest API."""
    url_fragments = urlparse(request.url)
    query_options = parse_qs(url_fragments.query)
    api_endpoint = url_fragments.path.rsplit('/', 2)[1]

    # Use API endpoint to load reference JSON data
    with open(os.path.join(HERE, 'data', '%s.json' % api_endpoint), 'r') as f:
        data = json.loads(f.read())

    def do_filter(entry):
        result = True

        for option, values in query_options.items():
            # Don't handle options which are not properties of the entry
            if option not in entry:
                continue

            for value in values:
                if isinstance(entry[option], int):
                    result &= entry[option] == int(value)
                else:
                    result &= entry[option] == value

        return result

    if api_endpoint == 'jobs':
        data['results'] = list(filter(do_filter, data['results']))

    elif api_endpoint == 'job-log-url':
        data = list(filter(do_filter, data))

    return data
