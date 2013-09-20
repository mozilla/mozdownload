# Test Cases

## Correct Choice of Scraper
```
mozdownload -t release -p win32 -v latest
mozdownload -t candidate -p win32 -v 21.0
mozdownload -t daily -p win32
mozdownload -t tinderbox -p win32
```

## Firefox


### Tinderbox
* unable to download tinderbox builds by timestamp #103

```
mozdownload -t tinderbox -p win32 --branch=mozilla-central
mozdownload -a firefox -t tinderbox -p win32
mozdownload -a firefox -t tinderbox -p linux --branch=mozilla-central
mozdownload -a firefox -t tinderbox -p linux64 --branch=mozilla-central
mozdownload -a firefox -t tinderbox -p mac64 --branch=mozilla-central
mozdownload -a firefox -t tinderbox -p win32 --branch=mozilla-central
mozdownload -a firefox -t tinderbox -p win64 --branch=mozilla-central
mozdownload -a firefox -t tinderbox -p linux --branch=mozilla-central --extension=txt
mozdownload -a firefox -t tinderbox -p win32 --branch=mozilla-central --debug-build
mozdownload -a firefox -t tinderbox -p win32 --branch=mozilla-central -d firefox-tinderbox-builds
mozdownload -a firefox -t tinderbox -p win32 --branch=mozilla-central -l el
mozdownload -a firefox -t tinderbox -p win32 --branch=mozilla-central -l pt-PT
mozdownload -a firefox -t tinderbox -p win32 --branch=mozilla-central --date=2013-07-17
mozdownload -a firefox -t tinderbox -p win32 --branch=mozilla-central --date=2013-07-17 --build-number=1
mozdownload -a firefox -t tinderbox -p win32 --branch=mozilla-central --date=1374141721
mozdownload -a firefox -t tinderbox -p win32 --branch=mozilla-inbound
```

## Thunderbird

```


### Tinderbox
* unable to download tinderbox builds by timestamp #103

```
mozdownload -a thunderbird -t tinderbox -p linux --branch=comm-central
mozdownload -a thunderbird -t tinderbox -p linux64 --branch=comm-central
mozdownload -a thunderbird -t tinderbox -p mac64 --branch=comm-central
mozdownload -a thunderbird -t tinderbox -p win32 --branch=comm-central
mozdownload -a thunderbird -t tinderbox -p win64 --branch=comm-central
mozdownload -a thunderbird -t tinderbox -p linux --branch=comm-central --extension=txt
mozdownload -a thunderbird -t tinderbox -p win32 --branch=comm-central --debug-build
mozdownload -a thunderbird -t tinderbox -p win32 --branch=comm-central -d thunderbird-tinderbox-builds
mozdownload -a thunderbird -t tinderbox -p win32 --branch=comm-central -l el
mozdownload -a thunderbird -t tinderbox -p win32 --branch=comm-central -l pt-PT
mozdownload -a thunderbird -t tinderbox -p win32 --branch=comm-central --date=2013-07-24
mozdownload -a thunderbird -t tinderbox -p win32 --branch=comm-central --date=2013-07-24 --build-number=1
mozdownload -a thunderbird -t tinderbox -p win32 --branch=comm-central --date=1374660125
mozdownload -a thunderbird -t tinderbox -p win32 --branch=comm-aurora
```

## B2G

### Releases
Not currently supported

### Candidates
Not currently supported

### Daily
Not currently supported due to #104

<!--
```
mozdownload -a b2g -t daily -p linux --branch=mozilla-central
mozdownload -a b2g -t daily -p linux64 --branch=mozilla-central
mozdownload -a b2g -t daily -p mac64 --branch=mozilla-central
mozdownload -a b2g -t daily -p win32 --branch=mozilla-central
mozdownload -a b2g -t daily -p win32 --branch=mozilla-central -d b2g-daily-builds
mozdownload -a b2g -t daily -p win32 --branch=mozilla-central -l en-US
mozdownload -a b2g -t daily -p win32 --branch=mozilla-central --date=2013-07-02
mozdownload -a b2g -t daily -p win32 --branch=mozilla-central --date=2013-07-02 --build-number=1
mozdownload -a b2g -t daily -p win32 --branch=mozilla-central --build-id=20130702031336
```
-->

### Tinderbox
Not currently supported

## URL
* need test case for password protected URL resource [bug 895835](https://bugzilla.mozilla.org/show_bug.cgi?id=895835)

```
mozdownload --url=https://mozqa.com/index.html
mozdownload --url=https://mozqa.com/index.html -d url-downloads
mozdownload --url=https://mozqa.com/index.html --username=username --password=password
```

## Errors
```
mozdownload -a firefox -t daily -p win32 --branch=invalid
mozdownload -a firefox -t daily -p win32 --branch=invalid --retry-attempts=2
mozdownload -a firefox -t daily -p win32 --branch=invalid --retry-attempts=2 --retry-delay=0
mozdownload -a firefox -t release -p win32 -v invalid
mozdownload -a firefox -t release -p win32 -v invalid --retry-attempts=2
mozdownload -a firefox -t release -p win32 -v invalid --retry-attempts=2 --retry-delay=0
mozdownload -a firefox -t release -p win32 -v latest --timeout=0.1
mozdownload -a firefox -t release -p win32 -v latest --timeout=0.1 --retry-attempts=2
mozdownload -a firefox -t release -p win32 -v latest --timeout=0.1 --retry-attempts=2 --retry-delay=0
```
