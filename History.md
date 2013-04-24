1.7 / 2013-04-24
==================
  * Revert to no retries by default (#65)
  * Add a percentage completion counter (Fixes #48)
  * Added urllib2.HTTPError to except clause in binary method
  * Remove default=None from OptionParser options (#43)
  * Added full command line options to README. Fixes issue #44
  * Added version number to docstring and --help output. Fixes issue #34
  * Implement automatic retries for locating the binary. Fixes issue #58
  * Implemented a download timeout (fixes issue #50) 

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
