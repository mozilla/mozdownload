1.8 / 2013-07-25
================
  * Multiple matches are shown when specifying a unique build ID (#102)
  * Filter potential build dirs by whether or not they contain a build (#11)
  * Download the file specified with --url to the correct target folder (#105)
  * Add pause between initial attempt and first retry (#106)
  * Output details of matching builds (#17)
  * Fallback to hostname if downloading from a URL without specifying a path (#89)
  * Removed default timeout for downloads (#91)
  * Fixed issues with --retry-attempts when download fails (#81)
  * Add timeout for network requests (#86)
  * Comply with PEP 8 (#63)
  * Disable caching when fetching build information (#13)
  * Add support for python requests (#83)

1.7.2 / 2013-05-13
==================
  *  Add support for hidden release candidate builds (#77)

1.7.1 / 2013-04-30
==================
  * total_seconds is not an attribute on timedelta in Python 2.6 (#73)

1.7 / 2013-04-24
==================
  * Revert to no retries by default (#65)
  * Add a percentage completion counter (#48)
  * Remove default=None from OptionParser options (#43)
  * Added full command line options to README (#44)
  * Added version number to docstring and --help output (#34)
  * Implement automatic retries for locating the binary (#58)
  * Implemented a download timeout (#50) 

1.6 / 2013-02-20
==================
  * Automatically retry on failure (#39)
  * Improve handling of exceptions when temporary file does not exist (#51)

1.5 / 2012-12-04
==================
  * Don't download stub installer for tinderbox builds (#41)
  * Support basic authentication (#36)
  * Support downloading from an arbitrary URL (#35)

1.4 / 2012-10-08
==================
  * Don't download stub installer by default (#31)
  * Move build-id to option group (#28)

1.3 / 2012-10-04
==================
  * Put --build-id option into Daily Build option group, where it appears to belong (#25)
  * Ignore the build/ and dist/ directories created by setup.py (#24)
  * Add support for downloading b2g builds (#23)

1.2 / 2012-08-16
==================
  * Download of builds via build-id fails if more than one subfolder is present for that day (#19)

1.1 / 2012-07-26
==================
  * Use last, not 1st .txt file in latest- dirs. Fixes issue #14.

1.0 / 2012-05-23
==================
  * Initial version
