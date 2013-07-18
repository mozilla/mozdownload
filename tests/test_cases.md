# Test Cases

## Firefox

### Releases
```
mozdownload -a firefox -t release -p linux -v latest
mozdownload -a firefox -t release -p linux64 -v latest
mozdownload -a firefox -t release -p mac -v latest
mozdownload -a firefox -t release -p win32 -v latest
mozdownload -a firefox -t release -p mac -v latest -d firefox-release-builds
mozdownload -a firefox -t release -p mac -v latest -l de
mozdownload -a firefox -t release -p mac -v 21.0
mozdownload -a firefox -t release -p mac -v 21.0 -l fr
```

### Candidates
```
mozdownload -a firefox -t candidate -p linux -v 21.0
mozdownload -a firefox -t candidate -p linux64 -v 21.0
mozdownload -a firefox -t candidate -p mac -v 21.0
mozdownload -a firefox -t candidate -p win32 -v 21.0
mozdownload -a firefox -t candidate -p mac -v 21.0 -d firefox-candidate-builds
mozdownload -a firefox -t candidate -p mac -v 21.0 -l en-GB
mozdownload -a firefox -t candidate -p mac -v 21.0 --build-number=3
# unable to find unsigned candidate builds
```

### Daily
```
mozdownload -a firefox -t daily -p linux --branch=mozilla-central
mozdownload -a firefox -t daily -p linux64 --branch=mozilla-central
mozdownload -a firefox -t daily -p mac --branch=mozilla-central
mozdownload -a firefox -t daily -p win32 --branch=mozilla-central
mozdownload -a firefox -t daily -p win64 --branch=mozilla-central
mozdownload -a firefox -t daily -p mac --branch=mozilla-central --extension=tests.zip
mozdownload -a firefox -t daily -p mac --branch=mozilla-central -d firefox-daily-builds
mozdownload -a firefox -t daily -p mac --branch=mozilla-central -l sv-SE
mozdownload -a firefox -t daily -p mac --branch=mozilla-central --build-id=20130706031213
mozdownload -a firefox -t daily -p mac --branch=mozilla-central --build-id=20130706031213 --build-number=2
# some folders do not contain builds
mozdownload -a firefox -t daily -p mac --branch=mozilla-central --date=2013-07-02
mozdownload -a firefox -t daily -p mac --branch=mozilla-central --date=2013-07-02 --build-number=1
mozdownload -a firefox -t daily -p mac --branch=mozilla-aurora
```

### Tinderbox
```
mozdownload -a firefox -t tinderbox -p linux --branch=mozilla-central
mozdownload -a firefox -t tinderbox -p linux64 --branch=mozilla-central
mozdownload -a firefox -t tinderbox -p mac64 --branch=mozilla-central
mozdownload -a firefox -t tinderbox -p win32 --branch=mozilla-central
mozdownload -a firefox -t tinderbox -p win64 --branch=mozilla-central
mozdownload -a firefox -t tinderbox -p mac64 --branch=mozilla-central --extension=tests.zip
mozdownload -a firefox -t tinderbox -p mac64 --branch=mozilla-central --debug-build
mozdownload -a firefox -t tinderbox -p mac64 --branch=mozilla-central -d firefox-tinderbox-builds
mozdownload -a firefox -t tinderbox -p mac64 --branch=mozilla-central -l el
mozdownload -a firefox -t tinderbox -p mac64 --branch=mozilla-central --date=2013-07-17
mozdownload -a firefox -t tinderbox -p mac64 --branch=mozilla-central --date=2013-07-17 --build-number=1
# unable to download tinderbox builds by timestamp
mozdownload -a firefox -t tinderbox -p mac64 --branch=mozilla-central --date=1374141721
mozdownload -a firefox -t tinderbox -p mac64 --branch=mozilla-inbound
```

## Thunderbird

### Releases
```
mozdownload -a thunderbird -t release -p linux -v latest
mozdownload -a thunderbird -t release -p linux64 -v latest
mozdownload -a thunderbird -t release -p mac -v latest
mozdownload -a thunderbird -t release -p win32 -v latest
mozdownload -a thunderbird -t release -p mac -v latest -d thunderbird-release-builds
mozdownload -a thunderbird -t release -p mac -v latest -l de
mozdownload -a thunderbird -t release -p mac -v 16.0
mozdownload -a thunderbird -t release -p mac -v 16.0 -l fr
```

### Candidates
```
mozdownload -a thunderbird -t candidate -p linux -v 10.0.5esr
mozdownload -a thunderbird -t candidate -p linux64 -v 10.0.5esr
mozdownload -a thunderbird -t candidate -p mac -v 10.0.5esr
mozdownload -a thunderbird -t candidate -p win32 -v 10.0.5esr
mozdownload -a thunderbird -t candidate -p mac -v 10.0.5esr -d thunderbird-candidate-builds
mozdownload -a thunderbird -t candidate -p mac -v 10.0.5esr -l en-GB
mozdownload -a thunderbird -t candidate -p mac -v 10.0.5esr --build-number=1
# unable to find unsigned candidate builds
```

### Daily
```
mozdownload -a thunderbird -t daily -p linux --branch=comm-central
mozdownload -a thunderbird -t daily -p linux64 --branch=comm-central
mozdownload -a thunderbird -t daily -p mac --branch=comm-central
mozdownload -a thunderbird -t daily -p win32 --branch=comm-central
mozdownload -a thunderbird -t daily -p win64 --branch=comm-central
mozdownload -a thunderbird -t daily -p mac --branch=comm-central --extension=tests.zip
mozdownload -a thunderbird -t daily -p mac --branch=comm-central -d thunderbird-daily-builds
mozdownload -a thunderbird -t daily -p mac --branch=comm-central -l sv-SE
mozdownload -a thunderbird -t daily -p mac --branch=comm-central --build-id=20130710030204
mozdownload -a thunderbird -t daily -p mac --branch=comm-central --build-id=20130710030204 --build-number=1
mozdownload -a thunderbird -t daily -p mac --branch=comm-central --date=2013-07-10
mozdownload -a thunderbird -t daily -p mac --branch=comm-central --date=2013-07-10 --build-number=1
mozdownload -a thunderbird -t daily -p mac --branch=comm-aurora
```

### Tinderbox
```
mozdownload -a thunderbird -t tinderbox -p linux --branch=comm-central
mozdownload -a thunderbird -t tinderbox -p linux64 --branch=comm-central
mozdownload -a thunderbird -t tinderbox -p mac64 --branch=comm-central
mozdownload -a thunderbird -t tinderbox -p win32 --branch=comm-central
# some folders do not contain builds
mozdownload -a thunderbird -t tinderbox -p win64 --branch=comm-central
mozdownload -a thunderbird -t tinderbox -p mac64 --branch=comm-central --extension=tests.zip
mozdownload -a thunderbird -t tinderbox -p mac64 --branch=comm-central --debug-build
mozdownload -a thunderbird -t tinderbox -p mac64 --branch=comm-central -d thunderbird-tinderbox-builds
mozdownload -a thunderbird -t tinderbox -p mac64 --branch=comm-central -l el
mozdownload -a thunderbird -t tinderbox -p mac64 --branch=comm-central --date=2013-07-17
mozdownload -a thunderbird -t tinderbox -p mac64 --branch=comm-central --date=2013-07-17 --build-number=1
# unable to download tinderbox builds by timestamp
mozdownload -a thunderbird -t tinderbox -p mac64 --branch=comm-central --date=1374084645
mozdownload -a thunderbird -t tinderbox -p mac64 --branch=comm-aurora
```

## B2G

### Releases
Not currently supported

### Candidates
Not currently supported

### Daily
Not currently supported

<!--
```
mozdownload -a b2g -t daily -p linux --branch=mozilla-central
mozdownload -a b2g -t daily -p linux64 --branch=mozilla-central
mozdownload -a b2g -t daily -p mac64 --branch=mozilla-central
mozdownload -a b2g -t daily -p win32 --branch=mozilla-central
mozdownload -a b2g -t daily -p mac64 --branch=mozilla-central -d b2g-daily-builds
mozdownload -a b2g -t daily -p mac64 --branch=mozilla-central -l en-US
mozdownload -a b2g -t daily -p mac64 --branch=mozilla-central --date=2013-07-02
mozdownload -a b2g -t daily -p mac64 --branch=mozilla-central --date=2013-07-02 --build-number=1
mozdownload -a b2g -t daily -p mac64 --branch=mozilla-central --build-id=20130702031336
```
-->

### Tinderbox
Not currently supported

## URL
```
mozdownload --url=https://mozqa.com/index.html
# downloaded url resources are not placed in target directory
mozdownload --url=https://mozqa.com/index.html -d url-downloads
# need test case for password protected URL resource
mozdownload --url=https://mozqa.com/index.html --username=username --password=password
```

## Errors
```
# first retry attempt does not pause for the retry delay
mozdownload -a firefox -t release -p mac -v invalid --retry-attempts=2
mozdownload -a firefox -t release -p mac -v invalid --retry-attempts=2 --retry-delay=0
mozdownload -a firefox -t release -p mac -v latest --timeout=0.1
```
