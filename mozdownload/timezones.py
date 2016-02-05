# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Module for providing specific timezones."""

from __future__ import absolute_import, unicode_literals

from datetime import datetime, timedelta, tzinfo


class PacificTimezone(tzinfo):
    """Class to set the timezone to PST/PDT, and adjusts for daylight saving."""

    def utcoffset(self, dt):
        """Offset from PST/PDT to UTC."""
        return timedelta(hours=-8) + self.dst(dt)

    def tzname(self, dt):
        """Name of the timezone."""
        return "Pacific"

    def dst(self, dt):
        """Calculate delta for daylight saving."""
        # Daylight saving starts on the second Sunday of March at 2AM standard
        dst_start_date = self.first_sunday(dt.year, 3) + timedelta(days=7) \
                                                       + timedelta(hours=2)
        # Daylight saving ends on the first Sunday of November at 2AM standard
        dst_end_date = self.first_sunday(dt.year, 11) + timedelta(hours=2)

        if dst_start_date <= dt.replace(tzinfo=None) < dst_end_date:
            return timedelta(hours=1)
        else:
            return timedelta(0)

    def first_sunday(self, year, month):
        """Get the first sunday of a month."""
        date = datetime(year, month, 1, 0)
        days_until_sunday = 6 - date.weekday()

        return date + timedelta(days=days_until_sunday)
