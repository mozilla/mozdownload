# mozdownload

[mozdownload](https://github.com/mozilla/mozdownload)
is a [python package](http://pypi.python.org/pypi/mozdownload)
which handles downloading of Mozilla applications.

## Command Line Usage

The `mozdownload` command will download the application based on the provided
command line options.

### Examples

Download the latest official Firefox release for your platform:

    mozdownload --version=latest

Download the latest Firefox Aurora build for Windows (32bit):

    mozdownload --type=daily --branch=mozilla-aurora --platform=win32

Download the latest official Thunderbird release for your platform: 

    mozdownload --application=thunderbird --version=latest

Download the latest Earlybird build for Linux (64bit): 

    mozdownload --application=thunderbird --type=daily --branch=comm-aurora --platform=linux64

Download this README file: 

    mozdownload --url=https://raw.github.com/mozilla/mozdownload/master/README.md

Download a file from a URL protected with basic authentication: 

    mozdownload --url=http://example.com/secrets.txt --username=admin --password=password

Run `mozdownload --help` for detailed information on the command line options.

### Command Line Options

    Options:
      -h, --help              show this help message and exit
      -a APPLICATION, --application=APPLICATION
                              The name of the application to download, default: "firefox"
      -d DIRECTORY, --directory=DIRECTORY
                              Target directory for the download, default: current working
                              directory
      --build-number=BUILD_NUMBER
                              Number of the build (for candidate, daily, and tinderbox builds)
      -l LOCALE, --locale=LOCALE
                              Locale of the application, default: "en-US"
      -p PLATFORM, --platform=PLATFORM
                              Platform of the application
      -t BUILD_TYPE, --type=BUILD_TYPE
                              Type of build to download, default: "release"
      --url=URL               URL to download.
                              Note: Reserved characters (such as &) must be escaped or put in
                              quotes otherwise CLI output may be abnormal.
      -v VERSION, --version=VERSION
                              Version of the application to be used by release and candidate
                              builds, i.e. "3.6"
      --extension=EXTENSION   File extension of the build (e.g. "zip"), default: the standard build
                              extension on the platform.
      --username=USERNAME     Username for basic HTTP authentication.
      --password=PASSWORD     Password for basic HTTP authentication.
      --retry-attempts=RETRY_ATTEMPTS
                              Number of times the download will be attempted in the event of a
                              failure, default: 3
      --retry-delay=RETRY_DELAY
                              Amount of time (in seconds) to wait between retry attempts,
                              default: 10
      --timeout=TIMEOUT       Amount of time (in seconds) until download times out

      Candidate builds:       Extra options for candidate builds.

      --no-unsigned           Don't allow to download unsigned builds if signed builds are not
                              available

      Daily builds:           Extra options for daily builds.

      --branch=BRANCH         Name of the branch, default: "mozilla-central"
      --build-id=BUILD_ID     ID of the build to download
      --date=DATE             Date of the build, default: latest build

      Tinderbox builds:       Extra options for tinderbox builds.

      --debug-build           Download a debug build


## Running the tests

To run the tests, run `python run_tests.py`.
